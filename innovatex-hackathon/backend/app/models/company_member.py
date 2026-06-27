"""CompanyMember — tenant-role join table."""
import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, RoleEnum


class CompanyMember(Base):
    __tablename__ = "company_members"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    company_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    profile_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    role: Mapped[RoleEnum] = mapped_column(nullable=False, default=RoleEnum.reader)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("company_id", "profile_id", name="uq_company_member"),
        Index("ix_company_members_company_id", "company_id"),
        Index("ix_company_members_profile_id", "profile_id"),
    )
