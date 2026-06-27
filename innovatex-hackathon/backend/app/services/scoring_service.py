"""Scoring engine — Phase 4/6 backend scoring.

Mirrors the frontend ``lib/scoring.ts`` algorithm exactly so that the
overall percentage and per-block percentages match what the UI shows.

Algorithm (per Cuestionario):
- Gate (P1) and validation (P11) questions carry weight 0 and never move
  the score. The gate's effect (P2-P5 forced to 0) is already persisted as
  ``scale_resp = 0`` answers by the frontend store, so the raw computation
  naturally reflects it — no special-casing needed here.
- Scale questions (P2-P10): each contributes ``(scale / 100) * weight`` to
  ``obtained`` and ``weight`` to ``maxPossible``.
- Global % = ``(totalObtained / maxPossible) * 100``.
- Maturity bands: 0-39 Crítico, 40-69 Básico, 70-89 Avanzado, 90-100
  Optimizado.
"""
from __future__ import annotations

import logging
import uuid as _uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.assessment_answer import AssessmentAnswer
from app.models.block import Block
from app.models.question import Question
from app.models.score import Score
from app.models.base import QuestionKindEnum

logger = logging.getLogger(__name__)


# ── Maturity matrix (matches frontend) ────────────────────────────────────
MATURITY_BANDS = [
    (40, "critico", "Nivel Crítico (Riesgo Alto)"),
    (70, "basico", "Nivel Básico (Cumplimiento Reactivo)"),
    (90, "avanzado", "Nivel Avanzado (Cumplimiento Proactivo)"),
    (101, "optimizado", "Nivel Optimizado (Liderazgo en Privacidad)"),
]


def maturity_for(pct: float) -> tuple[str, str]:
    """Return (level, label) for a percentage value."""
    n = round(pct, 3)
    for threshold, level, label in MATURITY_BANDS:
        if n < threshold:
            return level, label
    return "optimizado", "Nivel Optimizado (Liderazgo en Privacidad)"


@dataclass
class BlockResult:
    block_id: str
    title: str
    weight: float
    score: float          # obtained raw points
    max_score: float      # max possible raw points for this block
    percentage: float     # 0-100 within block


@dataclass
class ScoreResult:
    overall_percentage: float
    maturity_level: str
    maturity_label: str
    blocks: list[BlockResult] = field(default_factory=list)


def _round2(n: float) -> float:
    return round(n * 100) / 100


def compute(
    answers: list[AssessmentAnswer],
    questions: list[Question],
    blocks: list[Block],
) -> ScoreResult:
    """Pure function — compute scores from answer/question/block rows.

    Each ``Block`` and ``Question`` is keyed by slug. Only scale questions
    move the score; gate/validation carry zero weight.
    """
    blocks_by_slug = {b.slug: b for b in blocks}
    questions_by_slug = {q.slug: q for q in questions}
    answer_by_q = {a.question_id: a for a in answers}

    obtained_by_block: dict[str, float] = {b.slug: 0.0 for b in blocks}
    max_by_block: dict[str, float] = {b.slug: 0.0 for b in blocks}
    total_obtained = 0.0
    total_max = 0.0

    for q in questions:
        if q.kind != QuestionKindEnum.scale:
            continue
        weight = float(q.weight)
        max_by_block[q.block_id] = max_by_block.get(q.block_id, 0.0) + weight
        total_max += weight
        ans = answer_by_q.get(q.slug)
        if ans is not None and ans.scale_resp is not None:
            pts = (float(ans.scale_resp) / 100.0) * weight
            obtained_by_block[q.block_id] = obtained_by_block.get(q.block_id, 0.0) + pts
            total_obtained += pts

    block_results: list[BlockResult] = []
    for b in blocks:
        mx = max_by_block.get(b.slug, 0.0)
        ob = obtained_by_block.get(b.slug, 0.0)
        pct = _round2((ob / mx) * 100) if mx > 0 else 0.0
        block_results.append(
            BlockResult(
                block_id=b.slug,
                title=b.title,
                weight=float(b.weight),
                score=_round2(ob),
                max_score=_round2(mx),
                percentage=pct,
            )
        )

    overall = _round2((total_obtained / total_max) * 100) if total_max > 0 else 0.0
    level, label = maturity_for(overall)
    return ScoreResult(
        overall_percentage=overall,
        maturity_level=level,
        maturity_label=label,
        blocks=block_results,
    )


def compute_and_persist(db: Session, assessment: Assessment) -> float:
    """Compute scores, persist one ``Score`` row per block, return overall %.

    Called by ``assessment_service.update_assessment`` on completion. Any
    stale Score rows for this assessment are deleted first so the operation
    is idempotent (re-completing a draft is a no-op due to the status guard,
    but a manual re-score is safe).
    """
    questions = (
        db.query(Question).order_by(Question.order_num).all()
    )
    blocks = db.query(Block).order_by(Block.order_num).all()
    answers = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.assessment_id == assessment.id)
        .all()
    )

    result = compute(answers, questions, blocks)

    # Idempotency: clear existing rows, then insert fresh.
    db.query(Score).filter(Score.assessment_id == assessment.id).delete(
        synchronize_session=False
    )
    for br in result.blocks:
        db.add(
            Score(
                assessment_id=assessment.id,
                block_id=br.block_id,
                score=br.score,
                max_score=br.max_score,
                percentage=br.percentage,
            )
        )
    db.flush()
    logger.info(
        "Scored assessment %s: overall=%.2f%% maturity=%s",
        assessment.id, result.overall_percentage, result.maturity_level,
    )
    return result.overall_percentage


def load_result(db: Session, assessment: Assessment) -> ScoreResult:
    """Rebuild a ScoreResult for read-only views.

    Prefers freshly-computed values (so reports reflect current answers even
    before persistence), but the stored ``overall_score``/``completed_at`` on
    the assessment are authoritative for the global percentage once
    completed.
    """
    questions = (
        db.query(Question).order_by(Question.order_num).all()
    )
    blocks = db.query(Block).order_by(Block.order_num).all()
    answers = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.assessment_id == assessment.id)
        .all()
    )
    result = compute(answers, questions, blocks)
    # If completed, prefer the persisted overall_score oracle.
    if assessment.overall_score is not None:
        result.overall_percentage = float(assessment.overall_score)
        level, label = maturity_for(result.overall_percentage)
        result.maturity_level = level
        result.maturity_label = label
    return result
