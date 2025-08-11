from __future__ import annotations

from injector import inject, singleton

from private_gpt.components.reflection.reflection_component import ReflectionComponent, ReflectionRecord


@singleton
class ReflectionService:
    @inject
    def __init__(self, reflection: ReflectionComponent) -> None:
        self._reflection = reflection

    def latest(self) -> ReflectionRecord | None:
        return self._reflection.latest()

    def history(self, limit: int = 50) -> list[ReflectionRecord]:
        return self._reflection.history(limit=limit)

    def clear(self) -> None:
        self._reflection.clear()
