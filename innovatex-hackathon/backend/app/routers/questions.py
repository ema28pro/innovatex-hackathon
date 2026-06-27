"""Questions endpoints — Phase 3 read-only questionnaire API.

Mounted in main.py as:
    app.include_router(questions.router, prefix="/api", tags=["Questions"])
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_required, UserPayload
from app.schemas.assessment import BlockRead, QuestionRead
from app.services import question_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/blocks", response_model=list[BlockRead])
def list_blocks(
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Return all questionnaire blocks, ordered by order_num."""
    return question_service.list_blocks(db)


@router.get(
    "/blocks/{block_slug}/questions",
    response_model=list[QuestionRead],
)
def list_questions_by_block(
    block_slug: str,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Return all questions for a block, ordered by order_num."""
    try:
        return question_service.list_questions_by_block(db, block_slug)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )