"""Knowledge retrieval and generative assistance endpoints."""
from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeArticle(BaseModel):
    title: str
    body: str
    tags: List[str] = Field(default_factory=list)


class KnowledgeRecord(BaseModel):
    id: str
    title: str
    body: str
    tags: List[str]
    created_at: str
    updated_at: str


class KnowledgeQuery(BaseModel):
    question: str
    tags: List[str] = Field(default_factory=list)


class KnowledgeAnswer(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    generated_at: str


@router.post("", response_model=KnowledgeRecord)
def add_article(payload: KnowledgeArticle) -> KnowledgeRecord:
    article_id = generate_id("article")
    record = {
        "id": article_id,
        **payload.model_dump(),
        "created_at": timestamp(),
        "updated_at": timestamp(),
    }
    STATE.knowledge_articles[article_id] = record
    return KnowledgeRecord(**record)


@router.get("", response_model=List[KnowledgeRecord])
def list_articles() -> List[KnowledgeRecord]:
    return [KnowledgeRecord(**record) for record in STATE.knowledge_articles.values()]


@router.post("/query", response_model=KnowledgeAnswer)
def query_knowledge(payload: KnowledgeQuery) -> KnowledgeAnswer:
    matches = []
    for article in STATE.knowledge_articles.values():
        if payload.tags and not set(payload.tags).intersection(article["tags"]):
            continue
        if payload.question.lower() in article["body"].lower():
            matches.append(article)
    if not matches:
        matches = list(STATE.knowledge_articles.values())[:2]
    snippets = [
        {
            "id": entry["id"],
            "title": entry["title"],
            "excerpt": entry["body"][:120],
        }
        for entry in matches
    ]
    answer = "Here is what I found based on the knowledge base."
    return KnowledgeAnswer(answer=answer, sources=snippets, generated_at=timestamp())
