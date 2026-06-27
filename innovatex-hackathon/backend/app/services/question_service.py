"""Question / Block read-only service — Phase 3 questions API.

Mirrors the company_service pattern: query SQLAlchemy models, map to the
Pydantic read schemas produced by Agent A (BlockRead, QuestionRead).
"""
import logging

from sqlalchemy.orm import Session

from app.models.block import Block
from app.models.question import Question
from app.schemas.assessment import BlockRead, QuestionRead

logger = logging.getLogger(__name__)


def list_blocks(db: Session) -> list[BlockRead]:
    """Return all questionnaire blocks ordered by order_num."""
    rows = (
        db.query(Block)
        .order_by(Block.order_num.asc())
        .all()
    )
    return [BlockRead.model_validate(b) for b in rows]


def list_questions_by_block(db: Session, block_slug: str) -> list[QuestionRead]:
    """Return all questions for a block, ordered by order_num.

    Raises ValueError("Block not found") if the block does not exist.
    """
    block = db.query(Block).filter(Block.slug == block_slug).first()
    if block is None:
        raise ValueError("Block not found")

    rows = (
        db.query(Question)
        .filter(Question.block_id == block_slug)
        .order_by(Question.order_num.asc())
        .all()
    )
    return [QuestionRead.model_validate(q) for q in rows]