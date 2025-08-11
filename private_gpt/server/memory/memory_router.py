from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from private_gpt.server.utils.auth import authenticated
from private_gpt.components.memory.memory_component import MemoryComponent, MemoryItem

memory_router = APIRouter(prefix="/v1/memory", tags=["Memory"], dependencies=[Depends(authenticated)])


class AddBody(BaseModel):
    text: str
    kind: str = "observation"
    importance: float = Field(0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    embed: bool = True


class SearchBody(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=50)
    decay_half_life_days: float = Field(30.0, ge=0.1, le=3650.0)


@memory_router.post("/add", response_model=MemoryItem)
def add_item(request: Request, body: AddBody) -> MemoryItem:
    m = request.state.injector.get(MemoryComponent)
    return m.add(text=body.text, kind=body.kind, importance=body.importance, tags=body.tags, embed=body.embed)


@memory_router.get("/list", response_model=list[MemoryItem])
def list_items(request: Request, limit: int = Query(100, ge=1, le=1000)) -> list[MemoryItem]:
    m = request.state.injector.get(MemoryComponent)
    return m.list(limit=limit)


@memory_router.post("/search")
def search_items(request: Request, body: SearchBody) -> list[dict]:
    m = request.state.injector.get(MemoryComponent)
    res = m.search(query=body.query, top_k=body.top_k, decay_half_life_days=body.decay_half_life_days)
    return [{"item": it.model_dump(), "score": round(score, 4)} for it, score in res]


@memory_router.post("/clear")
def clear_memory(request: Request) -> dict:
    m = request.state.injector.get(MemoryComponent)
    m.clear()
    return {"status": "ok"}
