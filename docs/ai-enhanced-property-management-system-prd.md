# AI-Enhanced Property Management System PRD

## 1. Product Overview

### 1.1 Vision
- Deliver an AI-enhanced, SaaS-native platform that lets Australian property managers manage portfolios through natural-language interactions.
- Reduce manual data entry, accelerate tenant response times, and surface the right vendors and policy guidance at the moment of need.
- Build trust with defensible AI guardrails: transparent citations, refusals when unsure, and human approval loops for critical actions.

### 1.2 Strategic Goals
- **Operational efficiency**: Cut time-to-resolution for maintenance and tenant enquiries by at least 40%.
- **Data quality**: Achieve ≥90% accuracy for extracted tenant, property, and issue metadata from free text.
- **Compliance and trust**: Ensure every factual AI response cites authoritative internal sources; maintain traceable trails for all AI-assisted actions.
- **Commercial viability**: Launch subscription-based service targeting independent agencies managing 500–5,000 properties with clear ROI.

### 1.3 Business Context
- Australian property management retains legacy, manual processes and fragmented vendor relationships.
- Competitive advantage comes from locally hosted data, independence from third-party platforms, and rapid onboarding via CSV/PDF exports before integrations.
- Investors value recurring revenue, low churn, and expansion potential through marketplace services and future add-ons.

### 1.4 Differentiators
- AI copilot tuned for property management jargon, Australian regulations, and tenancy workflows.
- Retrieval-augmented responses with verifiable citations; system refuses to fabricate information.
- Vendor recommendation engine leveraging internal performance history and budget constraints.
- Modular architecture enabling future integrations without compromising initial independence.

## 2. Target Users and Personas

### 2.1 Senior Property Manager (Primary)
- Oversees 300–800 properties; accountable for tenant satisfaction and regulatory compliance.
- Needs rapid triage of incoming issues, visibility into SLA breaches, and reliable vendor assignments.

### 2.2 Property Management Assistant
- Handles daily log entries, follow-ups, and documentation.
- Requires streamlined data entry from calls/emails and automation for repetitive communications.

### 2.3 Regional Portfolio Manager
- Manages multiple offices; focuses on regulatory compliance and risk management.
- Needs timely visibility into SLA breaches, compliance requirements, and escalation alerts.

### 2.4 Service Vendor Coordinator
- Maintains local vendor roster and negotiates rates.
- Needs insights on vendor workload, availability, and performance outcomes.

### 2.5 Tenant Support Agent (Secondary)
- Frontline responder to tenant queries.
- Needs quick access to policies and templated responses with citations.

## 3. Key User Stories

### 3.1 Senior Property Manager
- Receive tenant email transcript; copilot extracts issue type, priority, SLA, and drafts response citing building policy.
- Ask: “Summarise outstanding high-priority maintenance for building 12 this week” and receive actionable digest.
- Generate work order draft with recommended vendors and export for approval.

### 3.2 Property Management Assistant
- Speak or paste inspection notes; system identifies defects, assigns severity, and updates property record.
- Request: “Log payment arrangement for tenant James Lee” and capture structured data without manual form filling.

### 3.3 Regional Portfolio Manager
- Configure alerts for unresolved issues >7 days and route to responsible manager.

### 3.4 Service Vendor Coordinator
- Query: “Suggest top vendors for leaking roof at 45 King St under $1,500” and receive ranked list with rationale.
- Update vendor profile via CSV import; copilot verifies data integrity and highlights missing insurance documents.

### 3.5 Tenant Support Agent
- Prompt: “Draft response to tenant about dog approval referencing City of Sydney guidelines” → AI cites stored policy documents.
- Ask clarifying questions and receive refusal when information is insufficient, preserving compliance.
- Tenant calls dedicated support number; AI voice agent authenticates caller, collects structured issue details, logs ticket, and routes urgent cases for human follow-up while displaying transcript in the agent workspace.

## 4. Core Features and Functional Requirements

