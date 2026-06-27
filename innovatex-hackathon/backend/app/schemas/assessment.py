"""Pydantic v2 schemas for Assessment & Answer endpoints."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from app.models.base import AssessmentStatusEnum, QuestionKindEnum


# ── Block / Question (Phase 3 read schemas — owned by this module) ─────────
class BlockRead(BaseModel):
    slug: str
    title: str
    description: str | None = None
    weight: float
    order_num: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionRead(BaseModel):
    slug: str
    block_id: str
    kind: QuestionKindEnum
    text: str
    weight: float
    order_num: int
    gate_for: list | None = None

    model_config = {"from_attributes": True}


# ── Answer ────────────────────────────────────────────────────────────────
class AnswerUpsert(BaseModel):
    """Payload for PUT/POST answer — exactly one response field must be set."""
    question_id: str = Field(..., min_length=1, max_length=10)
    kind: QuestionKindEnum
    scale_resp: int | None = Field(None)
    gate_resp: bool | None = Field(None)
    validation_resp: bool | None = Field(None)
    notes: str | None = Field(None, max_length=2000)

    @model_validator(mode="after")
    def _exactly_one_response(self):
        filled = sum(
            x is not None for x in
            (self.scale_resp, self.gate_resp, self.validation_resp)
        )
        if filled != 1:
            raise ValueError(
                "Exactly one of scale_resp / gate_resp / validation_resp must be set"
            )
        return self


class AnswerRead(BaseModel):
    assessment_id: UUID
    question_id: str
    kind: QuestionKindEnum
    scale_resp: int | None = None
    gate_resp: bool | None = None
    validation_resp: bool | None = None
    notes: str | None = None
    answered_at: datetime

    model_config = {"from_attributes": True}


# Typed discriminated answer variants (kept for forward-compat).
class ScaleAnswer(BaseModel):
    question_id: str = Field(..., max_length=10)
    kind: QuestionKindEnum = QuestionKindEnum.scale
    scale_resp: int = Field(..., ge=0, le=100)
    notes: str | None = Field(None, max_length=2000)


class GateAnswer(BaseModel):
    question_id: str = Field(..., max_length=10)
    kind: QuestionKindEnum = QuestionKindEnum.gate
    gate_resp: bool
    notes: str | None = Field(None, max_length=2000)


class ValidationAnswer(BaseModel):
    question_id: str = Field(..., max_length=10)
    kind: QuestionKindEnum = QuestionKindEnum.validation
    validation_resp: bool
    notes: str | None = Field(None, max_length=2000)


# ── Assessment ─────────────────────────────────────────────────────────────
class AssessmentCreate(BaseModel):
    company_id: str = Field(..., description="Company UUID string")


class AssessmentRead(BaseModel):
    id: UUID
    company_id: UUID
    created_by: UUID
    status: AssessmentStatusEnum
    overall_score: float | None = None
    completed_at: datetime | None = None
    created_at: datetime
    answers: list[AnswerRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class AssessmentUpdate(BaseModel):
    status: AssessmentStatusEnum | None = None
