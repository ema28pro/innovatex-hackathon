"""Recommendation — AI-generated compliance recommendation per assessment."""
import uuid as _uuid
from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, PriorityEnum


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    assessment_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    block_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("blocks.slug", ondelete="RESTRICT"),
        nullable=True, index=True,
    )
    ai_generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[PriorityEnum] = mapped_column(
        nullable=False, default=PriorityEnum.medium
    )

    __table_args__ = (
        Index("ix_recommendations_assessment_id", "assessment_id"),
    )