### 4.1 Structured Information Extraction
- Automatic detection of tenant name, property address, issue category, severity, SLA target, sentiment, and attachments.
- Confidence scoring with inline highlighting; low-confidence fields flagged for human confirmation.
- Editable structured output before commit; AI never writes directly to production database without approval.

### 4.2 Work Order Drafting
- Generate scope including problem description, recommended steps, required materials, estimated cost, and SLA.
- Suggest 1–3 vendors ranked by fit; include vendor contact info and justification.
- Export to PDF/CSV; enable download and secure share link.

### 4.3 Tenant Communication Assistance
- Draft responses using RAG to pull policy excerpts and historical notices; cite all sources.
- Provide tone controls (formal, empathetic, urgent) with preview.
- Refuse to answer or escalate when source confidence is below threshold or conflicting.

### 4.4 Vendor Management
- Maintain local vendor registry with specialties, coverage zone, rates, licensing, insurance expiry.
- Historical performance tracking (completion rate, average response time, tenant feedback).
- Search, filter, and bulk import/export capability.

### 4.5 Knowledge Management and RAG Corpus
- Content ingestion from PDFs, DOCX, emails, and web archives of community policies.
- Metadata tagging by property, date, policy type, or notice.
- Version control with rollback; change log when documents become obsolete.

### 4.6 AI Tenant Intake Agent
- Dedicated phone line and monitored inbox fronted by AI; callers and email senders interact with natural-language agent that mirrors agency scripts.
- Real-time transcription and summarisation feed structured extraction to auto-populate issue tickets and recommended tasks.
- Identity verification via property-specific challenge questions or SMS OTP before sensitive updates.
- Escalation pathways for emergencies or low-confidence captures, with full transcript and audio snippet surfaced in the agent workspace.

### 4.7 Source Pool Directory
- **Feature Overview**: Maintain a Source Pool covering all external workers—plumbers, electricians, HVAC technicians, cleaners—supporting agency teams, with profiles visible alongside active workflows.
- **Core Functionality**: Store worker metadata (trade, certifications, coverage zones, contact channels, service history) and associate each record with work orders, jobs, and past communications.
- **Goals / Benefits**: Streamline agent outreach to trusted providers, reduce time spent finding qualified workers, and ensure consistent service quality.
- **User Flow**: Agent filters Source Pool by trade/location/performance → selects worker → links record to job ticket → communication history updates automatically.
- **Technical Notes**: Persist Source Pool data within vendor registry tables; sync updates from onboarding forms or CSV imports; expose APIs for downstream scheduling tools.
- **Metrics for Success**: ≥95% completeness of worker profiles; ≥30% reduction in time-to-assign vendor; <2% of outbound messages fail due to outdated contact info.

### 4.8 Intelligent Message Intake Orchestration
- **Feature Overview**: Aggregate all inbound communications sent to property management agents across email, SMS, and messaging integrations into a unified queue tied to the Source Pool.
- **Core Functionality**: Ingest and normalise multi-channel messages, auto-categorise content by topic (maintenance, scheduling, payment, compliance), and trigger AI Copilot drafts for agent approval.
- **Goals / Benefits**: Streamline collaboration with service providers, reduce manual triage effort, and maintain consistent tone and accuracy in agent responses.
- **User Flow**: Incoming message received → categorised → matched to relevant topic or job → AI Copilot suggests reply → agent reviews edits if needed → response sent and logged.
- **Technical Notes**: Integrate with email/SMS APIs; apply NLP pipelines for topic detection, summarisation, and entity extraction; retain correspondence and classifications linked to Source Pool contacts.
- **Metrics for Success**: ≥90% of messages categorised correctly without intervention; ≥45 minutes saved per agent per day; ≥4.5/5 average agent satisfaction with AI-generated drafts.

