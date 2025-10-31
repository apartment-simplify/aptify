"""Document vault management and AI extraction services."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentPayload(BaseModel):
    title: str
    category: str
    related_entities: List[str] = Field(default_factory=list)
    content: str = Field(..., description="Raw text or summary of the document")


class DocumentRecord(BaseModel):
    id: str
    title: str
    category: str
    related_entities: List[str]
    created_at: str
    updated_at: str


class ExtractionRequest(BaseModel):
    schema: Dict[str, str] = Field(
        ..., description="Mapping of field names to extraction instructions"
    )


class ExtractionResult(BaseModel):
    document_id: str
    fields: Dict[str, str]
    created_at: str


@router.post("", response_model=DocumentRecord)
def upload_document(payload: DocumentPayload) -> DocumentRecord:
    document_id = generate_id("doc")
    record = with_audit({"id": document_id, **payload.model_dump()})
    STATE.documents[document_id] = record
    return DocumentRecord(**record)


@router.get("", response_model=List[Dict[str, object]])
def list_documents() -> List[Dict[str, object]]:
    return list(STATE.documents.values())


@router.post("/{document_id}/extract", response_model=ExtractionResult)
def extract_fields(document_id: str, payload: ExtractionRequest) -> ExtractionResult:
    if document_id not in STATE.documents:
        raise HTTPException(status_code=404, detail="Document not found")
    fields = {
        key: f"Extracted {instruction}"
        for key, instruction in payload.schema.items()
    }
    extraction_id = generate_id("extract")
    result = {
        "id": extraction_id,
        "document_id": document_id,
        "fields": fields,
        "created_at": timestamp(),
    }
    STATE.document_extractions[extraction_id] = result
    return ExtractionResult(**result)


@router.get("/extractions", response_model=List[Dict[str, object]])
def list_extractions() -> List[Dict[str, object]]:
    return list(STATE.document_extractions.values())
