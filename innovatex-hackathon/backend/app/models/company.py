"""Company — multi-tenant root entity."""
import uuid as _uuid
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    nit: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False, index=True,
        comment="Creator = owner for MVP (ownership transfer deferred)"
    )

    __table_args__ = (
        Index("ix_companies_nit", "nit"),
        Index("ix_companies_created_by", "created_by"),
    )