### 4.9 Documents Control (Invoices & Records)
- **Feature Overview**: Centralise management of invoices, receipts, quotes, and contracts linked to properties, jobs, and compliance obligations.
- **Core Functionality**: Support upload from desktop/mobile, smart tagging by property/job/vendor, approval routing, version tracking, and granular access controls for agents, owners, and tenants.
- **User Flow**: Agent uploads document → applies tags or accepts AI-suggested metadata → selects approval path → reviewers approve/annotate → final version attaches to property/job record and becomes searchable.
- **Technical Notes**: Store objects in encrypted document repository (S3-compatible) with metadata in relational DB; leverage OCR for text extraction; enforce RBAC policies and audit logs; integrate with e-signature providers when needed.
- **Metrics for Success**: ≥95% of documents tagged accurately; average document approval turnaround reduced by 40%; zero unauthorised document access incidents.

### 4.10 Inspection Manager
- **Feature Overview**: Maintain a live schedule of inspections with assigned agents or contractors, ensuring timely execution and reporting.
- **Core Functionality**: Create inspection events, assign personnel, attach checklists/templates, trigger reminders, and capture outcomes via mobile or desktop.
- **User Flow**: Property flagged for inspection → agent schedules date/time → assignee receives calendar invite and reminder → inspection completed using template → report and photos uploaded → stakeholders notified.
- **Technical Notes**: Sync with calendar APIs (Google/Microsoft); provide offline-capable mobile interface; store inspection templates and outcomes in structured schema; integrate push/SMS reminders.
- **Metrics for Success**: ≥90% of inspections completed on schedule; inspection report submission time reduced by 50%; ≥4.5/5 satisfaction from agents using mobile workflow.

### 4.11 Rent & Cashflow
- **Feature Overview**: Automate rent communications, track inflows/outflows, and surface cashflow insights for properties and owners.
- **Core Functionality**: Send rent reminders and receipts, monitor overdue balances, publish dashboards showing monthly cashflow, and support CSV exports for accounting.
- **User Flow**: Rent schedule ingested → system issues reminders ahead of due dates → payments reconciled → overdue accounts flagged → receipts auto-generated → owners view cashflow dashboard and export data.
- **Technical Notes**: Integrate with payment gateways/banking feeds where available; maintain ledger tables for rent/expense transactions; generate PDFs via templating service; expose webhooks for accounting sync.
- **Metrics for Success**: ≥80% of tenants receive automated reminders; overdue rent reduced by 25%; monthly cashflow dashboards accessed by ≥70% of owners.

### 4.12 Knowledge Base (Law & Policy RAG System)
- **Feature Overview**: Provide AI-assisted answers grounded in property law, compliance rules, and internal policies via retrieval-augmented generation.
- **Core Functionality**: Allow natural-language queries, retrieve relevant legal/policy documents, and deliver AI responses with citations and confidence indicators.
- **User Flow**: User asks compliance question → RAG retrieves supporting passages → AI drafts answer with cited sources → user reviews, bookmarks, or escalates for legal confirmation if needed.
- **Technical Notes**: Curate legal corpus with metadata (jurisdiction, topic, effective dates); ingest via document pipeline; use vector search plus hybrid keyword filters; enforce human-in-loop for low-confidence responses.
- **Metrics for Success**: ≥95% citation accuracy; ≥60% of compliance queries resolved without escalation; average time to answer regulatory questions reduced by 50%.

### 4.13 AI Intake Ops (Urgency-Based Reordering)
- **Feature Overview**: Automatically prioritise incoming maintenance and tenant requests based on urgency to focus agent attention on critical work.
- **Core Functionality**: Analyse message content for urgency cues, assign priority levels, reorder queues in the operations dashboard, and allow manual overrides.
- **User Flow**: Message ingested → NLP scores urgency and sentiment → task queued with visual indicator (high/medium/low) → agent reviews, optionally overrides, and actioned item moves forward in workflow.
- **Technical Notes**: Train classifiers on historical resolution data; incorporate keyword rules and sentiment analysis; expose priority state via real-time API/WebSocket; log overrides for continuous model tuning.
- **Metrics for Success**: ≥85% accuracy in urgency classification; high-priority tasks addressed within SLA 95% of the time; manual overrides decrease by 30% as model matures.

