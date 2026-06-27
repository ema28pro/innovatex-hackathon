"""Assessment — compliance diagnostic evaluation."""
import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, AssessmentStatusEnum


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    company_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    created_by: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    status: Mapped[AssessmentStatusEnum] = mapped_column(
        nullable=False, default=AssessmentStatusEnum.draft
    )
    overall_score: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True,
        comment="Final compliance percentage — set when status=completed"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None,
        comment="Set explicitly at completion time — NO server default"
    )

    __table_args__ = (
        CheckConstraint(
            "status != 'completed' OR overall_score IS NOT NULL",
            name="ck_completed_has_score",
        ),
        Index("ix_assessments_company_id", "company_id"),
        Index("ix_assessments_created_by", "created_by"),
    )
