## Feature Overview
Establish a structured information extraction service that transforms unstructured tenant communications into validated entities powering tickets, work orders, and analytics while maintaining human oversight.

## Target Users
- Property Management Assistants ingesting emails and calls.
- Maintenance Coordinators relying on accurate ticket data.
- Data Quality Analysts monitoring governance.

## Key Functional Requirements
1. **Multi-source Ingestion**
   - Support email parsing, file attachments, voice transcripts, and portal submissions.
   - Detect language, sentiment, and channel metadata.
2. **Entity & Attribute Extraction**
   - Capture tenant name, property address, issue category, severity, SLA, sentiment, attachments, access constraints.
   - Provide editable structured output prior to commit.
3. **Confidence Scoring & Flagging**
   - Assign confidence per field; route low-confidence results to manual review queues.
4. **Validation & Guardrails**
   - Apply business rules (e.g., address matches known property, SLA aligned to issue type) before persisting.
5. **Feedback Loop Management**
   - Allow users to correct fields; store corrections for model retraining and audit.

## AI Enhancements
- **Fine-tuned Extraction Models**: Custom NER/classification tuned for Australian property jargon.
- **Heuristic + ML Ensemble**: Combine ML outputs with rule validation to improve accuracy.
- **Continuous Learning**: Reinforce models with labelled corrections and active learning sampling.
- **Sentiment & Urgency Detection**: Inform prioritisation and escalation workflows.
- **Explainability Layer**: Highlight text spans supporting each extracted field to build trust.

## User Flows
1. Email arrives → Extraction pipeline runs → Results presented in review panel → User confirms → Ticket created.
2. Voice call recorded → Speech-to-text transcript generated → Entities extracted → Low-confidence fields flagged → Assistant edits prior to save.
3. Batch import via CSV → System parses rows → Validates against schema → Exceptions routed to remediation queue.
4. Correction submitted → Feedback stored → Data scientist reviews → Model retraining scheduled.
5. Audit request → Reviewer downloads extraction log with original text, extracted fields, confidence, approver.

## Success Metrics
- Achieve ≥90% extraction F1 score on key fields.
- Reduce manual data entry time by 50% for intake tasks.
- Keep exception queue volume below 10% of total ingestions.
- Provide traceable extraction logs for 100% of processed records.
- Improve downstream SLA compliance by 15% via faster accurate intake.

## Future Enhancements
- Real-time address validation with geocoding APIs.
- Multilingual extraction support.
- Automated summarisation for long transcripts.
- Smart attachment parsing (images/videos) for additional context.
- Adaptive confidence thresholds per customer based on tolerance.
