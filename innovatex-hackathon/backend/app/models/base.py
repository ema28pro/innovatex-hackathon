"""Shared ORM foundation: enums, timestamp mixin, and Base re-export.

All model files import from here to avoid circular imports with database.py.
"""

import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum as SAEnum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ── Base (single source of truth for all models) ────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Enums ───────────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    admin = "admin"
    auditor = "auditor"
    reader = "reader"


class AssessmentStatusEnum(str, enum.Enum):
    draft = "draft"
    completed = "completed"


class QuestionKindEnum(str, enum.Enum):
    gate = "gate"              # P1 — Sí/No, controls Bloque 1
    scale = "scale"            # P2-P10 — 0/35/70/100 maturity scale
    validation = "validation"  # P11 — Sí/No, weight 0, audit-only


class PriorityEnum(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ActionItemStatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class ShareLinkStatusEnum(str, enum.Enum):
    active = "active"
    revoked = "revoked"
    expired = "expired"


# ── Mixin ───────────────────────────────────────────────────────────────────

class TimestampMixin:
    """Adds created_at + updated_at columns. Apply to all mutable tables."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
