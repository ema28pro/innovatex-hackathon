"""ActionItem — actionable task derived from a recommendation."""
import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, ActionItemStatusEnum


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    recommendation_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    assessment_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[ActionItemStatusEnum] = mapped_column(
        nullable=False, default=ActionItemStatusEnum.pending
    )
    assigned_to: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_action_items_recommendation_id", "recommendation_id"),
        Index("ix_action_items_assessment_id", "assessment_id"),
        Index("ix_action_items_assigned_to", "assigned_to"),
    )
