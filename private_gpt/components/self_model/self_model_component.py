from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from injector import inject, singleton
from pydantic import BaseModel, Field

from private_gpt.paths import local_data_path
from private_gpt.settings.settings import Settings

logger = logging.getLogger(__name__)

_DATA_DIR = local_data_path / "self_model"
_STATE_FILE = _DATA_DIR / "mental_states.jsonl"


class SelfState(BaseModel):
    """Текущее субъективное состояние Агента.

    Attributes
    ----------
    timestamp : str
        Время фиксации в ISO8601 (UTC).
    goals : list[str]
        Актуальные цели (кратко).
    emotions : dict[str, float]
        Карта эмоций ([-1..1] или [0..1], на твоё усмотрение).
    self_notes : str
        Короткая текстовая сводка состояния/осознанности.
    tags : list[str]
        Произвольные ярлыки.
    """

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    goals: list[str] = Field(default_factory=list)
    emotions: dict[str, float] = Field(default_factory=dict)
    self_notes: str = ""
    tags: list[str] = Field(default_factory=list)


@dataclass
class _SelfModelStorage:
    file_path: Path = _STATE_FILE

    def ensure(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.touch()

    def append(self, record: dict[str, Any]) -> None:
        """Append JSON line to storage."""
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_last(self) -> dict[str, Any] | None:
        """Return last JSON object or None if empty."""
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return None
        last = None
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                last = json.loads(line)
        return last

    def iter_all(self) -> Iterable[dict[str, Any]]:
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


@singleton
class SelfModelComponent:
    """Ядро субъективности: фиксация состояний, целей, эмоций, тегов.

    Хранение: JSONL (`local_data/self_model/mental_states.jsonl`).
    """

    @inject
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._storage = _SelfModelStorage()
        self._storage.ensure()
        logger.info("SelfModel storage at %s", self._storage.file_path)

    def record_state(self, state: SelfState) -> SelfState:
        """Сохранить состояние и вернуть его обратно."""
        self._storage.append(state.model_dump())
        logger.info("SelfModel: state recorded at %s", state.timestamp)
        return state

    def get_current_state(self) -> SelfState | None:
        """Вернуть последнее зафиксированное состояние или None."""
        last = self._storage.read_last()
        return SelfState(**last) if last else None

    def history(self, limit: int = 50) -> list[SelfState]:
        """Вернуть последние N состояний (по умолчанию 50)."""
        items: list[SelfState] = []
        for rec in self._storage.iter_all():
            items.append(SelfState(**rec))
        return items[-limit:]

    def clear(self) -> None:
        """Очистить хранилище (аккуратно!)."""
        self._storage.file_path.unlink(missing_ok=True)
        self._storage.ensure()
        logger.warning("SelfModel: storage cleared")














