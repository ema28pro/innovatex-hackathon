"""Scoring engine — computes per-block and overall compliance scores.

NOTE: Minimal stub for Agent D to flesh out. Provides compute_and_persist used
by assessment_service when an assessment is completed.
"""
from sqlalchemy.orm import Session


def compute_and_persist(db: Session, assessment) -> float:
    """Compute per-block scores, persist Score rows, return overall percentage.

    Stub implementation — Agent D replaces with real scoring logic.
    """
    raise NotImplementedError("scoring_service.compute_and_persist not yet implemented")