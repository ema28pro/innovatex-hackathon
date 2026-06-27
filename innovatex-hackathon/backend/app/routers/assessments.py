"""Assessment endpoints — start, get, answer upsert, completion.

Mounted in main.py as:
    app.include_router(assessments.router, prefix="/api", tags=["Assessments"])

All ValueErrors from the service layer are mapped to HTTP here. Tenant
(IDOR) checks live inside the service via ``tenant_service.assert_membership``.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_required, UserPayload
from app.schemas.assessment import (
    AssessmentCreate, AssessmentRead, AssessmentUpdate,
    AnswerUpsert, AnswerRead,
)
from app.services import assessment_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/assessments", response_model=AssessmentRead,
             status_code=status.HTTP_201_CREATED)
def start_assessment(
    payload: AssessmentCreate,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    try:
        return assessment_service.start_assessment(db, user.user_id, payload)
    except ValueError as exc:
        msg = str(exc)
        code = 403 if "Forbidden" in msg else 400
        raise HTTPException(status_code=code, detail=msg)
    except Exception as exc:
        logger.exception("Failed to start assessment")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/assessments/{assessment_id}", response_model=AssessmentRead)
def get_assessment(
    assessment_id: str,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    try:
        return assessment_service.get_assessment(db, assessment_id, user.user_id)
    except ValueError as exc:
        msg = str(exc)
        code = 403 if "Forbidden" in msg else 404
        raise HTTPException(status_code=code, detail=msg)


@router.post(
    "/assessments/{assessment_id}/answers",
    response_model=AnswerRead,
)
def upsert_answer(
    assessment_id: str,
    payload: AnswerUpsert,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    try:
        return assessment_service.upsert_answer(
            db, assessment_id, user.user_id, payload)
    except ValueError as exc:
        msg = str(exc)
        # Contract mapping: 403 forbidden, 404 not found,
        # 409 already completed, 400 fallback.
        code = (
            403 if "Forbidden" in msg
            else 404 if "not found" in msg
            else 409 if "already completed" in msg
            else 400
        )
        raise HTTPException(status_code=code, detail=msg)
    except Exception as exc:
        logger.exception("Failed to upsert answer")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/assessments/{assessment_id}", response_model=AssessmentRead)
def update_assessment(
    assessment_id: str,
    payload: AssessmentUpdate,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    try:
        return assessment_service.update_assessment(
            db, assessment_id, user.user_id, payload)
    except ValueError as exc:
        msg = str(exc)
        # Contract mapping: 403 forbidden, 404 not found,
        # 409 already completed, 400 fallback.
        code = (
            403 if "Forbidden" in msg
            else 404 if "not found" in msg
            else 409 if "already completed" in msg
            else 400
        )
        raise HTTPException(status_code=code, detail=msg)
    except Exception as exc:
        logger.exception("Failed to update assessment")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