### 4.14 Email Classification and Tagging
- **Feature Overview**: Provide automated email triage that categorises, tags, and routes inbound communications to the right workflows.
- **Core Functionality**: Detect intent (maintenance, payments, compliance, general enquiry), apply configurable labels, map emails to existing tickets or create new ones, and surface suggested next actions within the agent workspace.
- **Goals / Benefits**: Reduce manual inbox triage, ensure consistent tagging for reporting, and accelerate assignment to responsible teams.
- **User Flow**: Email received → AI analyses subject/body/attachments → system assigns category and tags → linked ticket updated or created → agent reviews and confirms routing.
- **Technical Notes**: Leverage fine-tuned classifiers with continual learning from historical email data; support IMAP/API ingestion; maintain audit trail of classification confidence and overrides.
- **Metrics for Success**: ≥90% precision/recall on top-level categories; 50% reduction in average email triage time; <5% of emails require reclassification by agents.

### 4.15 Feedback-Driven Model Optimisation
- **Feature Overview**: Capture explicit agent feedback on AI actions (classifications, drafts, recommendations) to improve model performance over time.
- **Core Functionality**: Provide in-line thumbs up/down and correction forms, log contextual metadata, route negative feedback to review queue, and incorporate validated signals into retraining datasets.
- **Goals / Benefits**: Maintain high model accuracy, build user trust through responsive improvements, and create governance artefacts for compliance.
- **User Flow**: Agent reviews AI output → submits feedback if adjustments needed → system stores annotated example → ops team reviews, labels, and pushes to training pipeline → updated models deployed with changelog.
- **Technical Notes**: Store feedback data in secure repository with role-based access; integrate with ML Ops workflows for evaluation, A/B testing, and automated monitoring dashboards.
- **Metrics for Success**: ≥60% of negative feedback resolved within one sprint; measurable uplift in model accuracy per release; maintain traceability between feedback items and model updates.

## 5. End-to-End Workflows

### 5.1 Issue Intake and Classification
1. User pastes tenant email into the agent workspace.
2. Copilot parses entities, proposes structured fields and recommended issue class.
3. User reviews, edits if necessary, and approves.
4. System logs issue, sets SLA, triggers notification to assigned manager.

### 5.2 Work Order Creation
1. User asks copilot to draft work order for approved issue.
2. AI fetches historical repairs, vendor metrics, and building specs.
3. Copilot drafts order with recommended vendors and cost estimate.
4. User selects vendor, finalises draft, exports PDF/CSV for signature or uploads to external system.

### 5.3 Tenant Reply
1. User requests AI to compose response referencing policy.
2. RAG retrieves relevant documents; AI cites references inline.
3. User edits, approves, and sends via existing email workflow (manual during MVP).
4. Conversation logged with citation and timestamp.

### 5.4 Vendor Registry Maintenance
1. Coordinator uploads CSV of vendor updates.
2. System validates required fields, flags missing compliance items.
3. Approved records update local registry; change history stored for future reference.

### 5.5 AI Tenant Voice/Email Intake
1. Tenant calls dedicated number or sends email to agency intake address.
2. AI agent greets tenant, authenticates identity, and gathers issue description, urgency, preferred contact method, and access constraints.
3. Conversation is transcribed; structured fields auto-populate new issue ticket with recommended task routing.
4. System notifies assigned manager, displays transcript/audio snippet in the agent workspace, and flags follow-up actions needing human confirmation.

## 6. Data Model and Sources

### 6.1 Core Entities
- Property: address, owner, strata info, compliance certificates.
- Tenant: contact info, lease details, communication history.
- Issue Ticket: category, subcategory, priority, SLA, attachments, status.
- Work Order: linked issue, vendor, cost estimates, schedule, completion notes.
- Vendor: capabilities, pricing, documents, performance metrics.
- Knowledge Asset: document metadata, embeddings, citation anchors.

