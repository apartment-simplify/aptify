"""AI tenant intake orchestration services."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/intake", tags=["tenant intake"])


class IdentityCheck(BaseModel):
    method: str = Field(..., description="Authentication method, e.g. otp")
    result: str = Field(..., description="pass/fail/flagged")
    score: Optional[float] = Field(None, description="Confidence score when available")


class IntakePayload(BaseModel):
    channel: str = Field(..., description="phone or email")
    tenant_name: Optional[str] = None
    tenant_id: Optional[str] = None
    property_id: Optional[str] = None
    summary: str = Field(..., description="Structured issue summary")
    urgency: str = Field(..., description="low/medium/high")
    consent_recorded: bool = Field(..., description="Whether consent was captured")
    identity_checks: List[IdentityCheck] = Field(default_factory=list)
    follow_up: Optional[str] = Field(
        None, description="Preferred follow-up channel or schedule"
    )


class IntakeRecord(BaseModel):
    id: str
    channel: str
    summary: str
    urgency: str
    confidence: float
    status: str
    created_at: str
    updated_at: str


@router.post("", response_model=IntakeRecord)
def capture_intake(payload: IntakePayload) -> IntakeRecord:
    """Capture omnichannel tenant issues with authentication context."""
    intake_id = generate_id("intake")
    confidence = 0.9 if payload.identity_checks else 0.7
    record = with_audit(
        {
            "id": intake_id,
            "channel": payload.channel,
            "tenant_name": payload.tenant_name,
            "tenant_id": payload.tenant_id,
            "property_id": payload.property_id,
            "summary": payload.summary,
            "urgency": payload.urgency,
            "consent_recorded": payload.consent_recorded,
            "identity_checks": [check.model_dump() for check in payload.identity_checks],
            "follow_up": payload.follow_up,
            "confidence": confidence,
            "status": "pending_review",
        }
    )
    STATE.intake_records[intake_id] = record
    return IntakeRecord(**record)


@router.get("", response_model=List[Dict[str, object]])
def list_intake_records() -> List[Dict[str, object]]:
    """List captured intake transcripts for compliance sampling."""
    return list(STATE.intake_records.values())


@router.post("/{intake_id}/approve", response_model=Dict[str, object])
def approve_intake(intake_id: str) -> Dict[str, object]:
    if intake_id not in STATE.intake_records:
        raise HTTPException(status_code=404, detail="Intake record not found")
    record = STATE.intake_records[intake_id].copy()
    record["status"] = "approved"
    record["updated_at"] = timestamp()
    STATE.intake_records[intake_id] = record
    return record
