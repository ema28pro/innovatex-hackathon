"""Recommendation model — AI-generated recommendation tied to an assessment, optionally scoped to a block."""

import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, PriorityEnum, TimestampMixin


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    block_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("blocks.slug", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    ai_generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[PriorityEnum] = mapped_column(
        SAEnum(PriorityEnum), nullable=False, default=PriorityEnum.medium
    )