### 6.2 Data Ingestion
- Manual entry through copilot-assisted workflow.
- Batch uploads via CSV for properties, tenants, vendors; validation on import.
- Document ingestion service accepting PDFs/DOCX with OCR for scans.

### 6.3 Data Governance
- Store data in Australian-hosted infrastructure.
- Access control enforced at row/column level for sensitive fields (e.g., tenant PII).
- Retention policies configurable per client; default 7-year archival for compliance.

## 7. System Architecture Overview

### 7.1 High-Level Components
- **Web Client**: React/Next single-page app with role-based UI modules, integrated voice input, and real-time updates via WebSockets.
- **Application API Layer**: Node.js/TypeScript services handling authentication (OIDC), business logic, exports, and vendor registry management.
- **AI Service Layer**: Dedicated microservice orchestrating LLM calls, parsers, RAG retrieval, vendor ranking, and guardrails.
- **Data Stores**: PostgreSQL for transactional data, object storage (S3-compatible) for documents, vector database (pgvector or Pinecone alternative) for embeddings, Redis for caching.
- **Observability Stack**: OpenTelemetry traces, Prometheus metrics, Loki logs, Grafana dashboards.

### 7.2 Integration Strategy
- REST/GraphQL APIs for future partner systems; webhooks for event-driven updates.
- Secure file drop (SFTP or HTTPS) for batch export/import during early phases.
- Future connectors planned for MYOB, Xero, Maintenance Manager once API maturity reached.

### 7.3 Security and Compliance
- SOC 2-aligned controls roadmap; encryption at rest (AES-256) and in transit (TLS 1.3).
- Role-based permissions; MFA and SSO for enterprise tiers.
- Regular penetration testing and vulnerability scanning.

## 8. AI Module Design

### 8.1 Copilot Orchestration
- “Parse → Decide → Draft” pipeline triggered per user interaction.
- System prompt defines persona, refusal policy, citation requirement, and JSON schema for extracted fields.
- Tooling layer selects between extraction, RAG lookup, vendor ranking, or drafting functions.

### 8.2 Information Extraction
- Fine-tuned transformer model for Australian property vocabulary with post-processing for addresses and amounts.
- Ensemble approach: NER, classification, and rule-based heuristics for SLA determination.
- Continuous learning via human feedback loop; flagged corrections stored as training data.

### 8.3 RAG Workflow
- Document ingestion pipeline creates embeddings (e.g., Instructor or OpenAI text-embedding-3-large) and stores metadata in vector DB.
- Hybrid retrieval (semantic + keyword) to ensure high recall on policy clauses.
- Response generator composes answer with inline citations (e.g., “[Source: Strata Policy 2023 §4.2]”).
- Confidence scoring; below-threshold responses default to refusal with guidance on next steps.

### 8.4 Vendor Recommendation Engine
- Feature inputs: issue category, severity, property location, budget, historical performance, vendor availability windows.
- Model: Gradient-boosted ranking (e.g., XGBoost) retrained monthly; fallback rules when data sparse.
- Output: ranked list of 1–3 vendors with decision rationale and risk flags (licence expiry, pending disputes).

### 8.5 Guardrails and Safety
- PII detection and redaction before LLM calls.
- Policy filters preventing sensitive actions (no direct CRUD, no financial advice).
- Monitoring of hallucination risk using QA pairs and automated red teaming.

### 8.6 Latency and Cost Optimisation
- Route extraction to lightweight hosted models; leverage larger models only for drafting.
- Response streaming to UI for perceived performance.
- Prompt caching and compression; daily cost reporting per tenant/property.

## 9. Non-Functional Requirements

