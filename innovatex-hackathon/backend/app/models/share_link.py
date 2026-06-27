"""ShareLink — expiring token-based assessment result sharing."""
import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, ShareLinkStatusEnum


class ShareLink(Base):
    __tablename__ = "share_links"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    assessment_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    token: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, default=_uuid.uuid4, index=True
    )
    created_by: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[ShareLinkStatusEnum] = mapped_column(
        nullable=False, default=ShareLinkStatusEnum.active
    )
    view_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_share_links_token", "token"),
        Index("ix_share_links_assessment_id", "assessment_id"),
    )
