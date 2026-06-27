"""Pytest config shared by Phase 3 questions tests.

`BlockRead` and `QuestionRead` live in ``app.schemas.assessment`` and are
provided by "Agent A". If they are not present yet, we inject lightweight
Pydantic stand-ins INTO the real module (we never replace it, so Agent A's
other schemas keep working). Once Agent A ships the real classes, the
``hasattr`` guards short-circuit and the stubs are not applied.
"""
import os
import sys

# ── Make app.* importable when pytest is run from the backend dir ─────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from datetime import datetime  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from app.models.base import QuestionKindEnum  # noqa: E402


def _ensure_block_question_reads() -> None:
    """Add BlockRead / QuestionRead stubs to app.schemas.assessment if missing."""
    import app.schemas.assessment as schema  # noqa: PLC0415

    if not hasattr(schema, "BlockRead"):
        class BlockRead(BaseModel):
            slug: str
            title: str
            description: str | None = None
            weight: float
            order_num: int
            created_at: datetime
            updated_at: datetime

            model_config = {"from_attributes": True}

        schema.BlockRead = BlockRead

    if not hasattr(schema, "QuestionRead"):
        class QuestionRead(BaseModel):
            slug: str
            block_id: str
            kind: QuestionKindEnum
            text: str
            weight: float
            order_num: int
            gate_for: list | None = None

            model_config = {"from_attributes": True}

        schema.QuestionRead = QuestionRead


_ensure_block_question_reads()