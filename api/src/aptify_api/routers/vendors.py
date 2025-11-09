"""Vendor onboarding, scoring, and performance tracking endpoints."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/vendors", tags=["vendors"])


class VendorPayload(BaseModel):
    name: str
    service_type: str
    coverage_area: List[str] = Field(default_factory=list)
    insurance_expiry: Optional[str] = None


class VendorRecord(BaseModel):
    id: str
    name: str
    service_type: str
    coverage_area: List[str]
    status: str
    rating: float
    created_at: str
    updated_at: str


class VendorReview(BaseModel):
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    work_order_id: Optional[str] = None


@router.post("", response_model=VendorRecord)
def register_vendor(payload: VendorPayload) -> VendorRecord:
    vendor_id = generate_id("vendor")
    record = with_audit(
        {
            "id": vendor_id,
            **payload.model_dump(),
            "status": "active",
            "rating": 4.5,
        }
    )
    STATE.vendors[vendor_id] = record
    STATE.vendor_reviews[vendor_id] = []
    return VendorRecord(**record)


@router.get("", response_model=List[Dict[str, object]])
def list_vendors() -> List[Dict[str, object]]:
    return list(STATE.vendors.values())


@router.post("/{vendor_id}/reviews", response_model=Dict[str, object])
def add_review(vendor_id: str, payload: VendorReview) -> Dict[str, object]:
    if vendor_id not in STATE.vendors:
        raise HTTPException(status_code=404, detail="Vendor not found")
    review = with_audit({"id": generate_id("review"), **payload.model_dump()})
    STATE.vendor_reviews.setdefault(vendor_id, []).append(review)
    ratings = [entry["score"] for entry in STATE.vendor_reviews[vendor_id]]
    record = STATE.vendors[vendor_id].copy()
    record["rating"] = sum(ratings) / len(ratings)
    record["updated_at"] = timestamp()
    STATE.vendors[vendor_id] = record
    return record
