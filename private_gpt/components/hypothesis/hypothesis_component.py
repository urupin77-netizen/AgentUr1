from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from injector import inject, singleton
from pydantic import BaseModel, Field
from llama_index.core.llms import ChatMessage, MessageRole

from private_gpt.paths import local_data_path
from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.memory.memory_component import MemoryComponent
from private_gpt.components.reflection.reflection_component import ReflectionRecord

logger = logging.getLogger(__name__)

_H_DIR = local_data_path / "hypothesis"
_H_FILE = _H_DIR / "hypotheses.jsonl"


class Hypothesis(BaseModel):
    """Гипотеза/цель и минимальный план проверок."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    title: str
    rationale: str
    steps: list[str] = Field(default_factory=list)
    expected_signal: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    priority: int = 3  # 1..5 (1 highest)
    tags: list[str] = Field(default_factory=list)
    status: str = "pending"  # pending|in_progress|done|discarded
    derived_from: dict[str, Any] = Field(default_factory=dict)  # {last_user_message, reflection_id?, memory_refs?}


@dataclass
class _HStorage:
    file_path: Path = _H_FILE

    def ensure(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.touch()

    def append(self, rec: dict[str, Any]) -> None:
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def iter_all(self) -> list[dict[str, Any]]:
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []
        out: list[dict[str, Any]] = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t:
                    out.append(json.loads(t))
        return out

    def rewrite(self, rows: list[dict[str, Any]]) -> None:
        with self.file_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


@singleton
class HypothesisComponent:
    """Генерация гипотез/целей на основе диалога, рефлексии и памяти."""

    @inject
    def __init__(self, llm_component: LLMComponent, memory: MemoryComponent) -> None:
        self._llm = llm_component.llm
        self._memory = memory
        self._store = _HStorage()
        self._store.ensure()
        logger.info("Hypothesis storage at %s", self._store.file_path)

    def generate(
        self,
        *,
        last_user_message: str,
        assistant_response: str,
        reflection: ReflectionRecord | None,
        top_memory_limit: int = 5,
        tags: list[str] | None = None,
    ) -> Hypothesis:
        # соберём контекст из памяти
        memories = self._memory.list(limit=200)[-top_memory_limit:]
        payload = {
            "last_user_message": last_user_message,
            "assistant_response": assistant_response,
            "reflection": reflection.model_dump() if reflection else None,
            "relevant_memories": [
                {"id": m.id, "kind": m.kind, "text": m.text, "importance": m.importance, "tags": m.tags}
                for m in memories
            ],
        }

        system = (
            "You are a goal & hypothesis generator. "
            "Given conversation turn, reflection and few memories, produce STRICT JSON with keys:\n"
            "title (short goal/hypothesis), rationale, steps (array of 1-5 strings), expected_signal (array of 1-3 strings), "
            "risks (array of 0-3 strings), confidence (number 0..1), priority (number 1..5), tags (array of strings).\n"
            "CRITICAL: steps, expected_signal, risks, and tags MUST be arrays of strings, NEVER single values or objects.\n"
            "Examples:\n"
            "- steps: [\"step 1\", \"step 2\", \"step 3\"]\n"
            "- expected_signal: [\"signal 1\", \"signal 2\"]\n"
            "- risks: [\"risk 1\"]\n"
            "- tags: [\"tag1\", \"tag2\"]\n"
            "Be concise, practical, executable locally. No markdown."
        )

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system),
            ChatMessage(role=MessageRole.USER, content=json.dumps(payload, ensure_ascii=False)),
        ]

        try:
            resp = self._llm.chat(messages)  # type: ignore
            text = getattr(resp, "message", None).content if hasattr(resp, "message") and resp.message else getattr(resp, "text", str(resp))
        except Exception as e:  # noqa: BLE001
            logger.error("Hypothesis LLM call failed: %s", e)
            text = '{"title":"Fallback hypothesis","rationale":"llm_error","steps":[],"expected_signal":[],"risks":["llm_failed"],"confidence":0.0,"priority":5,"tags":["error"]}'

        data = self._safe_parse(text)
        
        # Безопасная обработка всех полей
        def safe_string_list(value, max_items=5):
            """Безопасно извлекает список строк из различных форматов."""
            if isinstance(value, list):
                result = []
                for item in value:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict):
                        # Если это объект, попробуем извлечь значение
                        for v in item.values():
                            if isinstance(v, str):
                                result.append(v)
                                break
                    else:
                        result.append(str(item))
                return result[:max_items]
            elif isinstance(value, str):
                return [value]
            elif isinstance(value, (int, float)):
                return [str(value)]
            else:
                return []
        
        steps = safe_string_list(data.get("steps", []), 5)
        expected_signal = safe_string_list(data.get("expected_signal", []), 3)
        risks = safe_string_list(data.get("risks", []), 3)
        
        # Безопасная обработка priority
        priority_raw = data.get("priority", 3)
        if isinstance(priority_raw, str):
            # Попробуем извлечь число из строки
            import re
            num_match = re.search(r'\d+', priority_raw)
            priority = int(num_match.group()) if num_match else 3
        else:
            priority = int(priority_raw) if isinstance(priority_raw, (int, float)) else 3
            
        hyp = Hypothesis(
            title=str(data.get("title", "Untitled"))[:200],
            rationale=str(data.get("rationale", ""))[:2000],
            steps=steps,
            expected_signal=expected_signal,
            risks=risks,
            confidence=float(data.get("confidence", 0.5)),
            priority=priority,
            tags=list(set([*(tags or []), *safe_string_list(data.get("tags", []), 10)])),
            derived_from={
                "last_user_message": last_user_message,
                "reflection_confidence": reflection.confidence if reflection else None,
            },
        )
        self._store.append(hyp.model_dump())
        return hyp

    def list(self, limit: int = 100) -> list[Hypothesis]:
        rows = self._store.iter_all()
        items = [Hypothesis(**r) for r in rows]
        return items[-limit:]

    def update_status(self, hyp_id: str, status: str) -> Hypothesis | None:
        rows = self._store.iter_all()
        out = []
        updated: Hypothesis | None = None
        for r in rows:
            if r.get("id") == hyp_id:
                r["status"] = status
                updated = Hypothesis(**r)
            out.append(r)
        if updated:
            self._store.rewrite(out)
        return updated

    def clear(self) -> None:
        self._store.rewrite([])

    @staticmethod
    def _safe_parse(text: str) -> dict[str, Any]:
        t = text.strip()
        s, e = t.find("{"), t.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(t[s : e + 1])
            except Exception:  # noqa: BLE001
                pass
        return {"title": t[:120], "rationale": "", "steps": [], "expected_signal": [], "risks": [], "confidence": 0.5, "priority": 3, "tags": []}
