"""Lease contract drafting, review, and onboarding workflows."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/leases", tags=["leasing"])


class LeasePayload(BaseModel):
    tenant_id: str
    property_id: str
    start_date: str
    end_date: str
    rent_amount: float
    terms: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)


class LeaseRecord(BaseModel):
    id: str
    tenant_id: str
    property_id: str
    start_date: str
    end_date: str
    rent_amount: float
    status: str
    created_at: str
    updated_at: str


class LeaseStatusUpdate(BaseModel):
    status: str = Field(..., description="draft|sent|signed|active|terminated")


class LeaseTask(BaseModel):
    title: str
    due_date: Optional[str] = None
    assignee: Optional[str] = None
    checklist: List[str] = Field(default_factory=list)


@router.post("", response_model=LeaseRecord)
def create_lease(payload: LeasePayload) -> LeaseRecord:
    if payload.tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    lease_id = generate_id("lease")
    record = with_audit(
        {
            "id": lease_id,
            **payload.model_dump(),
            "status": "draft",
        }
    )
    STATE.leases[lease_id] = record
    STATE.lease_tasks[lease_id] = []
    return LeaseRecord(**record)


@router.get("", response_model=List[Dict[str, object]])
def list_leases() -> List[Dict[str, object]]:
    return list(STATE.leases.values())


@router.post("/{lease_id}/status", response_model=LeaseRecord)
def update_status(lease_id: str, payload: LeaseStatusUpdate) -> LeaseRecord:
    if lease_id not in STATE.leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    record = STATE.leases[lease_id].copy()
    record["status"] = payload.status
    record["updated_at"] = timestamp()
    STATE.leases[lease_id] = record
    return LeaseRecord(**record)


@router.post("/{lease_id}/tasks", response_model=List[Dict[str, object]])
def add_task(lease_id: str, payload: LeaseTask) -> List[Dict[str, object]]:
    if lease_id not in STATE.leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    task = with_audit({"id": generate_id("task"), **payload.model_dump()})
    STATE.lease_tasks.setdefault(lease_id, []).append(task)
    return STATE.lease_tasks[lease_id]


@router.get("/{lease_id}/tasks", response_model=List[Dict[str, object]])
def list_tasks(lease_id: str) -> List[Dict[str, object]]:
    if lease_id not in STATE.leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    return STATE.lease_tasks.get(lease_id, [])
