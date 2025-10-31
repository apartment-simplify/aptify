"""Portfolio analytics, inspections, and forecasting endpoints."""
from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp


router = APIRouter(prefix="/analytics", tags=["analytics"])


class ForecastRequest(BaseModel):
    metric: str = Field(..., description="occupancy|rent|maintenance")
    horizon_months: int = Field(..., ge=1, le=24)
    assumptions: List[str] = Field(default_factory=list)


class ForecastRecord(BaseModel):
    id: str
    metric: str
    horizon_months: int
    projections: List[Dict[str, float]]
    created_at: str


@router.get("/kpis", response_model=Dict[str, float])
def portfolio_kpis() -> Dict[str, float]:
    active_leases = sum(1 for lease in STATE.leases.values() if lease["status"] == "active")
    rent_collected = sum(
        record["amount"]
        for record in STATE.payments.values()
        if record["status"] == "received"
    )
    maintenance_backlog = sum(
        1 for order in STATE.maintenance_orders.values() if order["status"] != "completed"
    )
    return {
        "active_leases": float(active_leases),
        "rent_collected": rent_collected,
        "maintenance_backlog": float(maintenance_backlog),
    }


@router.post("/forecasts", response_model=ForecastRecord)
def create_forecast(payload: ForecastRequest) -> ForecastRecord:
    forecast_id = generate_id("forecast")
    projections = []
    base = 100.0
    for month in range(1, payload.horizon_months + 1):
        projections.append({"month": float(month), "value": base * (1 + 0.02 * month)})
    record = {
        "id": forecast_id,
        **payload.model_dump(),
        "projections": projections,
        "created_at": timestamp(),
    }
    STATE.forecasts[forecast_id] = record
    return ForecastRecord(**record)
