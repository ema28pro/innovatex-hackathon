"""Pydantic v2 schemas for Company endpoints."""
from datetime import datetime
from pydantic import BaseModel, Field


# ── Create ────────────────────────────────────────────────────────────────
class CompanyCreate(BaseModel):
    """Payload for POST /api/companies (onboarding)."""
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    nit: str = Field(..., min_length=1, max_length=20, description="Colombian tax ID")
    sector: str | None = Field(None, max_length=100)
    size: str | None = Field(None, max_length=50)
    contact_email: str | None = Field(None, max_length=255)


# ── Read ──────────────────────────────────────────────────────────────────
class CompanyRead(BaseModel):
    """Response for GET /api/companies and GET /api/companies/{id}."""
    id: str
    name: str
    nit: str
    sector: str | None = None
    size: str | None = None
    contact_email: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
