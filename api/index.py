"""FastAPI backend implementing Aptify PRD-driven workflows.

The backend provides in-memory prototypes covering every feature family in
``docs/features`` including tenant intake, lifecycle management, leasing,
payments, maintenance, communications, analytics, knowledge, and AI feedback
loops.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(
    title="Aptify Property Management Backend",
    description=(
        "Prototype backend implementing all feature families defined across the "
        "Aptify PRDs. Each endpoint mirrors the AI-assisted workflows "
        "documented in docs/features by providing mock orchestration, "
        "summaries, and decision support."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Email management (Email_PRD)
# ---------------------------------------------------------------------------


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
    """Automated classification with suggested actions (Email PRD)."""

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
    """Tagging & label management (Email PRD)."""

    tags: List[str] = Field(..., description="Full tag list replacing current values")


class QueueRouteRequest(BaseModel):
    """Queue orchestration and workload balancing."""

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
    """Feedback-driven optimisation loop."""

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
    actions = {
        "rent": ["Send payment reminder", "Update ledger"],
        "maintenance": ["Create work order", "Check vendor availability"],
        "compliance": ["Review policy citations", "Escalate to compliance lead"],
        "vendor": ["Attach invoice", "Update vendor performance record"],
        "general": ["Draft acknowledgement", "Schedule follow-up"],
    }
    next_steps = actions.get(category, ["Review details", "Assign owner"])
    if priority == "high" and "Escalate" not in " ".join(next_steps):
        next_steps = ["Escalate to duty manager"] + next_steps
    return next_steps


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/emails/classify", response_model=ClassificationResult)
def classify_email(payload: EmailPayload) -> ClassificationResult:
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
    if email_id not in EMAIL_STORE:
        raise HTTPException(status_code=404, detail="Email not found")
    return EMAIL_STORE[email_id]


@app.put("/emails/{email_id}/tags", response_model=ClassificationResult)
def update_tags(email_id: str, request: TagUpdateRequest) -> ClassificationResult:
    if email_id not in EMAIL_STORE:
        raise HTTPException(status_code=404, detail="Email not found")

    stored = EMAIL_STORE[email_id]["classification"]
    stored["tags"] = request.tags
    EMAIL_STORE[email_id]["classification"] = stored
    return ClassificationResult(**stored)


@app.post("/emails/route", response_model=QueueRouteResponse)
def route_email(request: QueueRouteRequest) -> QueueRouteResponse:
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
    FEEDBACK_STORE.append(feedback)
    return feedback


@app.get("/feedback/summary", response_model=FeedbackSummary)
def feedback_summary() -> FeedbackSummary:
    ratings = Counter(item.rating for item in FEEDBACK_STORE)
    return FeedbackSummary(total_items=len(FEEDBACK_STORE), sentiment_breakdown=dict(ratings))


# ---------------------------------------------------------------------------
# AI Tenant Intake (AI_Tenant_Intake_PRD)
# ---------------------------------------------------------------------------


class TenantApplicationCreate(BaseModel):
    applicant_name: str
    property_id: str
    income: float
    credit_score: Optional[int] = None
    household_size: int = 1
    references: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class TenantApplication(BaseModel):
    application_id: str
    status: str
    submitted_at: datetime
    ai_risk_score: float
    recommended_actions: List[str]
    missing_documents: List[str]
    decision: Optional[str]
    timeline: List[str]
    payload: TenantApplicationCreate


APPLICATION_STORE: Dict[str, TenantApplication] = {}
REQUIRED_DOCUMENTS = {"id_verification", "proof_of_income", "rental_history"}


def _score_application(data: TenantApplicationCreate) -> float:
    score = 0.5
    if data.credit_score:
        if data.credit_score > 750:
            score += 0.3
        elif data.credit_score < 600:
            score -= 0.2
    if data.income >= 3_000:
        score += 0.1
    if data.household_size > 4:
        score -= 0.05
    if data.references:
        score += 0.05
    return max(0.0, min(score, 1.0))


def _missing_docs(data: TenantApplicationCreate) -> List[str]:
    provided = {ref.split(":")[0] for ref in data.references}
    return sorted(REQUIRED_DOCUMENTS - provided)


@app.post("/intake/applications", response_model=TenantApplication)
def create_application(payload: TenantApplicationCreate) -> TenantApplication:
    application_id = str(uuid4())
    risk = _score_application(payload)
    missing = _missing_docs(payload)
    recommendations = ["Request additional documents"] if missing else ["Schedule interview"]
    if risk < 0.4:
        recommendations.append("Flag for manual underwriting")
    timeline = [f"{datetime.utcnow().isoformat()} - Application submitted"]
    record = TenantApplication(
        application_id=application_id,
        status="submitted",
        submitted_at=datetime.utcnow(),
        ai_risk_score=risk,
        recommended_actions=recommendations,
        missing_documents=missing,
        decision=None,
        timeline=timeline,
        payload=payload,
    )
    APPLICATION_STORE[application_id] = record
    return record


@app.get("/intake/applications/{application_id}", response_model=TenantApplication)
def get_application(application_id: str) -> TenantApplication:
    if application_id not in APPLICATION_STORE:
        raise HTTPException(status_code=404, detail="Application not found")
    return APPLICATION_STORE[application_id]


class ScreeningUpdate(BaseModel):
    reviewer: str
    comments: Optional[str] = None


@app.post("/intake/applications/{application_id}/screen", response_model=TenantApplication)
def screen_application(application_id: str, update: ScreeningUpdate) -> TenantApplication:
    if application_id not in APPLICATION_STORE:
        raise HTTPException(status_code=404, detail="Application not found")

    record = APPLICATION_STORE[application_id]
    record.status = "screening"
    record.timeline.append(
        f"{datetime.utcnow().isoformat()} - Screening started by {update.reviewer}"
    )
    if update.comments:
        record.timeline.append(update.comments)
    if record.ai_risk_score < 0.35:
        record.recommended_actions.insert(0, "Escalate to senior manager")
    APPLICATION_STORE[application_id] = record
    return record


class DecisionRequest(BaseModel):
    reviewer: str
    decision: str
    rationale: Optional[str] = None


@app.post("/intake/applications/{application_id}/decision", response_model=TenantApplication)
def decide_application(application_id: str, request: DecisionRequest) -> TenantApplication:
    if application_id not in APPLICATION_STORE:
        raise HTTPException(status_code=404, detail="Application not found")

    record = APPLICATION_STORE[application_id]
    record.status = "completed"
    record.decision = request.decision
    record.timeline.append(
        f"{datetime.utcnow().isoformat()} - Decision {request.decision} by {request.reviewer}"
    )
    if request.rationale:
        record.timeline.append(f"Rationale: {request.rationale}")
    APPLICATION_STORE[application_id] = record
    return record


# ---------------------------------------------------------------------------
# Tenant Management & Communications (Tenant_Management_PRD, Tenant_Communication_PRD)
# ---------------------------------------------------------------------------


class TenantProfileCreate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    property_id: Optional[str] = None
    move_in_date: Optional[date] = None
    arrears_balance: float = 0.0
    sentiment_score: float = 0.5


class TenantProfile(BaseModel):
    tenant_id: str
    created_at: datetime
    profile: TenantProfileCreate
    lifecycle_status: str
    outstanding_tasks: List[str]
    risk_flags: List[str]


class CommunicationEntryCreate(BaseModel):
    channel: str
    subject: str
    summary: str
    sentiment: Optional[str] = None
    follow_up_required: bool = False


class CommunicationEntry(BaseModel):
    communication_id: str
    recorded_at: datetime
    author: str
    entry: CommunicationEntryCreate


class OnboardingTask(BaseModel):
    task_id: str
    title: str
    due_date: date
    owner: str
    status: str


class IncidentReport(BaseModel):
    incident_id: str
    created_at: datetime
    category: str
    severity: str
    description: str
    routed_queue: str
    next_actions: List[str]


TENANT_STORE: Dict[str, TenantProfile] = {}
COMMUNICATION_LOGS: Dict[str, List[CommunicationEntry]] = defaultdict(list)
ONBOARDING_TASKS: Dict[str, List[OnboardingTask]] = defaultdict(list)
INCIDENT_STORE: Dict[str, List[IncidentReport]] = defaultdict(list)


def _baseline_tasks(profile: TenantProfileCreate) -> List[OnboardingTask]:
    base = [
        ("Collect identification", 2, "onboarding-team"),
        ("Verify employment", 4, "screening-team"),
        ("Schedule welcome call", 7, "property-manager"),
    ]
    if profile.arrears_balance > 0:
        base.append(("Arrange arrears payment plan", 1, "finance-team"))
    tasks: List[OnboardingTask] = []
    for title, offset, owner in base:
        tasks.append(
            OnboardingTask(
                task_id=str(uuid4()),
                title=title,
                due_date=date.today() + timedelta(days=offset),
                owner=owner,
                status="pending",
            )
        )
    return tasks


def _derive_risk(profile: TenantProfileCreate) -> List[str]:
    risk = []
    if profile.arrears_balance > 500:
        risk.append("arrears-high")
    if profile.sentiment_score < 0.3:
        risk.append("negative-sentiment")
    if profile.move_in_date and profile.move_in_date > date.today():
        risk.append("upcoming-move-in")
    return risk


@app.post("/tenants", response_model=TenantProfile)
def create_tenant(profile: TenantProfileCreate) -> TenantProfile:
    tenant_id = str(uuid4())
    record = TenantProfile(
        tenant_id=tenant_id,
        created_at=datetime.utcnow(),
        profile=profile,
        lifecycle_status="active" if profile.move_in_date and profile.move_in_date <= date.today() else "onboarding",
        outstanding_tasks=[task.title for task in _baseline_tasks(profile)],
        risk_flags=_derive_risk(profile),
    )
    TENANT_STORE[tenant_id] = record
    ONBOARDING_TASKS[tenant_id] = _baseline_tasks(profile)
    return record


@app.get("/tenants/{tenant_id}", response_model=TenantProfile)
def get_tenant(tenant_id: str) -> TenantProfile:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TENANT_STORE[tenant_id]


class CommunicationRequest(BaseModel):
    author: str
    entry: CommunicationEntryCreate


@app.post("/tenants/{tenant_id}/communications", response_model=CommunicationEntry)
def log_communication(tenant_id: str, request: CommunicationRequest) -> CommunicationEntry:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")

    entry = CommunicationEntry(
        communication_id=str(uuid4()),
        recorded_at=datetime.utcnow(),
        author=request.author,
        entry=request.entry,
    )
    COMMUNICATION_LOGS[tenant_id].append(entry)
    if request.entry.follow_up_required:
        TENANT_STORE[tenant_id].outstanding_tasks.append(request.entry.subject)
    return entry


@app.get("/tenants/{tenant_id}/communications", response_model=List[CommunicationEntry])
def list_communications(tenant_id: str) -> List[CommunicationEntry]:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return COMMUNICATION_LOGS[tenant_id]


@app.get("/tenants/{tenant_id}/onboarding", response_model=List[OnboardingTask])
def list_onboarding_tasks(tenant_id: str) -> List[OnboardingTask]:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return ONBOARDING_TASKS[tenant_id]


class TaskStatusUpdate(BaseModel):
    task_id: str
    status: str


@app.post("/tenants/{tenant_id}/onboarding/status", response_model=List[OnboardingTask])
def update_onboarding_task_status(tenant_id: str, update: TaskStatusUpdate) -> List[OnboardingTask]:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tasks = ONBOARDING_TASKS[tenant_id]
    for task in tasks:
        if task.task_id == update.task_id:
            task.status = update.status
    return tasks


class IncidentCreate(BaseModel):
    category: str
    severity: str
    description: str


@app.post("/tenants/{tenant_id}/incidents", response_model=IncidentReport)
def create_incident(tenant_id: str, payload: IncidentCreate) -> IncidentReport:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")

    severity = payload.severity.lower()
    queue = "tenant-support"
    next_actions = ["Acknowledge tenant", "Review history"]
    if payload.category == "maintenance":
        queue = "maintenance-desk"
        next_actions.append("Create work order")
    if severity in {"high", "urgent"}:
        queue = f"{queue}-priority"
        next_actions.insert(0, "Notify duty manager")

    incident = IncidentReport(
        incident_id=str(uuid4()),
        created_at=datetime.utcnow(),
        category=payload.category,
        severity=payload.severity,
        description=payload.description,
        routed_queue=queue,
        next_actions=next_actions,
    )
    INCIDENT_STORE[tenant_id].append(incident)
    TENANT_STORE[tenant_id].risk_flags.append("incident-open")
    return incident


@app.get("/tenants/{tenant_id}/copilot-summary")
def tenant_copilot_summary(tenant_id: str) -> Dict[str, object]:
    if tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")

    profile = TENANT_STORE[tenant_id]
    communications = COMMUNICATION_LOGS[tenant_id][-3:]
    incidents = INCIDENT_STORE[tenant_id]
    summary = {
        "tenant": profile.profile.full_name,
        "status": profile.lifecycle_status,
        "arrears_balance": profile.profile.arrears_balance,
        "sentiment_score": profile.profile.sentiment_score,
        "recent_communications": [entry.entry.summary for entry in communications],
        "open_incidents": [incident.description for incident in incidents],
        "recommended_next_step": "Schedule welfare check" if profile.profile.sentiment_score < 0.4 else "Maintain regular cadence",
    }
    return summary


@app.get("/tenants/risk-alerts")
def tenant_risk_alerts() -> Dict[str, List[str]]:
    alerts: Dict[str, List[str]] = {}
    for tenant_id, profile in TENANT_STORE.items():
        flags = _derive_risk(profile.profile)
        if "arrears-high" in flags or profile.profile.sentiment_score < 0.3:
            alerts[tenant_id] = flags
    return alerts


class OutboundMessageRequest(BaseModel):
    tenant_id: str
    channel: str
    template: str
    variables: Dict[str, str] = Field(default_factory=dict)


class OutboundMessageResponse(BaseModel):
    message_id: str
    preview: str
    suggested_send_time: datetime
    compliance_notes: List[str]


TEMPLATES = {
    "rent_reminder": "Hi {name}, this is a reminder that your rent of ${amount} is due on {due_date}.",
    "maintenance_update": "Hi {name}, your maintenance request regarding {issue} is scheduled for {date}.",
    "welcome": "Welcome {name}! We're excited to have you move into {property}. Here are your next steps: {steps}.",
}


@app.post("/communications/outbound", response_model=OutboundMessageResponse)
def compose_outbound_message(request: OutboundMessageRequest) -> OutboundMessageResponse:
    tenant = TENANT_STORE.get(request.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    template = TEMPLATES.get(request.template, "Hello {name}")
    preview = template.format(name=tenant.profile.full_name, **request.variables)
    notes = []
    if request.channel == "email" and "unsubscribe" not in preview.lower():
        notes.append("Include unsubscribe footer")
    if tenant.profile.sentiment_score < 0.3:
        notes.append("Use empathetic tone and offer assistance")
    return OutboundMessageResponse(
        message_id=str(uuid4()),
        preview=preview,
        suggested_send_time=datetime.utcnow() + timedelta(hours=2),
        compliance_notes=notes,
    )


class CampaignRequest(BaseModel):
    name: str
    audience: List[str]
    template: str


@app.post("/communications/campaigns")
def schedule_campaign(request: CampaignRequest) -> Dict[str, object]:
    delivered = [tenant_id for tenant_id in request.audience if tenant_id in TENANT_STORE]
    skipped = list(set(request.audience) - set(delivered))
    return {
        "campaign_id": str(uuid4()),
        "delivered": delivered,
        "skipped": skipped,
        "send_count": len(delivered),
        "template_used": request.template,
    }


@app.get("/communications/templates")
def list_templates() -> Dict[str, str]:
    return TEMPLATES


# ---------------------------------------------------------------------------
# Lease Contract & Rent Payment (Lease_Contract_PRD, Rent_Payment_PRD)
# ---------------------------------------------------------------------------


class LeaseCreate(BaseModel):
    tenant_id: str
    property_id: str
    start_date: date
    end_date: date
    rent_amount: float
    frequency: str


class LeaseRecord(BaseModel):
    lease_id: str
    created_at: datetime
    status: str
    documents: List[str]
    signatures: Dict[str, str]
    lease: LeaseCreate


LEASE_STORE: Dict[str, LeaseRecord] = {}


@app.post("/leases", response_model=LeaseRecord)
def create_lease(payload: LeaseCreate) -> LeaseRecord:
    if payload.tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")
    lease_id = str(uuid4())
    record = LeaseRecord(
        lease_id=lease_id,
        created_at=datetime.utcnow(),
        status="draft",
        documents=["draft_contract_v1"],
        signatures={},
        lease=payload,
    )
    LEASE_STORE[lease_id] = record
    return record


class SignatureRequest(BaseModel):
    signer: str
    signed_at: datetime


@app.post("/leases/{lease_id}/signatures", response_model=LeaseRecord)
def capture_signature(lease_id: str, request: SignatureRequest) -> LeaseRecord:
    if lease_id not in LEASE_STORE:
        raise HTTPException(status_code=404, detail="Lease not found")
    lease = LEASE_STORE[lease_id]
    lease.signatures[request.signer] = request.signed_at.isoformat()
    if {"tenant", "owner"}.issubset(lease.signatures.keys()):
        lease.status = "executed"
    LEASE_STORE[lease_id] = lease
    return lease


@app.get("/leases/{lease_id}", response_model=LeaseRecord)
def get_lease(lease_id: str) -> LeaseRecord:
    if lease_id not in LEASE_STORE:
        raise HTTPException(status_code=404, detail="Lease not found")
    return LEASE_STORE[lease_id]


@app.post("/leases/{lease_id}/summary")
def lease_summary(lease_id: str) -> Dict[str, object]:
    if lease_id not in LEASE_STORE:
        raise HTTPException(status_code=404, detail="Lease not found")
    lease = LEASE_STORE[lease_id]
    return {
        "lease_id": lease_id,
        "status": lease.status,
        "duration_days": (lease.lease.end_date - lease.lease.start_date).days,
        "rent_amount": lease.lease.rent_amount,
        "signatures_missing": list({"tenant", "owner"} - set(lease.signatures.keys())),
    }


class RentScheduleCreate(BaseModel):
    lease_id: str
    next_due_date: date
    amount: float
    frequency: str


class RentSchedule(BaseModel):
    schedule_id: str
    lease_id: str
    next_due_date: date
    amount: float
    frequency: str
    arrears: float


class RentPayment(BaseModel):
    payment_id: str
    lease_id: str
    amount: float
    paid_on: date
    method: str


SCHEDULE_STORE: Dict[str, RentSchedule] = {}
PAYMENT_STORE: Dict[str, List[RentPayment]] = defaultdict(list)


@app.post("/rent/schedules", response_model=RentSchedule)
def create_schedule(payload: RentScheduleCreate) -> RentSchedule:
    if payload.lease_id not in LEASE_STORE:
        raise HTTPException(status_code=404, detail="Lease not found")
    schedule_id = str(uuid4())
    schedule = RentSchedule(
        schedule_id=schedule_id,
        lease_id=payload.lease_id,
        next_due_date=payload.next_due_date,
        amount=payload.amount,
        frequency=payload.frequency,
        arrears=0.0,
    )
    SCHEDULE_STORE[schedule_id] = schedule
    return schedule


class RentPaymentCreate(BaseModel):
    lease_id: str
    amount: float
    paid_on: date
    method: str


@app.post("/rent/payments", response_model=RentPayment)
def log_payment(payload: RentPaymentCreate) -> RentPayment:
    if payload.lease_id not in LEASE_STORE:
        raise HTTPException(status_code=404, detail="Lease not found")

    payment = RentPayment(
        payment_id=str(uuid4()),
        lease_id=payload.lease_id,
        amount=payload.amount,
        paid_on=payload.paid_on,
        method=payload.method,
    )
    PAYMENT_STORE[payload.lease_id].append(payment)
    for schedule in SCHEDULE_STORE.values():
        if schedule.lease_id == payload.lease_id:
            schedule.arrears = max(0.0, schedule.arrears - payload.amount)
    return payment


@app.get("/rent/arrears")
def rent_arrears() -> Dict[str, float]:
    arrears: Dict[str, float] = {}
    for schedule in SCHEDULE_STORE.values():
        arrears[schedule.lease_id] = arrears.get(schedule.lease_id, 0.0) + schedule.arrears
    return arrears


# ---------------------------------------------------------------------------
# Maintenance & Work Orders (Repair_Maintenance_PRD, Work_Order_Drafting_PRD)
# ---------------------------------------------------------------------------


class MaintenanceRequest(BaseModel):
    tenant_id: str
    description: str
    severity: str
    location: str
    preferred_times: List[str] = Field(default_factory=list)


class WorkOrder(BaseModel):
    work_order_id: str
    created_at: datetime
    status: str
    queue: str
    vendor_id: Optional[str]
    tenant_id: Optional[str]
    tasks: List[str]
    sla_due: datetime


WORK_ORDER_STORE: Dict[str, WorkOrder] = {}


def _draft_tasks(description: str) -> List[str]:
    if "leak" in description.lower():
        return ["Isolate water supply", "Dispatch plumber", "Capture photos"]
    if "electrical" in description.lower():
        return ["Switch off circuit", "Assign electrician", "Run safety check"]
    return ["Contact tenant", "Assess issue", "Schedule vendor"]


def _maintenance_queue(severity: str) -> str:
    severity = severity.lower()
    if severity in {"high", "urgent"}:
        return "maintenance-priority"
    if severity in {"medium", "moderate"}:
        return "maintenance-standard"
    return "maintenance-backlog"


@app.post("/maintenance/work-orders", response_model=WorkOrder)
def create_work_order(payload: MaintenanceRequest) -> WorkOrder:
    if payload.tenant_id not in TENANT_STORE:
        raise HTTPException(status_code=404, detail="Tenant not found")
    work_order_id = str(uuid4())
    tasks = _draft_tasks(payload.description)
    queue = _maintenance_queue(payload.severity)
    sla = datetime.utcnow() + (
        timedelta(hours=4) if queue == "maintenance-priority" else timedelta(days=2)
    )
    work_order = WorkOrder(
        work_order_id=work_order_id,
        created_at=datetime.utcnow(),
        status="draft",
        queue=queue,
        vendor_id=None,
        tenant_id=payload.tenant_id,
        tasks=tasks,
        sla_due=sla,
    )
    WORK_ORDER_STORE[work_order_id] = work_order
    INCIDENT_STORE[payload.tenant_id].append(
        IncidentReport(
            incident_id=str(uuid4()),
            created_at=datetime.utcnow(),
            category="maintenance",
            severity=payload.severity,
            description=payload.description,
            routed_queue=queue,
            next_actions=tasks,
        )
    )
    return work_order


class WorkOrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


@app.post("/maintenance/work-orders/{work_order_id}/status", response_model=WorkOrder)
def update_work_order_status(work_order_id: str, update: WorkOrderStatusUpdate) -> WorkOrder:
    if work_order_id not in WORK_ORDER_STORE:
        raise HTTPException(status_code=404, detail="Work order not found")
    order = WORK_ORDER_STORE[work_order_id]
    order.status = update.status
    WORK_ORDER_STORE[work_order_id] = order
    return order


@app.get("/maintenance/work-orders/{work_order_id}", response_model=WorkOrder)
def get_work_order(work_order_id: str) -> WorkOrder:
    if work_order_id not in WORK_ORDER_STORE:
        raise HTTPException(status_code=404, detail="Work order not found")
    return WORK_ORDER_STORE[work_order_id]


# ---------------------------------------------------------------------------
# Vendor Management (Vendor_Management_PRD)
# ---------------------------------------------------------------------------


class VendorProfileCreate(BaseModel):
    name: str
    services: List[str]
    compliance_docs: List[str] = Field(default_factory=list)
    rating: Optional[float] = None


class VendorProfile(BaseModel):
    vendor_id: str
    created_at: datetime
    profile: VendorProfileCreate
    performance_notes: List[str]


VENDOR_STORE: Dict[str, VendorProfile] = {}


@app.post("/vendors", response_model=VendorProfile)
def create_vendor(profile: VendorProfileCreate) -> VendorProfile:
    vendor_id = str(uuid4())
    record = VendorProfile(
        vendor_id=vendor_id,
        created_at=datetime.utcnow(),
        profile=profile,
        performance_notes=[],
    )
    VENDOR_STORE[vendor_id] = record
    return record


class VendorEvaluation(BaseModel):
    score: float
    comments: str


@app.post("/vendors/{vendor_id}/evaluation", response_model=VendorProfile)
def evaluate_vendor(vendor_id: str, evaluation: VendorEvaluation) -> VendorProfile:
    if vendor_id not in VENDOR_STORE:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor = VENDOR_STORE[vendor_id]
    note = f"{datetime.utcnow().date().isoformat()} - Score {evaluation.score}: {evaluation.comments}"
    vendor.performance_notes.append(note)
    VENDOR_STORE[vendor_id] = vendor
    return vendor


class VendorAssignment(BaseModel):
    work_order_id: str


@app.post("/vendors/{vendor_id}/assign", response_model=WorkOrder)
def assign_vendor(vendor_id: str, assignment: VendorAssignment) -> WorkOrder:
    if vendor_id not in VENDOR_STORE:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if assignment.work_order_id not in WORK_ORDER_STORE:
        raise HTTPException(status_code=404, detail="Work order not found")
    order = WORK_ORDER_STORE[assignment.work_order_id]
    order.vendor_id = vendor_id
    order.status = "scheduled"
    WORK_ORDER_STORE[assignment.work_order_id] = order
    return order


# ---------------------------------------------------------------------------
# Owner Management (Owner_Management_PRD)
# ---------------------------------------------------------------------------


class OwnerProfileCreate(BaseModel):
    name: str
    email: str
    properties: List[str]


class OwnerProfile(BaseModel):
    owner_id: str
    created_at: datetime
    profile: OwnerProfileCreate
    preferences: Dict[str, str]


OWNER_STORE: Dict[str, OwnerProfile] = {}


@app.post("/owners", response_model=OwnerProfile)
def create_owner(payload: OwnerProfileCreate) -> OwnerProfile:
    owner_id = str(uuid4())
    record = OwnerProfile(
        owner_id=owner_id,
        created_at=datetime.utcnow(),
        profile=payload,
        preferences={"report_frequency": "monthly", "communication": "email"},
    )
    OWNER_STORE[owner_id] = record
    return record


@app.get("/owners/{owner_id}/portfolio")
def owner_portfolio(owner_id: str) -> Dict[str, object]:
    if owner_id not in OWNER_STORE:
        raise HTTPException(status_code=404, detail="Owner not found")
    owner = OWNER_STORE[owner_id]
    properties = owner.profile.properties
    occupancy_rate = 0.95 if properties else 0.0
    return {
        "owner": owner.profile.name,
        "properties": properties,
        "occupancy_rate": occupancy_rate,
        "upcoming_events": ["Lease renewal due in 30 days"],
    }


# ---------------------------------------------------------------------------
# Document Vault & Structured Extraction (Documents_PRD, Structured_Extraction_PRD)
# ---------------------------------------------------------------------------


class DocumentCreate(BaseModel):
    title: str
    category: str
    related_entity: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    content: str


class DocumentRecord(BaseModel):
    document_id: str
    uploaded_at: datetime
    document: DocumentCreate
    ai_summary: str


DOCUMENT_STORE: Dict[str, DocumentRecord] = {}


@app.post("/documents", response_model=DocumentRecord)
def upload_document(payload: DocumentCreate) -> DocumentRecord:
    document_id = str(uuid4())
    summary = payload.content[:140] + "..." if len(payload.content) > 140 else payload.content
    record = DocumentRecord(
        document_id=document_id,
        uploaded_at=datetime.utcnow(),
        document=payload,
        ai_summary=summary,
    )
    DOCUMENT_STORE[document_id] = record
    return record


@app.get("/documents/{document_id}", response_model=DocumentRecord)
def get_document(document_id: str) -> DocumentRecord:
    if document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found")
    return DOCUMENT_STORE[document_id]


@app.get("/documents/search")
def search_documents(tag: Optional[str] = None, category: Optional[str] = None) -> List[DocumentRecord]:
    results = []
    for record in DOCUMENT_STORE.values():
        if tag and tag not in record.document.tags:
            continue
        if category and record.document.category != category:
            continue
        results.append(record)
    return results


class ExtractionRequest(BaseModel):
    document_id: str
    extraction_type: str


@app.post("/extractions")
def run_extraction(request: ExtractionRequest) -> Dict[str, object]:
    if request.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found")
    document = DOCUMENT_STORE[request.document_id]
    extracted = {
        "lease": {"tenant": document.document.related_entity, "rent": "1200"},
        "invoice": {"vendor": document.document.related_entity, "amount": "540"},
    }
    payload = extracted.get(request.extraction_type, {"summary": document.ai_summary})
    return {
        "document_id": request.document_id,
        "extraction_type": request.extraction_type,
        "fields": payload,
        "confidence": 0.82,
    }


# ---------------------------------------------------------------------------
# Knowledge RAG & Analytics (Knowledge_RAG_PRD, Data_Analytics_PRD)
# ---------------------------------------------------------------------------


class KnowledgeArticle(BaseModel):
    article_id: str
    title: str
    body: str
    tags: List[str]


KNOWLEDGE_BASE: Dict[str, KnowledgeArticle] = {}


class KnowledgeCreate(BaseModel):
    title: str
    body: str
    tags: List[str]


@app.post("/knowledge/articles", response_model=KnowledgeArticle)
def create_article(payload: KnowledgeCreate) -> KnowledgeArticle:
    article_id = str(uuid4())
    article = KnowledgeArticle(article_id=article_id, title=payload.title, body=payload.body, tags=payload.tags)
    KNOWLEDGE_BASE[article_id] = article
    return article


class KnowledgeQuery(BaseModel):
    question: str
    top_k: int = 3


@app.post("/knowledge/query")
def knowledge_query(payload: KnowledgeQuery) -> Dict[str, object]:
    question_tokens = set(payload.question.lower().split())
    scored = []
    for article in KNOWLEDGE_BASE.values():
        score = len(question_tokens.intersection(set(article.body.lower().split())))
        scored.append((score, article))
    scored.sort(key=lambda item: item[0], reverse=True)
    top_articles = [article for _, article in scored[: payload.top_k]]
    return {
        "question": payload.question,
        "results": [
            {"article_id": article.article_id, "title": article.title, "snippet": article.body[:120]} for article in top_articles
        ],
        "confidence": 0.6 + 0.1 * len(top_articles),
    }


@app.get("/analytics/dashboard")
def analytics_dashboard() -> Dict[str, object]:
    return {
        "active_tenants": len(TENANT_STORE),
        "open_work_orders": sum(1 for order in WORK_ORDER_STORE.values() if order.status != "completed"),
        "average_sentiment": (
            sum(profile.profile.sentiment_score for profile in TENANT_STORE.values()) / len(TENANT_STORE)
            if TENANT_STORE
            else 0.0
        ),
        "arrears_total": sum(schedule.arrears for schedule in SCHEDULE_STORE.values()),
        "owner_count": len(OWNER_STORE),
    }


# ---------------------------------------------------------------------------
# House Acceptance & Inspection Workflows (House_Acceptance_PRD)
# ---------------------------------------------------------------------------


class InspectionTemplateCreate(BaseModel):
    name: str
    property_type: str
    checklist: List[str]


class InspectionTemplate(BaseModel):
    template_id: str
    created_at: datetime
    template: InspectionTemplateCreate


INSPECTION_TEMPLATES: Dict[str, InspectionTemplate] = {}


@app.post("/inspections/templates", response_model=InspectionTemplate)
def create_inspection_template(payload: InspectionTemplateCreate) -> InspectionTemplate:
    template_id = str(uuid4())
    record = InspectionTemplate(template_id=template_id, created_at=datetime.utcnow(), template=payload)
    INSPECTION_TEMPLATES[template_id] = record
    return record


class InspectionSessionCreate(BaseModel):
    template_id: str
    inspector: str
    property_id: str
    scheduled_for: datetime


class InspectionSession(BaseModel):
    session_id: str
    template_id: str
    inspector: str
    property_id: str
    scheduled_for: datetime
    status: str
    findings: List[str]
    issues_detected: List[str]
    report_url: Optional[str]


INSPECTION_SESSIONS: Dict[str, InspectionSession] = {}


@app.post("/inspections/sessions", response_model=InspectionSession)
def schedule_inspection(payload: InspectionSessionCreate) -> InspectionSession:
    if payload.template_id not in INSPECTION_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    session_id = str(uuid4())
    findings = ["Checklist initiated", "Awaiting onsite data"]
    issues = []
    session = InspectionSession(
        session_id=session_id,
        template_id=payload.template_id,
        inspector=payload.inspector,
        property_id=payload.property_id,
        scheduled_for=payload.scheduled_for,
        status="scheduled",
        findings=findings,
        issues_detected=issues,
        report_url=None,
    )
    INSPECTION_SESSIONS[session_id] = session
    return session


class InspectionUpdate(BaseModel):
    notes: List[str]
    photos_uploaded: int = 0


@app.post("/inspections/sessions/{session_id}/complete", response_model=InspectionSession)
def complete_inspection(session_id: str, payload: InspectionUpdate) -> InspectionSession:
    if session_id not in INSPECTION_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    session = INSPECTION_SESSIONS[session_id]
    session.status = "completed"
    session.findings.extend(payload.notes)
    if payload.photos_uploaded > 0:
        session.issues_detected.append("Images pending review")
    session.report_url = f"https://reports.example.com/{session_id}"
    INSPECTION_SESSIONS[session_id] = session
    return session


# ---------------------------------------------------------------------------
# Rent Payment Insights & Forecasts (Rent_Payment_PRD enhancements)
# ---------------------------------------------------------------------------


@app.get("/rent/forecasts")
def rent_forecasts() -> Dict[str, object]:
    projections = []
    for schedule in SCHEDULE_STORE.values():
        projections.append(
            {
                "lease_id": schedule.lease_id,
                "next_due_date": schedule.next_due_date,
                "projected_amount": schedule.amount,
                "risk": "high" if schedule.arrears > schedule.amount else "normal",
            }
        )
    return {"projections": projections, "generated_at": datetime.utcnow()}


# ---------------------------------------------------------------------------
# Owner & Tenant Reporting (Tenant_Management_PRD, Owner_Management_PRD)
# ---------------------------------------------------------------------------


@app.get("/reports/tenant-health")
def tenant_health_report() -> Dict[str, object]:
    report = []
    for tenant_id, profile in TENANT_STORE.items():
        report.append(
            {
                "tenant_id": tenant_id,
                "name": profile.profile.full_name,
                "sentiment": profile.profile.sentiment_score,
                "arrears": profile.profile.arrears_balance,
                "open_tasks": len(profile.outstanding_tasks),
            }
        )
    return {"generated_at": datetime.utcnow(), "tenants": report}


@app.get("/reports/owner-summary")
def owner_summary_report() -> Dict[str, object]:
    report = []
    for owner_id, owner in OWNER_STORE.items():
        report.append(
            {
                "owner_id": owner_id,
                "name": owner.profile.name,
                "properties": owner.profile.properties,
                "occupancy_rate": 0.95,
            }
        )
    return {"generated_at": datetime.utcnow(), "owners": report}


# ---------------------------------------------------------------------------
# Feedback-driven optimisation (global)
# ---------------------------------------------------------------------------


@app.get("/feedback/items")
def list_feedback_items() -> List[FeedbackRequest]:
    return FEEDBACK_STORE


# ---------------------------------------------------------------------------
# Utility endpoints for testing & demos
# ---------------------------------------------------------------------------


@app.get("/")
def index() -> Dict[str, str]:
    return {"message": "Aptify backend prototype covering PRD feature families."}
