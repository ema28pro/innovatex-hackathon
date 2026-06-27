"""AssessmentAnswer model — polymorphic answer row (gate/scale/validation) tied to an assessment and question."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, QuestionKindEnum, TimestampMixin


class AssessmentAnswer(Base, TimestampMixin):
    __tablename__ = "assessment_answers"
    __table_args__ = (
        CheckConstraint(
            "scale_resp IS NULL OR scale_resp IN (0, 35, 70, 100)",
            name="ck_scale_resp_values",
        ),
        CheckConstraint(
            "(kind='gate' AND gate_resp IS NOT NULL AND scale_resp IS NULL AND validation_resp IS NULL) OR "
            "(kind='scale' AND scale_resp IS NOT NULL AND gate_resp IS NULL AND validation_resp IS NULL) OR "
            "(kind='validation' AND validation_resp IS NOT NULL AND scale_resp IS NULL AND gate_resp IS NULL)",
            name="ck_answer_one_kind",
        ),
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
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
    kind: Mapped[QuestionKindEnum] = mapped_column(
        SAEnum(QuestionKindEnum), nullable=False
    )
    scale_resp: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    gate_resp: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    validation_resp: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
