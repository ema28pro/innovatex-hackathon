"""Idempotent seed runner — populates blocks + questions if empty.

Uses INSERT … ON CONFLICT DO NOTHING (safe for concurrent starts).
Called from entrypoint.sh after alembic upgrade head.
"""
import logging
from sqlalchemy.dialects.postgresql import insert
from app.database import SessionLocal
from app.models.block import Block
from app.models.question import Question
from app.seeds.data import BLOCKS, QUESTIONS

logger = logging.getLogger(__name__)

EXPECTED_BLOCKS = 3
EXPECTED_QUESTIONS = 11


def seed_if_empty() -> None:
    """Idempotent: inserts only if tables are empty. Safe for concurrent callers."""
    db = SessionLocal()
    try:
        # ── Blocks ──────────────────────────────────────────────────
        existing_blocks = db.query(Block).count()
        if existing_blocks == 0:
            logger.info("Seeding %d blocks…", EXPECTED_BLOCKS)
            for b in BLOCKS:
                db.execute(insert(Block).values(**b).on_conflict_do_nothing())
            db.commit()

            actual = db.query(Block).count()
            assert actual == EXPECTED_BLOCKS, (
                f"Expected {EXPECTED_BLOCKS} blocks, found {actual}"
            )
            logger.info("✅ Blocks seeded.")
        else:
            logger.info("Blocks already populated (%d rows). Skipping.", existing_blocks)

        # ── Questions ───────────────────────────────────────────────
        existing_q = db.query(Question).count()
        if existing_q == 0:
            logger.info("Seeding %d questions…", EXPECTED_QUESTIONS)
            for q in QUESTIONS:
                db.execute(insert(Question).values(**q).on_conflict_do_nothing())
            db.commit()

            actual_q = db.query(Question).count()
            assert actual_q == EXPECTED_QUESTIONS, (
                f"Expected {EXPECTED_QUESTIONS} questions, found {actual_q}"
            )
            logger.info("✅ Questions seeded.")
        else:
            logger.info("Questions already populated (%d rows). Skipping.", existing_q)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_if_empty()
