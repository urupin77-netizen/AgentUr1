from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Optional

from injector import inject, singleton
from llama_index.core.llms import ChatMessage, MessageRole

from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.memory.memory_component import MemoryComponent
from private_gpt.components.self_model.self_model_component import SelfModelComponent, SelfState
from private_gpt.settings.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class _Cfg:
    enabled: bool
    interval_minutes: int
    top_k_memories: int
    system_prompt: str


@singleton
class MonologueRunner:
    """Фоновая внутренняя речь: периодически генерирует короткую мысль и записывает её в память и SelfModel."""

    @inject
    def __init__(
        self,
        settings: Settings,
        llm_component: LLMComponent,
        memory: MemoryComponent,
        self_model: SelfModelComponent,
    ) -> None:
        s = settings
        self._cfg = _Cfg(
            enabled=getattr(s, "monologue", None) is not None and s.monologue.enabled,
            interval_minutes=s.monologue.interval_minutes if getattr(s, "monologue", None) else 10,
            top_k_memories=s.monologue.top_k_memories if getattr(s, "monologue", None) else 5,
            system_prompt=(
                s.monologue.system_prompt
                if getattr(s, "monologue", None) and s.monologue.system_prompt
                else "You are the agent's inner voice. Produce STRICT JSON with keys: note (string), new_goals (array of strings), tags (array of strings). Be brief, 1-2 sentences max in 'note'."
            ),
        )
        self._llm = llm_component.llm
        self._memory = memory
        self._self = self_model
        self._task: Optional[asyncio.Task] = None

    # --- lifecycle ---
    def mount_app(self, app) -> None:
        if not self._cfg.enabled:
            logger.info("Internal monologue disabled in settings.")
            return

        @app.on_event("startup")
        async def _start() -> None:  # noqa: D401
            """Start monologue loop."""
            self._task = asyncio.create_task(self._loop())
            logger.info("Internal monologue started with interval=%s min", self._cfg.interval_minutes)

        @app.on_event("shutdown")
        async def _stop() -> None:  # noqa: D401
            """Stop monologue loop."""
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except Exception:  # noqa: BLE001
                    pass
            logger.info("Internal monologue stopped")

    # --- worker ---
    async def _loop(self) -> None:
        while True:
            try:
                await self._tick()
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                logger.error("Monologue tick error: %s", e)
            await asyncio.sleep(max(60, self._cfg.interval_minutes * 60))

    async def _tick(self) -> None:
        # собрать контекст: лучшие воспоминания + текущее состояние Self
        mem = self._memory.list(limit=200)
        best = mem[-self._cfg.top_k_memories:] if mem else []
        current_self = self._self.get_current_state()

        user_payload = self._compose_payload(best, current_self)
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=self._cfg.system_prompt),
            ChatMessage(role=MessageRole.USER, content=user_payload),
        ]
        try:
            resp = self._llm.chat(messages)  # type: ignore
            text = getattr(resp, "message", None).content if hasattr(resp, "message") and resp.message else getattr(resp, "text", str(resp))
        except Exception as e:  # noqa: BLE001
            logger.error("Monologue LLM failed: %s", e)
            return

        data = self._safe_parse(text)
        note = data.get("note", "").strip()
        new_goals = [g for g in data.get("new_goals", []) if isinstance(g, str)]
        tags = [t for t in data.get("tags", []) if isinstance(t, str)]

        if note:
            self._memory.add(text=note, kind="monologue", importance=0.6, tags=tags, embed=True)
            # обновим SelfModel короткой заметкой и целями (если есть)
            merged_goals = []
            if current_self and current_self.goals:
                merged_goals.extend(current_self.goals)
            merged_goals.extend([g for g in new_goals if g not in merged_goals])
            self._self.record_state(
                SelfState(goals=merged_goals, emotions=current_self.emotions if current_self else {}, self_notes=note, tags=list(set((current_self.tags if current_self else []) + tags)))
            )

    # --- utils ---
    @staticmethod
    def _compose_payload(memories, current_self: SelfState | None) -> str:
        payload = {
            "self": current_self.model_dump() if current_self else {},
            "memories": [
                {"id": m.id, "kind": m.kind, "text": m.text, "importance": m.importance, "tags": m.tags}
                for m in memories[-10:]
            ],
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _safe_parse(text: str) -> dict:
        t = text.strip()
        s, e = t.find("{"), t.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(t[s : e + 1])
            except Exception:  # noqa: BLE001
                pass
        return {"note": t[:200], "new_goals": [], "tags": []}
