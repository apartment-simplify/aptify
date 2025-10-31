"""Shared helpers for the Aptify FastAPI backend."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


def generate_id(prefix: str) -> str:
    """Generate a short identifier with a semantic prefix."""
    return f"{prefix}_{uuid4().hex[:8]}"


def timestamp() -> str:
    """Return an ISO 8601 timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def with_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Attach created/updated timestamps to the payload."""
    now = timestamp()
    return {**payload, "created_at": now, "updated_at": now}
