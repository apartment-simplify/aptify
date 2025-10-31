"""FastAPI backend implementing key AI email workflows.

The feature set aligns with the AI-Enhanced Property Management PRD and the
Email feature PRD in ``docs/`` by exposing endpoints for:
* Automated email classification and tagging.
* Queue orchestration and suggested next actions.
* Feedback capture loops for continual model optimisation.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(
    title="Aptify Property Management Backend",
    description=(
        "Implements email classification, tagging, routing, and feedback capture "
        "workflows described in the product requirement documents."
    ),
    version="0.1.0",
)

# Enable wide client experimentation (e.g. UI prototypes, partner integrations).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailPayload(BaseModel):
    """Incoming email metadata used for classification."""

    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body text")
    sender: Optional[str] = Field(None, description="Email address of the sender")
    property_id: Optional[str] = Field(
        None, description="Linked property identifier if available"
    )
    tenant_id: Optional[str] = Field(
        None, description="Linked tenant identifier if available"
    )
    attachments: Optional[List[str]] = Field(
        default=None, description="Attachment names for audit history"
    )


class ClassificationResult(BaseModel):
    """Feature Overview: Automated classification with suggested actions (PRD §4.14)."""

    email_id: str = Field(..., description="Identifier assigned by the backend")
    category: str = Field(..., description="Predicted high-level intent category")
    confidence: float = Field(..., ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    priority: str = Field(..., description="Urgency classification for queueing")
    suggested_actions: List[str] = Field(
        default_factory=list,
        description="Recommended follow-up tasks for the agent workspace",
    )


class TagUpdateRequest(BaseModel):
    """Feature Overview: Tagging & label management (Email PRD section 'Tagging')."""

    tags: List[str] = Field(..., description="Full tag list replacing current values")


class QueueRouteRequest(BaseModel):
    """Feature Overview: Queue orchestration and workload balancing."""

    email_id: str = Field(..., description="Email identifier returned by classification")
    priority_override: Optional[str] = Field(
        None, description="Manual override for queue priority"
    )


class QueueRouteResponse(BaseModel):
    queue: str = Field(..., description="Operational queue that should own the email")
    assignee: Optional[str] = Field(
        None, description="Preferred assignee when workload balancing is applicable"
    )
    next_actions: List[str] = Field(
        default_factory=list,
        description="Suggested steps such as drafting responses or creating tasks",
    )


class FeedbackRequest(BaseModel):
    """Feature Overview: Feedback-driven optimisation (PRD §4.15)."""

    item_id: str = Field(..., description="Identifier of the AI output being reviewed")
    item_type: str = Field(..., description="Type of artefact, e.g. 'classification'")
    rating: str = Field(..., description="Thumbs up/down or similar rating label")
    comment: Optional[str] = Field(None, description="Agent free-text feedback")
    correction: Optional[Dict[str, str]] = Field(
        None,
        description="Optional corrected fields to improve future models",
    )


class FeedbackSummary(BaseModel):
    total_items: int
    sentiment_breakdown: Dict[str, int]


EMAIL_STORE: Dict[str, Dict[str, object]] = {}
FEEDBACK_STORE: List[FeedbackRequest] = []


def _derive_category(subject: str, body: str) -> str:
    """Simple heuristic classifier approximating Email PRD intent detection."""

    text = f"{subject} {body}".lower()
    if any(keyword in text for keyword in ["rent", "arrears", "payment"]):
        return "rent"
    if any(keyword in text for keyword in ["leak", "repair", "maintenance", "broken"]):
        return "maintenance"
    if any(keyword in text for keyword in ["lease", "contract", "compliance", "policy"]):
        return "compliance"
    if any(keyword in text for keyword in ["vendor", "quote", "invoice"]):
        return "vendor"
    return "general"


def _derive_priority(body: str) -> str:
    text = body.lower()
    if any(word in text for word in ["urgent", "immediately", "asap", "emergency"]):
        return "high"
    if any(word in text for word in ["soon", "follow up", "reminder"]):
        return "medium"
    return "low"


def _suggest_actions(category: str, priority: str) -> List[str]:
    """Map categories to recommended next steps for the agent workspace."""

    actions = {
        "rent": ["Send payment reminder", "Update ledger"],
        "maintenance": ["Create work order", "Check vendor availability"],
        "compliance": ["Review policy citations", "Escalate to compliance lead"],
        "vendor": ["Attach invoice", "Update vendor performance record"],
        "general": ["Draft acknowledgement", "Schedule follow-up"]
    }
    next_steps = actions.get(category, ["Review details", "Assign owner"])
    if priority == "high" and "Escalate" not in " ".join(next_steps):
        next_steps = ["Escalate to duty manager"] + next_steps
    return next_steps


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    """Basic health endpoint for monitoring and deployment checks."""

    return {"status": "ok"}


@app.post("/emails/classify", response_model=ClassificationResult)
def classify_email(payload: EmailPayload) -> ClassificationResult:
    """Automated classification + tagging stub per Email PRD requirements."""

    category = _derive_category(payload.subject, payload.body)
    priority = _derive_priority(payload.body)
    email_id = str(uuid4())

    tags = [category]
    if priority == "high":
        tags.append("priority:high")
    if payload.property_id:
        tags.append(f"property:{payload.property_id}")
    if payload.tenant_id:
        tags.append(f"tenant:{payload.tenant_id}")

    result = ClassificationResult(
        email_id=email_id,
        category=category,
        confidence=0.72,
        tags=tags,
        priority=priority,
        suggested_actions=_suggest_actions(category, priority),
    )

    EMAIL_STORE[email_id] = {
        "payload": payload.dict(),
        "classification": result.dict(),
    }

    return result


@app.get("/emails/{email_id}")
def get_email(email_id: str) -> Dict[str, object]:
    """Retrieve stored email metadata, supporting audit and review flows."""

    if email_id not in EMAIL_STORE:
        raise HTTPException(status_code=404, detail="Email not found")
    return EMAIL_STORE[email_id]


@app.put("/emails/{email_id}/tags", response_model=ClassificationResult)
def update_tags(email_id: str, request: TagUpdateRequest) -> ClassificationResult:
    """Allow agents to correct or bulk edit tags with audit history support."""

    if email_id not in EMAIL_STORE:
        raise HTTPException(status_code=404, detail="Email not found")

    stored = EMAIL_STORE[email_id]["classification"]
    stored["tags"] = request.tags
    EMAIL_STORE[email_id]["classification"] = stored
    return ClassificationResult(**stored)


@app.post("/emails/route", response_model=QueueRouteResponse)
def route_email(request: QueueRouteRequest) -> QueueRouteResponse:
    """Route email to operational queue with workload hints."""

    if request.email_id not in EMAIL_STORE:
        raise HTTPException(status_code=404, detail="Email not found")

    classification: Dict[str, object] = EMAIL_STORE[request.email_id]["classification"]
    category = str(classification["category"])
    priority = request.priority_override or str(classification["priority"])

    queue_map = {
        "rent": "rent-ops",
        "maintenance": "maintenance-desk",
        "compliance": "compliance-review",
        "vendor": "vendor-management",
        "general": "customer-support",
    }
    queue = queue_map.get(category, "customer-support")
    assignee = None
    if priority == "high":
        assignee = "duty-manager"
    elif queue == "maintenance-desk":
        assignee = "maintenance-agent"

    next_actions = list(classification.get("suggested_actions", []))
    if priority == "high":
        next_actions.insert(0, "Acknowledge within 15 minutes")

    return QueueRouteResponse(queue=queue, assignee=assignee, next_actions=next_actions)


@app.post("/feedback", response_model=FeedbackRequest)
def submit_feedback(feedback: FeedbackRequest) -> FeedbackRequest:
    """Capture agent feedback loops for continual optimisation."""

    FEEDBACK_STORE.append(feedback)
    return feedback


@app.get("/feedback/summary", response_model=FeedbackSummary)
def feedback_summary() -> FeedbackSummary:
    """Provide aggregate metrics mirroring Email PRD reporting needs."""

    ratings = Counter(item.rating for item in FEEDBACK_STORE)
    return FeedbackSummary(total_items=len(FEEDBACK_STORE), sentiment_breakdown=dict(ratings))
