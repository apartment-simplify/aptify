"""In-memory storage utilities for the FastAPI prototype."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MemoryState:
    """Container object storing all mock domain records."""

    emails: Dict[str, dict] = field(default_factory=dict)
    email_feedback: List[dict] = field(default_factory=list)
    tenants: Dict[str, dict] = field(default_factory=dict)
    intake_records: Dict[str, dict] = field(default_factory=dict)
    communications: Dict[str, List[dict]] = field(default_factory=dict)
    leases: Dict[str, dict] = field(default_factory=dict)
    lease_tasks: Dict[str, List[dict]] = field(default_factory=dict)
    payments: Dict[str, dict] = field(default_factory=dict)
    maintenance_orders: Dict[str, dict] = field(default_factory=dict)
    maintenance_events: Dict[str, List[dict]] = field(default_factory=dict)
    vendors: Dict[str, dict] = field(default_factory=dict)
    vendor_reviews: Dict[str, List[dict]] = field(default_factory=dict)
    owners: Dict[str, dict] = field(default_factory=dict)
    owner_reports: Dict[str, dict] = field(default_factory=dict)
    documents: Dict[str, dict] = field(default_factory=dict)
    document_extractions: Dict[str, dict] = field(default_factory=dict)
    knowledge_articles: Dict[str, dict] = field(default_factory=dict)
    analytics_dashboards: Dict[str, dict] = field(default_factory=dict)
    inspections: Dict[str, dict] = field(default_factory=dict)
    forecasts: Dict[str, dict] = field(default_factory=dict)


STATE = MemoryState()
