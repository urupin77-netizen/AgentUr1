from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from injector import inject, singleton
from pydantic import BaseModel, Field
from llama_index.core.llms import ChatMessage, MessageRole

from private_gpt.paths import local_data_path
from private_gpt.components.llm.llm_component import LLMComponent

logger = logging.getLogger(__name__)

_REFLECTION_DIR = local_data_path / "reflection"
_REFLECTION_FILE = _REFLECTION_DIR / "reflections.jsonl"


class ReflectionRecord(BaseModel):
    """Запись рефлексии ответа чата."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    system_prompt: Optional[str] = None
    last_user_message: str
    chat_history: list[dict[str, str]] = Field(default_factory=list)  # [{"role": "...", "content": "..."}]
    assistant_response: str
    sources: list[dict[str, Any]] | None = None  # [{"file":..., "page":..., "text":...}]
    why: str
    alternatives: list[str] = Field(default_factory=list)
    error_patterns: list[str] = Field(default_factory=list)
    confidence: float = 0.5


@singleton
class ReflectionComponent:
    """Компонент: вызывает локальную LLM и сохраняет разбор ответа."""

    @inject
    def __init__(self, llm_component: LLMComponent) -> None:
        self._llm = llm_component.llm
        _REFLECTION_DIR.mkdir(parents=True, exist_ok=True)
        if not _REFLECTION_FILE.exists():
            _REFLECTION_FILE.touch()
        logger.info("Reflection storage at %s", _REFLECTION_FILE)

    # --------- публичное API ----------
    def reflect(
        self,
        *,
        system_prompt: Optional[str],
        last_user_message: str,
        chat_history: list[Any] | None,
        assistant_response: str,
        sources: list[dict[str, Any]] | None,
    ) -> ReflectionRecord:
        """Сгенерировать и сохранить рефлексию по ответу."""
        messages = self._build_reflection_chat(
            system_prompt=system_prompt,
            last_user_message=last_user_message,
            chat_history=chat_history,
            assistant_response=assistant_response,
            sources=sources,
        )
        try:
            resp = self._llm.chat(messages)  # type: ignore
            text = getattr(resp, "message", None).content if hasattr(resp, "message") and resp.message else getattr(resp, "text", str(resp))
        except Exception as e:
            logger.error("Reflection LLM call failed: %s", e)
            text = '{"why":"internal_error","alternatives":[],"error_patterns":["reflection_llm_failed"],"confidence":0.0}'

        parsed = self._safe_parse_json(text)
        record = ReflectionRecord(
            system_prompt=system_prompt,
            last_user_message=last_user_message,
            chat_history=self._normalize_history(chat_history),
            assistant_response=assistant_response,
            sources=sources,
            why=parsed.get("why", "")[:2000],
            alternatives=[str(a) for a in parsed.get("alternatives", [])][:5],
            error_patterns=[str(e) for e in parsed.get("error_patterns", [])][:10],
            confidence=float(parsed.get("confidence", 0.5)),
        )
        self._append_jsonl(record.model_dump())
        return record

    def latest(self) -> ReflectionRecord | None:
        last = self._read_last()
        return ReflectionRecord(**last) if last else None

    def history(self, limit: int = 50) -> list[ReflectionRecord]:
        items: list[ReflectionRecord] = []
        for rec in self._iter_all():
            items.append(ReflectionRecord(**rec))
        return items[-limit:]

    def clear(self) -> None:
        _REFLECTION_FILE.unlink(missing_ok=True)
        _REFLECTION_FILE.touch()
        logger.warning("Reflection storage cleared")

    # --------- внутренние ----------
    def _build_reflection_chat(
        self,
        *,
        system_prompt: Optional[str],
        last_user_message: str,
        chat_history: list[Any] | None,
        assistant_response: str,
        sources: list[dict[str, Any]] | None,
    ) -> list[ChatMessage]:
        sys = (
            "You are a concise introspection module. "
            "Given a chat turn (user message, assistant answer, optional context sources), "
            "output STRICT JSON with keys: why (string), alternatives (array of 1-3 short strings), "
            "error_patterns (array of short strings), confidence (0..1). "
            "Be brief, actionable, no markdown."
        )
        user = self._compose_user_payload(system_prompt, last_user_message, chat_history, assistant_response, sources)
        return [
            ChatMessage(role=MessageRole.SYSTEM, content=sys),
            ChatMessage(role=MessageRole.USER, content=user),
        ]

    @staticmethod
    def _compose_user_payload(
        system_prompt: Optional[str],
        last_user_message: str,
        chat_history: list[Any] | None,
        assistant_response: str,
        sources: list[dict[str, Any]] | None,
    ) -> str:
        hist = []
        if chat_history:
            for m in chat_history:
                role = getattr(m, "role", None)
                content = getattr(m, "role", None)
                if role is None and isinstance(m, dict):
                    role = m.get("role")
                    content = m.get("content")
                if role and content:
                    hist.append({"role": str(role), "content": str(content)})
        srcs = []
        if sources:
            for s in sources[:4]:
                srcs.append({
                    "file": s.get("file") or s.get("document", {}).get("doc_metadata", {}).get("file_name"),
                    "page": s.get("page") or s.get("document", {}).get("doc_metadata", {}).get("page_label"),
                })
        payload = {
            "system_prompt": system_prompt or "",
            "user": last_user_message,
            "assistant": assistant_response,
            "history": hist[-6:],  # ограничим
            "sources": srcs,
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _safe_parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        # попытка вытащить JSON из текста
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:  # noqa: BLE001
                pass
        # дефолт
        return {"why": text[:512], "alternatives": [], "error_patterns": [], "confidence": 0.5}

    @staticmethod
    def _normalize_history(chat_history: list[Any] | None) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        if not chat_history:
            return out
        for m in chat_history:
            role = getattr(m, "role", None)
            content = getattr(m, "content", None)
            if role is None and isinstance(m, dict):
                role = m.get("role")
                content = m.get("content")
            if role and content:
                out.append({"role": str(role), "content": str(content)})
        return out

    # ---- storage helpers ----
    @staticmethod
    def _append_jsonl(d: dict[str, Any]) -> None:
        with _REFLECTION_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    @staticmethod
    def _read_last() -> dict[str, Any] | None:
        if not _REFLECTION_FILE.exists() or _REFLECTION_FILE.stat().st_size == 0:
            return None
        last = None
        with _REFLECTION_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t:
                    last = json.loads(t)
        return last

    @staticmethod
    def _iter_all() -> Iterable[dict[str, Any]]:
        if not _REFLECTION_FILE.exists() or _REFLECTION_FILE.stat().st_size == 0:
            return []
        with _REFLECTION_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t:
                    yield json.loads(t)
