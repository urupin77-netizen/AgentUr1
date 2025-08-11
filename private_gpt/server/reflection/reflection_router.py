from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from private_gpt.server.utils.auth import authenticated

from private_gpt.components.reflection.reflection_component import ReflectionRecord
from private_gpt.server.reflection.reflection_service import ReflectionService

reflection_router = APIRouter(prefix="/v1/reflection", tags=["Reflection"], dependencies=[Depends(authenticated)])


@reflection_router.get("/latest", response_model=ReflectionRecord | None)
def get_latest(request: Request) -> ReflectionRecord | None:
    service = request.state.injector.get(ReflectionService)
    return service.latest()


@reflection_router.get("/history", response_model=list[ReflectionRecord])
def get_history(request: Request, limit: int = Query(50, ge=1, le=1000)) -> list[ReflectionRecord]:
    service = request.state.injector.get(ReflectionService)
    return service.history(limit=limit)


@reflection_router.post("/clear")
def post_clear(request: Request) -> dict:
    service = request.state.injector.get(ReflectionService)
    service.clear()
    return {"status": "ok"}
