from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field

from private_gpt.server.utils.auth import authenticated
from private_gpt.components.hypothesis.hypothesis_component import HypothesisComponent, Hypothesis
from private_gpt.components.reflection.reflection_component import ReflectionRecord

hypothesis_router = APIRouter(prefix="/v1/hypothesis", tags=["Hypothesis"], dependencies=[Depends(authenticated)])


class GenerateBody(BaseModel):
    last_user_message: str
    assistant_response: str
    reflection: ReflectionRecord | None = None
    top_memory_limit: int = Field(5, ge=0, le=20)
    tags: list[str] = Field(default_factory=list)


class UpdateStatusBody(BaseModel):
    id: str
    status: str  # pending|in_progress|done|discarded


@hypothesis_router.post("/generate", response_model=Hypothesis)
def generate(request: Request, body: GenerateBody) -> Hypothesis:
    h = request.state.injector.get(HypothesisComponent)
    return h.generate(
        last_user_message=body.last_user_message,
        assistant_response=body.assistant_response,
        reflection=body.reflection,
        top_memory_limit=body.top_memory_limit,
        tags=body.tags,
    )


@hypothesis_router.get("/list", response_model=list[Hypothesis])
def list_items(request: Request, limit: int = Query(100, ge=1, le=1000)) -> list[Hypothesis]:
    h = request.state.injector.get(HypothesisComponent)
    return h.list(limit=limit)


@hypothesis_router.post("/update_status", response_model=Hypothesis | None)
def update_status(request: Request, body: UpdateStatusBody) -> Hypothesis | None:
    h = request.state.injector.get(HypothesisComponent)
    return h.update_status(hyp_id=body.id, status=body.status)


@hypothesis_router.post("/clear")
def clear_all(request: Request) -> dict:
    h = request.state.injector.get(HypothesisComponent)
    h.clear()
    return {"status": "ok"}
