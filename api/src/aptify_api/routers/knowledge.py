"""Knowledge retrieval and generative assistance endpoints."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import GraphState, generate_id, timestamp
from aptify_api.services.rag import app as rag_app


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
    initial_state: GraphState = {
        "question": payload.question,
        "generation": "",
        "documents": [],
    }
    final_state = rag_app.invoke(initial_state)

    answer = final_state.get("generation", "")
    raw_documents = final_state.get("documents") or []
    if not isinstance(raw_documents, list):
        raw_documents = [raw_documents]

    sources: List[Dict[str, str]] = []
    for idx, document in enumerate(raw_documents, start=1):
        if document is None:
            continue
        page_content = getattr(document, "page_content", "")
        metadata = getattr(document, "metadata", {}) or {}
        source_label = (
            metadata.get("source")
            or metadata.get("title")
            or metadata.get("path")
            or f"document-{idx}"
        )
        snippet = (
            page_content.replace("\n", " ").strip()
            if isinstance(page_content, str)
            else ""
        )
        sources.append(
            {"source": source_label, "snippet": snippet[:1000]},
        )

    return KnowledgeAnswer(answer=answer, sources=sources, generated_at=timestamp())
