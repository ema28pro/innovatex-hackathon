"""CompanyMember model — associates a profile with a company and role."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, RoleEnum


class CompanyMember(Base):
    __tablename__ = "company_members"
    __table_args__ = (
        UniqueConstraint("company_id", "profile_id", name="uq_company_member"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role: Mapped[RoleEnum] = mapped_column(
        SAEnum(RoleEnum), nullable=False, default=RoleEnum.reader
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
