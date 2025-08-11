from __future__ import annotations

import logging
from injector import inject, singleton

from private_gpt.components.self_model.self_model_component import (
    SelfModelComponent,
    SelfState,
)

logger = logging.getLogger(__name__)


@singleton
class SelfService:
    """Сервис-обёртка над компонентом SelfModel (бизнес-логика)."""

    @inject
    def __init__(self, self_model: SelfModelComponent) -> None:
        self._self_model = self_model

    def record(self, state: SelfState) -> SelfState:
        return self._self_model.record_state(state)

    def current(self) -> SelfState | None:
        return self._self_model.get_current_state()

    def history(self, limit: int = 50) -> list[SelfState]:
        return self._self_model.history(limit=limit)

    def clear(self) -> None:
        self._self_model.clear()
