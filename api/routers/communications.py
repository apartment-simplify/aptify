"""Tenant communication and messaging timeline services."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/communications", tags=["communications"])


class MessagePayload(BaseModel):
    tenant_id: str = Field(..., description="Recipient tenant identifier")
    channel: str = Field(..., description="sms/email/app")
    subject: Optional[str] = None
    body: str
    intent: str = Field(
        ..., description="Purpose of the message such as reminder or update"
    )
    attachments: List[str] = Field(default_factory=list)


class MessageRecord(BaseModel):
    id: str
    tenant_id: str
    channel: str
    subject: Optional[str]
    body: str
    intent: str
    sentiment: str
    created_at: str
    updated_at: str


def _estimate_sentiment(body: str) -> str:
    lowered = body.lower()
    if any(phrase in lowered for phrase in ["thank", "appreciate", "great"]):
        return "positive"
    if any(phrase in lowered for phrase in ["frustrated", "angry", "unhappy"]):
        return "negative"
    return "neutral"


@router.post("", response_model=MessageRecord)
def send_message(payload: MessagePayload) -> MessageRecord:
    if payload.tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    message_id = generate_id("msg")
    record = with_audit(
        {
            "id": message_id,
            **payload.model_dump(),
            "sentiment": _estimate_sentiment(payload.body),
        }
    )
    STATE.communications.setdefault(payload.tenant_id, []).append(record)
    return MessageRecord(**record)


@router.get("/{tenant_id}", response_model=List[Dict[str, object]])
def timeline(tenant_id: str) -> List[Dict[str, object]]:
    if tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return STATE.communications.get(tenant_id, [])
