"""Pydantic v2 schemas for Report generation & Share Links."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.base import ShareLinkStatusEnum, PriorityEnum


# ── Report Data ──────────────────────────────────────────────────────────

class BlockScoreRead(BaseModel):
    block_slug: str
    block_title: str
    score: float
    max_score: float
    percentage: float

    model_config = {"from_attributes": True}


class ScoreSummary(BaseModel):
    overall_percentage: float
    maturity_level: str
    maturity_label: str
    blocks: list[BlockScoreRead] = Field(default_factory=list)


class QuestionAnswerRead(BaseModel):
    question_slug: str
    question_text: str
    block_slug: str
    kind: str
    answer_value: str | None = None  # human-readable
    scale_resp: int | None = None
    gate_resp: bool | None = None
    validation_resp: bool | None = None
    notes: str | None = None


class RecommendationRead(BaseModel):
    id: UUID
    block_id: str | None
    ai_generated_text: str
    priority: PriorityEnum

    model_config = {"from_attributes": True}


class ActionItemRead(BaseModel):
    id: UUID
    title: str
    status: str
    notes: str | None

    model_config = {"from_attributes": True}


class ReportData(BaseModel):
    """Full data needed to render a PDF/Excel report."""
    company_name: str
    company_nit: str
    company_sector: str | None = None
    company_size: str | None = None
    assessment_id: UUID
    assessment_status: str
    completed_at: datetime | None = None
    scores: ScoreSummary
    answers: list[QuestionAnswerRead] = Field(default_factory=list)
    recommendations: list[RecommendationRead] = Field(default_factory=list)
    action_items: list[ActionItemRead] = Field(default_factory=list)
    generated_at: datetime


# ── Share Link ───────────────────────────────────────────────────────────

class ShareLinkCreate(BaseModel):
    expires_in_hours: int = Field(default=168, ge=1, le=8760,  # 1h — 365d
                                  description="Hours until the share link expires")


class ShareLinkRead(BaseModel):
    id: UUID
    assessment_id: UUID
    token: str
    expires_at: datetime
    status: ShareLinkStatusEnum
    view_count: int
    created_at: datetime
    url: str

    model_config = {"from_attributes": True}


class SharedReportView(BaseModel):
    """Public read-only payload served at GET /share/{token}."""
    company_name: str
    assessment_status: str
    completed_at: datetime | None
    scores: ScoreSummary
    action_items: list[ActionItemRead] = Field(default_factory=list)
    expires_at: datetime
    view_count: int
