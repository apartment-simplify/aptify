"""Centralised feedback endpoint for continuous learning loops."""
from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import timestamp


router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackPayload(BaseModel):
    item_id: str = Field(..., description="Referenced artefact identifier")
    item_type: str = Field(..., description="classification|summary|recommendation")
    rating: str = Field(..., description="positive|negative|neutral")
    comment: Optional[str] = None
    correction: Optional[Dict[str, str]] = None


class FeedbackRecord(BaseModel):
    item_id: str
    item_type: str
    rating: str
    comment: Optional[str]
    correction: Optional[Dict[str, str]]
    submitted_at: str


@router.post("", response_model=FeedbackRecord)
def submit_feedback(payload: FeedbackPayload) -> FeedbackRecord:
    record = {
        **payload.model_dump(),
        "submitted_at": timestamp(),
    }
    STATE.email_feedback.append(record)
    return FeedbackRecord(**record)


@router.get("", response_model=Dict[str, object])
def feedback_summary() -> Dict[str, object]:
    breakdown: Dict[str, int] = {}
    for record in STATE.email_feedback:
        rating = record["rating"]
        breakdown[rating] = breakdown.get(rating, 0) + 1
    return {"count": len(STATE.email_feedback), "sentiment": breakdown}
