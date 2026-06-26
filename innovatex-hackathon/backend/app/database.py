"""SQLAlchemy engine and session configuration.

Path B (Phase 2): Two engines — direct connection for Alembic DDL,
pooler connection for FastAPI runtime queries via Supabase PgBouncer.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

# ── Direct connection (for Alembic migrations / DDL) ──────────────────────
# PgBouncer in transaction mode can break DDL; use the direct Supabase endpoint.
if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required (direct Supabase connection)")

engine_direct = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=2,          # only Alembic uses this — keep it small
    max_overflow=3,
)

# ── Pooler connection (for FastAPI runtime) ────────────────────────────────
# Uses Supabase's PgBouncer pooler on port 6543 for efficient connection reuse.
_pooler_url = settings.DATABASE_URL_POOLER or settings.DATABASE_URL

engine_pooler = create_engine(
    _pooler_url,
    pool_pre_ping=True,
    pool_recycle=280,
    pool_size=10,
    max_overflow=20,
    connect_args={"prepare_threshold": None},  # Supavisor transaction mode disables prepared stmts
)

# ── Session factories ──────────────────────────────────────────────────────
SessionLocalDirect = sessionmaker(autocommit=False, autoflush=False, bind=engine_direct)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_pooler)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_db():
    """FastAPI dependency that provides a database session via the pooler."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
