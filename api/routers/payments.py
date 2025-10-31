"""Rent payment orchestration and reconciliation services."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentSchedule(BaseModel):
    tenant_id: str
    due_date: str
    amount: float
    method: str = Field(..., description="bank_transfer|card|cash")
    autopay: bool = False


class PaymentRecord(BaseModel):
    id: str
    tenant_id: str
    due_date: str
    amount: float
    method: str
    autopay: bool
    status: str
    created_at: str
    updated_at: str


class PaymentUpdate(BaseModel):
    status: str = Field(..., description="scheduled|received|failed|refunded")
    reference: Optional[str] = None


@router.post("/schedule", response_model=PaymentRecord)
def schedule_payment(payload: PaymentSchedule) -> PaymentRecord:
    if payload.tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    payment_id = generate_id("pay")
    record = with_audit(
        {
            "id": payment_id,
            **payload.model_dump(),
            "status": "scheduled",
        }
    )
    STATE.payments[payment_id] = record
    return PaymentRecord(**record)


@router.post("/{payment_id}/status", response_model=PaymentRecord)
def update_payment(payment_id: str, payload: PaymentUpdate) -> PaymentRecord:
    if payment_id not in STATE.payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    record = STATE.payments[payment_id].copy()
    record.update(payload.model_dump(exclude_unset=True))
    record["updated_at"] = timestamp()
    STATE.payments[payment_id] = record
    return PaymentRecord(**record)


@router.get("", response_model=List[Dict[str, object]])
def list_payments() -> List[Dict[str, object]]:
    return list(STATE.payments.values())


@router.get("/summary", response_model=Dict[str, object])
def payment_summary() -> Dict[str, object]:
    totals = {
        "scheduled": 0.0,
        "received": 0.0,
        "failed": 0.0,
        "refunded": 0.0,
    }
    for record in STATE.payments.values():
        totals[record["status"]] += record["amount"]
    return {
        "totals": totals,
        "count": len(STATE.payments),
    }
