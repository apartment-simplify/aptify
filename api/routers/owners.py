"""Owner reporting and collaboration endpoints."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/owners", tags=["owners"])


class OwnerPayload(BaseModel):
    name: str
    email: str
    portfolio: List[str] = Field(default_factory=list)


class OwnerRecord(BaseModel):
    id: str
    name: str
    email: str
    portfolio: List[str]
    created_at: str
    updated_at: str


class OwnerReportPayload(BaseModel):
    owner_id: str
    period: str
    highlights: List[str] = Field(default_factory=list)
    income: float
    expenses: float
    recommendations: List[str] = Field(default_factory=list)


@router.post("", response_model=OwnerRecord)
def create_owner(payload: OwnerPayload) -> OwnerRecord:
    owner_id = generate_id("owner")
    record = with_audit({"id": owner_id, **payload.model_dump()})
    STATE.owners[owner_id] = record
    return OwnerRecord(**record)


@router.get("", response_model=List[OwnerRecord])
def list_owners() -> List[OwnerRecord]:
    return [OwnerRecord(**record) for record in STATE.owners.values()]


@router.post("/reports", response_model=Dict[str, object])
def generate_report(payload: OwnerReportPayload) -> Dict[str, object]:
    if payload.owner_id not in STATE.owners:
        raise HTTPException(status_code=404, detail="Owner not found")
    report_id = generate_id("report")
    net_income = payload.income - payload.expenses
    report = with_audit(
        {
            "id": report_id,
            **payload.model_dump(),
            "net_income": net_income,
            "status": "delivered",
        }
    )
    STATE.owner_reports[report_id] = report
    return report


@router.get("/reports", response_model=List[Dict[str, object]])
def list_reports() -> List[Dict[str, object]]:
    return list(STATE.owner_reports.values())
