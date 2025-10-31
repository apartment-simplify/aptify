"""Tenant lifecycle management endpoints."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantPayload(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    stage: str = Field("prospect", description="Lifecycle stage")
    preferred_channel: str = Field(
        "email", description="Preferred communication channel"
    )


class TenantRecord(BaseModel):
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    stage: str
    preferred_channel: str
    created_at: str
    updated_at: str


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    stage: Optional[str] = None
    preferred_channel: Optional[str] = None


@router.post("", response_model=TenantRecord)
def create_tenant(payload: TenantPayload) -> TenantRecord:
    tenant_id = generate_id("tenant")
    record = with_audit({**payload.model_dump(), "id": tenant_id})
    STATE.tenants[tenant_id] = record
    STATE.communications.setdefault(tenant_id, [])
    return TenantRecord(**record)


@router.get("", response_model=List[TenantRecord])
def list_tenants() -> List[TenantRecord]:
    return [TenantRecord(**tenant) for tenant in STATE.tenants.values()]


@router.get("/{tenant_id}", response_model=TenantRecord)
def get_tenant(tenant_id: str) -> TenantRecord:
    if tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantRecord(**STATE.tenants[tenant_id])


@router.patch("/{tenant_id}", response_model=TenantRecord)
def update_tenant(tenant_id: str, payload: TenantUpdate) -> TenantRecord:
    if tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    record = STATE.tenants[tenant_id].copy()
    for field, value in payload.model_dump(exclude_unset=True).items():
        record[field] = value
    record["updated_at"] = timestamp()
    STATE.tenants[tenant_id] = record
    return TenantRecord(**record)


@router.get("/{tenant_id}/communications", response_model=List[Dict[str, object]])
def tenant_communications(tenant_id: str) -> List[Dict[str, object]]:
    if tenant_id not in STATE.tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return STATE.communications.get(tenant_id, [])
