"""Company CRUD endpoints — Phase 2 onboarding API."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_required, UserPayload
from app.schemas.company import CompanyCreate, CompanyRead
from app.services import company_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[CompanyRead])
def list_companies(
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Return all companies the authenticated user belongs to."""
    return company_service.list_companies(db, user_id=user.user_id)


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create a new company and assign the creator as admin."""
    try:
        return company_service.create_company(
            db,
            user_id=user.user_id,
            email=user.email,
            payload=payload,
        )
    except Exception as exc:
        logger.exception("Failed to create company")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: str,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get a single company by ID. Returns 404 if not found or not a member."""
    try:
        return company_service.get_company(db, company_id, user_id=user.user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