- **Availability**: Target 99.5% uptime for MVP; scale to 99.9% with redundancy by Phase 3.
- **Scalability**: Support 1,000 concurrent sessions with <5s P95 response time for copilot interactions.
- **Data Residency**: All production data stored in Australian regions; ensure compliance with Privacy Act 1988.
- **Usability**: Achieve SUS >80 in pilot; accessible design meeting WCAG 2.1 AA.
- **Observability**: Metrics for extraction accuracy, RAG hit rate, vendor recommendation acceptance, and latency.
- **Supportability**: Admin portal for configuration, service health dashboards, and incident playbooks.

## 10. Success Metrics and Evaluation Plan

- **Adoption**: ≥60% of active users engage copilot weekly within three months of onboarding.
- **Efficiency**: Median time from issue intake to work order draft reduced from baseline by 40%.
- **Quality**: Citation accuracy ≥95%; extraction F1 ≥0.9 on key fields (tenant, property, issue type, priority).
- **Reliability**: Copilot refusal rate when unsure <5%; false confident answers <1% in quality reviews.
- **Vendor Utilisation**: AI-recommended vendors accepted without changes ≥70%.
- **User Satisfaction**: CSAT ≥4.5/5 for AI-assisted tasks; NPS increase of +10 points after six months.
- **Tenant Intake Automation**: ≥60% of business-hours inbound tenant calls/emails are handled end-to-end by AI agent without manual intake.
- **Financial**: Gross margin ≥70% by end of Year 1; churn <5% per quarter.
- Evaluation cadence: Monthly performance review, quarterly customer advisory board feedback, and biannual penetration tests.

## 11. Release Plan and Initial Deliverables

### 11.1 Phase 0 – Foundation (Month 0–1)
- Finalise data schemas, security baselines, and AI governance policies.
- Build document ingestion and embedding pipeline.
- Deliver CSV/PDF export templates for issues, work orders, and vendor lists.

### 11.2 Phase 1 – MVP (Month 2–4)
- Enable vendor recommendation v1 with rule-based fallback.
- Provide manual export workflows and batch import for properties/tenants/vendors.

### 11.3 Phase 2 – Beta Enhancements (Month 5–7)
- Add approval workflows, SLA alerts, and scheduled reporting.
- Introduce voice input, mobile-responsive UI, and vendor availability tracking.
- Pilot AI tenant intake agent covering voice calls and emails with supervised review queue.
- Expand guardrails and feedback loops for continuous learning.

### 11.4 Phase 3 – General Availability (Month 8–12)
- Integrate optional APIs (accounting, maintenance platforms) while preserving independence.
- Launch marketplace onboarding for certified vendors.

## 12. Future Roadmap

- **Integrations**: Bi-directional sync with accounting/ERP systems, e-signature providers, and tenant portals.
- **Expansion**: Multi-region support (New Zealand, UK), multilingual copilot, white-label offering for enterprise agencies.
- **Optimisation**: Reinforcement learning from human feedback, cost-aware model routing, predictive vacancy and budget forecasts.
- **Marketplace**: Vendor performance benchmarking, insurance verification services, dynamic scheduling optimisation.
- **Compliance**: ISO 27001 certification, real-time compliance monitoring, automated tribunal documentation packages.

## 13. Risks and Mitigations

- **Low trust in AI outputs**: Provide transparent citations, editable structured fields, and traceable records; run pilot programs with high-touch onboarding.
- **Data privacy concerns**: Host data within Australia, enforce strict access controls, and communicate compliance posture clearly.
- **Vendor data staleness**: Implement reminders for document expiry and quarterly data hygiene reviews.
- **Model drift**: Schedule retraining, monitor accuracy dashboards, and maintain human feedback loop.
- **Latency/cost overruns**: Introduce usage quotas, model routing, and continuous profiling of AI service costs.

## 14. Open Questions

- Preferred pricing model (per property vs. per seat) for launch cohort?
- Required integration priorities post-MVP (accounting vs. maintenance vs. tenant portals)?
- Appetite for AI-driven proactive insights (vacancy prediction) in early phases?
- Legal review requirements for AI-generated tenant communications in each state/territory?
- Thresholds for mandatory human approval before issuing work orders or vendor communications?
