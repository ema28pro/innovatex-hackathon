"""Company business logic — CRUD + onboarding with auto profile creation."""
import uuid as _uuid
import logging
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.profile import Profile
from app.models.base import RoleEnum
from app.schemas.company import CompanyCreate, CompanyRead

logger = logging.getLogger(__name__)


def _ensure_profile(db: Session, user_id: str, email: str) -> Profile:
    """Lazy-upsert: create a profile row from JWT data if it doesn't exist.

    This is the fallback for the Supabase Auth Hook (which runs in production
    but may be unavailable during local dev or if the hook fails).
    """
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if profile is None:
        profile = Profile(
            id=_uuid.UUID(user_id),
            email=email,
            full_name=None,
        )
        db.add(profile)
        db.flush()
        logger.info("Created profile for user %s", user_id)
    return profile


def list_companies(db: Session, user_id: str) -> list[CompanyRead]:
    """Return all companies the user is a member of."""
    rows = (
        db.query(Company)
        .join(CompanyMember, CompanyMember.company_id == Company.id)
        .filter(CompanyMember.profile_id == _uuid.UUID(user_id))
        .order_by(Company.created_at.desc())
        .all()
    )
    return [_company_to_read(c) for c in rows]


def create_company(
    db: Session, user_id: str, email: str, payload: CompanyCreate
) -> CompanyRead:
    """Create a company and assign the creator as admin.

    1. Ensure a profile row exists for the creator (lazy-upsert fallback).
    2. Insert the company row.
    3. Insert the admin membership row.
    All in one transaction.
    """
    # Ensure profile
    _ensure_profile(db, user_id, email)

    uid = _uuid.UUID(user_id)

    # Create company
    company = Company(
        name=payload.name,
        nit=payload.nit,
        sector=payload.sector,
        size=payload.size,
        contact_email=payload.contact_email,
        created_by=uid,
    )
    db.add(company)
    db.flush()  # get company.id

    # Assign creator as admin
    membership = CompanyMember(
        company_id=company.id,
        profile_id=uid,
        role=RoleEnum.admin,
    )
    db.add(membership)

    db.commit()
    db.refresh(company)
    logger.info("Company '%s' created by user %s", company.name, user_id)
    return _company_to_read(company)


def get_company(db: Session, company_id: str, user_id: str) -> CompanyRead:
    """Return a single company — caller must verify membership."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise ValueError("Company not found")
    return _company_to_read(company)


def _company_to_read(c: Company) -> CompanyRead:
    return CompanyRead(
        id=str(c.id),
        name=c.name,
        nit=c.nit,
        sector=c.sector,
        size=c.size,
        contact_email=c.contact_email,
        created_at=c.created_at,
    )
