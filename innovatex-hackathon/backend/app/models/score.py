"""Score — per-block normalized scoring for an assessment."""
import uuid as _uuid
from sqlalchemy import String, ForeignKey, Numeric, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Score(Base, TimestampMixin):
    __tablename__ = "scores"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    assessment_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    block_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("blocks.slug", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    score: Mapped[float] = mapped_column(
        Numeric(6, 2), nullable=False, default=0
    )
    max_score: Mapped[float] = mapped_column(
        Numeric(6, 2), nullable=False, default=0
    )
    percentage: Mapped[float] = mapped_column(
        Numeric(6, 3), nullable=False, default=0
    )

    __table_args__ = (
        UniqueConstraint("assessment_id", "block_id", name="uq_score_assessment_block"),
        Index("ix_scores_assessment_id", "assessment_id"),
        Index("ix_scores_block_id", "block_id"),
    )
