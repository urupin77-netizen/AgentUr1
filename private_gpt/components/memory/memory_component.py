from __future__ import annotations

import json
import logging
import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from injector import inject, singleton
from pydantic import BaseModel, Field

from private_gpt.paths import local_data_path
from private_gpt.components.embedding.embedding_component import EmbeddingComponent

logger = logging.getLogger(__name__)

_MEM_DIR = local_data_path / "memory"
_MEM_FILE = _MEM_DIR / "memory.jsonl"


class MemoryItem(BaseModel):
    """Элемент памяти агента.

    Attributes
    ----------
    id : str
        Уникальный идентификатор.
    timestamp : str
        Время создания (UTC, ISO8601).
    kind : str
        Тип записи (e.g., "observation", "insight", "todo", "monologue").
    text : str
        Содержимое.
    importance : float
        Важность [0..1].
    embedding : list[float] | None
        Векторное представление текста.
    tags : list[str]
        Ярлыки.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    kind: str = "observation"
    text: str
    importance: float = 0.5
    embedding: list[float] | None = None
    tags: list[str] = Field(default_factory=list)


@dataclass
class _MemStorage:
    file_path: Path = _MEM_FILE

    def ensure(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.touch()

    def append(self, rec: dict[str, Any]) -> None:
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def iter_all(self) -> Iterable[dict[str, Any]]:
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t:
                    yield json.loads(t)

    def clear(self) -> None:
        self.file_path.unlink(missing_ok=True)
        self.ensure()


@singleton
class MemoryComponent:
    """Память с поддержкой забывания (decay) и поиска по эмбеддингам."""

    @inject
    def __init__(self, embedding_component: EmbeddingComponent) -> None:
        self._emb = embedding_component.embedding_model
        self._store = _MemStorage()
        self._store.ensure()
        logger.info("Memory storage at %s", self._store.file_path)

    # ---------- API ----------
    def add(
        self,
        *,
        text: str,
        kind: str = "observation",
        importance: float = 0.5,
        tags: list[str] | None = None,
        embed: bool = True,
    ) -> MemoryItem:
        emb: Optional[list[float]] = None
        if embed:
            try:
                emb = self._emb.get_text_embedding(text)  # type: ignore
            except Exception as e: # noqa: BLE001
                logger.error("Embedding failed: %s", e)
                emb = None

        item = MemoryItem(text=text, kind=kind, importance=float(importance), tags=tags or [], embedding=emb)
        self._store.append(item.model_dump())
        return item

    def list(self, limit: int = 100) -> list[MemoryItem]:
        items: list[MemoryItem] = [MemoryItem(**r) for r in self._store.iter_all()]
        return items[-limit:]

    def clear(self) -> None:
        self._store.clear()

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        decay_half_life_days: float = 30.0,
    ) -> list[tuple[MemoryItem, float]]:
        """Поиск по косинусной близости с учётом затухания (importance * decay)."""
        try:
            q_emb = self._emb.get_text_embedding(query)  # type: ignore
        except Exception as e: # noqa: BLE001
            logger.error("Query embedding failed: %s", e)
            return []

        now = datetime.now(timezone.utc)
        results: list[tuple[MemoryItem, float]] = []
        for rec in self._store.iter_all():
            it = MemoryItem(**rec)
            sim = cosine(q_emb, it.embedding) if it.embedding else 0.0
            age_days = max(
                0.0,
                (now - datetime.fromisoformat(it.timestamp)).total_seconds() / 86400.0,
            )
            decay = 0.5 ** (age_days / max(decay_half_life_days, 0.1))
            score = sim * (0.2 + 0.8 * it.importance) * decay  # легкий вес важности
            results.append((it, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


# ---------- helpers ----------
def cosine(a: list[float] | None, b: list[float] | None) -> float:
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        n = min(len(a), len(b))
        a = a[:n]
        b = b[:n]
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
