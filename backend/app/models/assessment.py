"""Assessment model — represents a company evaluation/diagnostic session."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AssessmentStatusEnum, Base, TimestampMixin


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "status != 'completed' OR overall_score IS NOT NULL",
            name="ck_completed_has_score",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[AssessmentStatusEnum] = mapped_column(
        SAEnum(AssessmentStatusEnum),
        nullable=False,
        default=AssessmentStatusEnum.draft,
    )
    overall_score: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
