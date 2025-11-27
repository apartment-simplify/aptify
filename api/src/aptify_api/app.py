"""FastAPI application wiring together feature routers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    analytics,
    communications,
    documents,
    email,
    feedback,
    intake,
    knowledge,
    leasing,
    maintenance,
    owners,
    payments,
    tenants,
    vendors,
)

from aptify_api.utils.init_vector_db import initialize_vectorstore

app = FastAPI(
    title="Aptify Property Management Platform",
    description=(
        "Implements the AI-enhanced workflows described in docs/ and powers the "
        "Aptify UI prototype. The API exposes modular routers for email triage, "
        "tenant lifecycle, leasing, payments, maintenance, vendor operations, "
        "document intelligence, analytics, and knowledge retrieval."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def load_vector_db():
    global retriever
    retriever = initialize_vectorstore()


app.include_router(email.router)
app.include_router(feedback.router)
app.include_router(intake.router)
app.include_router(tenants.router)
app.include_router(communications.router)
app.include_router(leasing.router)
app.include_router(payments.router)
app.include_router(maintenance.router)
app.include_router(vendors.router)
app.include_router(owners.router)
app.include_router(documents.router)
app.include_router(knowledge.router)
app.include_router(analytics.router)


@app.get("/health")
def healthcheck() -> dict:
    """Simple health probe for monitoring."""
    return {"status": "ok"}
