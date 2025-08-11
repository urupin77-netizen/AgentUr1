from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel

from private_gpt.components.self_model.self_model_component import SelfState
from private_gpt.server.self.self_service import SelfService
from private_gpt.server.utils.auth import authenticated

self_router = APIRouter(prefix="/v1/self", tags=["SelfModel"], dependencies=[Depends(authenticated)])


class RecordBody(BaseModel):
    goals: list[str] = []
    emotions: dict[str, float] = {}
    self_notes: str = ""
    tags: list[str] = []


@self_router.get("/current", response_model=SelfState | None)
def get_current(request: Request) -> SelfState | None:
    service = request.state.injector.get(SelfService)
    return service.current()


@self_router.get("/history", response_model=list[SelfState])
def get_history(request: Request, limit: int = Query(50, ge=1, le=1000)) -> list[SelfState]:
    service = request.state.injector.get(SelfService)
    return service.history(limit=limit)


@self_router.post("/record", response_model=SelfState)
def post_record(request: Request, body: RecordBody) -> SelfState:
    service = request.state.injector.get(SelfService)
    state = SelfState(goals=body.goals, emotions=body.emotions, self_notes=body.self_notes, tags=body.tags)
    return service.record(state)


@self_router.post("/clear")
def post_clear(request: Request) -> dict:
    service = request.state.injector.get(SelfService)
    service.clear()
    return {"status": "ok"}
