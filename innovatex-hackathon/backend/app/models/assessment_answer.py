"""AssessmentAnswer — polymorphic answer row. One row per (assessment, question).

Gate (P1)       → gate_resp populated (bool: Sí/No)
Scale (P2–P10)  → scale_resp populated (0/35/70/100)
Validation (P11)→ validation_resp populated (bool: Sí/No)

Exactly one response column is non-null per row, enforced by CHECK constraint.
"""
import uuid as _uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Boolean, SmallInteger, ForeignKey,
    CheckConstraint, DateTime, func, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, QuestionKindEnum


class AssessmentAnswer(Base, TimestampMixin):
    __tablename__ = "assessment_answers"

    assessment_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("questions.slug", ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    )
    kind: Mapped[QuestionKindEnum] = mapped_column(nullable=False)

    # Polymorphic response columns — exactly one is non-null per row
    scale_resp: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True,
    )
    gate_resp: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    validation_resp: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "scale_resp IS NULL OR scale_resp IN (0, 35, 70, 100)",
            name="ck_scale_resp_valid",
        ),
        CheckConstraint(
            "(kind = 'gate'        AND gate_resp IS NOT NULL AND scale_resp IS NULL AND validation_resp IS NULL) OR "
            "(kind = 'scale'       AND scale_resp IS NOT NULL AND gate_resp IS NULL AND validation_resp IS NULL) OR "
            "(kind = 'validation'  AND validation_resp IS NOT NULL AND scale_resp IS NULL AND gate_resp IS NULL)",
            name="ck_answer_one_kind",
        ),
        Index("ix_assessment_answers_assessment_id", "assessment_id"),
        Index("ix_assessment_answers_question_id", "question_id"),
    )
