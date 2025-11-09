"""Maintenance triage, work order drafting, and scheduling."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/maintenance", tags=["maintenance"])


class WorkOrderPayload(BaseModel):
    tenant_id: str
    property_id: str
    description: str
    priority: str = Field(..., description="low|medium|high|emergency")
    target_date: Optional[str] = None
    vendor_id: Optional[str] = None
    access_notes: Optional[str] = None


class WorkOrderRecord(BaseModel):
    id: str
    tenant_id: str
    property_id: str
    description: str
    priority: str
    status: str
    created_at: str
    updated_at: str


class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    vendor_id: Optional[str] = None
    scheduled_at: Optional[str] = None
    completion_notes: Optional[str] = None


@router.post("/work-orders", response_model=WorkOrderRecord)
def create_work_order(payload: WorkOrderPayload) -> WorkOrderRecord:
    if payload.tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    work_order_id = generate_id("wo")
    record = with_audit(
        {
            "id": work_order_id,
            **payload.model_dump(),
            "status": "draft",
        }
    )
    STATE.maintenance_orders[work_order_id] = record
    STATE.maintenance_events[work_order_id] = []
    return WorkOrderRecord(**record)


@router.post("/work-orders/{work_order_id}", response_model=WorkOrderRecord)
def update_work_order(work_order_id: str, payload: WorkOrderUpdate) -> WorkOrderRecord:
    if work_order_id not in STATE.maintenance_orders:
        raise HTTPException(status_code=404, detail="Work order not found")
    record = STATE.maintenance_orders[work_order_id].copy()
    for field, value in payload.model_dump(exclude_unset=True).items():
        record[field] = value
    record["updated_at"] = timestamp()
    STATE.maintenance_orders[work_order_id] = record
    if payload.status:
        event = with_audit(
            {"type": "status_change", "status": payload.status, "id": generate_id("evt")}
        )
        STATE.maintenance_events.setdefault(work_order_id, []).append(event)
    return WorkOrderRecord(**record)


@router.get("/work-orders", response_model=List[Dict[str, object]])
def list_work_orders() -> List[Dict[str, object]]:
    return list(STATE.maintenance_orders.values())


@router.get("/dashboard", response_model=Dict[str, object])
def maintenance_dashboard() -> Dict[str, object]:
    summary: Dict[str, int] = {"draft": 0, "scheduled": 0, "in_progress": 0, "completed": 0}
    for order in STATE.maintenance_orders.values():
        status = order["status"]
        summary[status] = summary.get(status, 0) + 1
    return {
        "summary": summary,
        "total": len(STATE.maintenance_orders),
    }
