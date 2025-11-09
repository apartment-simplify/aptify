"""Email triage, tagging, and routing services."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..state import STATE
from ..utils import generate_id, timestamp, with_audit


router = APIRouter(prefix="/emails", tags=["email"])


EMAIL_KEYWORDS: Dict[str, List[str]] = {
    "rent": ["rent", "arrear", "payment", "invoice"],
    "maintenance": ["repair", "leak", "maintenance", "broken", "fix"],
    "compliance": ["policy", "compliance", "violation", "notice"],
    "vendor": ["vendor", "quote", "contractor", "bid"],
    "communication": ["update", "follow up", "question"],
}

MOCK_EMAILS: List[Dict[str, object]] = [
    {
        "subject": "Leaking faucet in unit 5B",
        "body": "Hi team, the kitchen faucet in unit 5B has been leaking for two days and is getting worse.",
        "sender": "julia.martinez@example.com",
        "property_id": "prop_park-west",
        "tenant_id": "tenant_martinez",
        "attachments": ["leak-photo.jpg"],
    },
    {
        "subject": "Reminder: April rent payment",
        "body": "Just a reminder that April rent for unit 9C is still outstanding. Can you confirm the balance?",
        "sender": "finance@rentpay.io",
        "property_id": "prop_river-crest",
        "tenant_id": "tenant_chen",
        "attachments": [],
    },
    {
        "subject": "Updated vendor contract attached",
        "body": "Please review the attached HVAC maintenance contract and countersign at your earliest convenience.",
        "sender": "linda@coolclimatehvac.com",
        "property_id": "prop_oak-villas",
        "tenant_id": None,
        "attachments": ["hvac-contract.pdf"],
    },
]


class EmailPayload(BaseModel):
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Full email body text")
    sender: Optional[str] = Field(None, description="Sender email address")
    property_id: Optional[str] = Field(
        None, description="Related property identifier if available"
    )
    tenant_id: Optional[str] = Field(
        None, description="Linked tenant identifier when recognised"
    )
    attachments: List[str] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    email_id: str
    category: str
    confidence: float
    priority: str
    tags: List[str]
    suggested_actions: List[str]
    created_at: str


class TagUpdateRequest(BaseModel):
    tags: List[str]


class QueueRouteRequest(BaseModel):
    email_id: str
    priority_override: Optional[str] = None


class QueueRouteResponse(BaseModel):
    queue: str
    assignee: Optional[str] = None
    next_actions: List[str]


def _detect_category(subject: str, body: str) -> str:
    counts: Dict[str, int] = Counter()
    haystack = f"{subject} {body}".lower()
    for category, keywords in EMAIL_KEYWORDS.items():
        counts[category] = sum(keyword in haystack for keyword in keywords)
    return max(counts, key=counts.get) if counts else "general"


def _priority_from_text(body: str) -> str:
    lowered = body.lower()
    if any(word in lowered for word in ["emergency", "flood", "immediately", "urgent"]):
        return "high"
    if any(word in lowered for word in ["soon", "reminder", "follow up"]):
        return "medium"
    return "low"


def _suggest_actions(category: str, priority: str) -> List[str]:
    base_actions: Dict[str, List[str]] = {
        "rent": ["Review ledger", "Send payment plan"],
        "maintenance": ["Create work order", "Notify on-call vendor"],
        "compliance": ["Check regulations", "Prepare notice"],
        "vendor": ["Attach invoice", "Confirm procurement"],
        "communication": ["Draft response", "Log interaction"],
        "general": ["Review conversation", "Assign owner"],
    }
    actions = base_actions.get(category, base_actions["general"]).copy()
    if priority == "high":
        actions.insert(0, "Escalate to duty manager")
    return actions


def _seed_mock_emails() -> None:
    """Warm the in-memory store with illustrative email records."""
    if STATE.emails:
        return

    for sample in MOCK_EMAILS:
        email_id = generate_id("email")
        category = _detect_category(sample["subject"], sample["body"])
        priority = _priority_from_text(sample["body"])
        record = with_audit(
            {
                "id": email_id,
                "category": category,
                "priority": priority,
                "confidence": 0.9 if category != "general" else 0.7,
                "tags": [category],
                "subject": sample["subject"],
                "body": sample["body"],
                "sender": sample["sender"],
                "property_id": sample["property_id"],
                "tenant_id": sample["tenant_id"],
                "attachments": sample["attachments"],
            }
        )
        STATE.emails[email_id] = record


@router.post("/classify", response_model=ClassificationResult)
def classify_email(payload: EmailPayload) -> ClassificationResult:
    """Classify an email, attach heuristics, and store it for later processing."""
    email_id = generate_id("email")
    category = _detect_category(payload.subject, payload.body)
    priority = _priority_from_text(payload.body)
    confidence = 0.82 if category != "general" else 0.65
    record = with_audit(
        {
            "id": email_id,
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "tags": [category],
            "subject": payload.subject,
            "body": payload.body,
            "sender": payload.sender,
            "property_id": payload.property_id,
            "tenant_id": payload.tenant_id,
            "attachments": payload.attachments,
        }
    )
    STATE.emails[email_id] = record
    return ClassificationResult(
        email_id=email_id,
        category=category,
        confidence=confidence,
        priority=priority,
        tags=record["tags"],
        suggested_actions=_suggest_actions(category, priority),
        created_at=record["created_at"],
    )


@router.get("", response_model=List[Dict[str, object]])
def list_emails() -> List[Dict[str, object]]:
    """Return stored email records for workspace queues."""
    _seed_mock_emails()
    return list(STATE.emails.values())


@router.get("/{email_id}", response_model=Dict[str, object])
def get_email(email_id: str) -> Dict[str, object]:
    if email_id not in STATE.emails:
        raise HTTPException(status_code=404, detail="Email not found")
    return STATE.emails[email_id]


@router.post("/{email_id}/tags", response_model=Dict[str, object])
def update_tags(email_id: str, request: TagUpdateRequest) -> Dict[str, object]:
    """Replace the tag collection for a stored email."""
    if email_id not in STATE.emails:
        raise HTTPException(status_code=404, detail="Email not found")
    record = STATE.emails[email_id].copy()
    record["tags"] = sorted(set(request.tags))
    record["updated_at"] = timestamp()
    STATE.emails[email_id] = record
    return record


@router.post("/route", response_model=QueueRouteResponse)
def route_email(request: QueueRouteRequest) -> QueueRouteResponse:
    if request.email_id not in STATE.emails:
        raise HTTPException(status_code=404, detail="Email not found")
    record = STATE.emails[request.email_id]
    priority = request.priority_override or record["priority"]
    queue_map = {
        "rent": "finance",
        "maintenance": "maintenance",
        "compliance": "compliance",
        "vendor": "vendor_ops",
        "communication": "customer_success",
        "general": "triage",
    }
    queue = queue_map.get(record["category"], "triage")
    assignee = None
    if priority == "high":
        assignee = "duty_manager"
    elif queue == "maintenance":
        assignee = "maintenance_lead"
    return QueueRouteResponse(
        queue=queue,
        assignee=assignee,
        next_actions=_suggest_actions(record["category"], priority),
    )
