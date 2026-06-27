"""Assessment business logic — start, fetch, answer upsert, completion.

All ValueErrors raised here are mapped to HTTP codes by the router layer.
Tenant membership is delegated to ``tenant_service`` (Agent E); per-block
scoring is delegated to ``scoring_service`` (Agent D, imported lazily at the
call site to avoid circular imports).

The Answer payload may arrive either as a flat ``AnswerUpsert`` or as a
discriminated-union subclass (``GateAnswer`` / ``ScaleAnswer`` /
``ValidationAnswer``). We read the response field via ``getattr`` so the same
code path works regardless of which schema variant the contract module ships.
"""
import logging
import uuid as _uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.assessment_answer import AssessmentAnswer
from app.models.base import QuestionKindEnum
from app.models.question import Question
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentRead,
    AssessmentUpdate,
    AnswerUpsert,
    AnswerRead,
)
from app.services import tenant_service

logger = logging.getLogger(__name__)


def _to_uuid(value) -> _uuid.UUID:
    """Coerce str|UUID -> UUID (raises ValueError on bad input)."""
    if isinstance(value, _uuid.UUID):
        return value
    return _uuid.UUID(str(value))


def start_assessment(
    db: Session, user_id: str, payload: AssessmentCreate
) -> AssessmentRead:
    """Create a new draft assessment for the given company.

    Raises ValueError if the caller is not a member of the company or if
    company_id is not a valid UUID.
    """
    company_id = _to_uuid(payload.company_id)
    uid = _uuid.UUID(str(user_id))

    tenant_service.assert_membership(db, company_id, user_id)

    assessment = Assessment(
        company_id=company_id,
        created_by=uid,
        status="draft",
    )
    db.add(assessment)
    db.flush()
    db.refresh(assessment)
    db.commit()
    logger.info("Assessment created for company %s by user %s", company_id, user_id)
    return AssessmentRead.model_validate(assessment)


def get_assessment(
    db: Session, assessment_id, user_id: str
) -> AssessmentRead:
    """Fetch a single assessment with its answers, ordered by question order_num.

    Raises ValueError if the assessment does not exist or the user is not a
    member of the assessment's company.
    """
    aid = _to_uuid(assessment_id)

    assessment = db.query(Assessment).filter(Assessment.id == aid).first()
    if assessment is None:
        raise ValueError("Assessment not found")

    tenant_service.assert_membership(db, assessment.company_id, user_id)

    answers = (
        db.query(AssessmentAnswer)
        .join(Question, Question.slug == AssessmentAnswer.question_id)
        .filter(AssessmentAnswer.assessment_id == assessment.id)
        .order_by(Question.order_num)
        .all()
    )
    # The Assessment model defines no relationship; attach answers dynamically
    # so the read model can serialize them.
    assessment.answers = answers

    return AssessmentRead.model_validate(assessment)


def upsert_answer(
    db: Session, assessment_id, user_id: str, payload: AnswerUpsert
) -> AnswerRead:
    """Insert or update a single answer row (one row per assessment+question).

    Raises ValueError if the assessment is missing/already completed, the user
    is not a member, or an existing answer's question kind conflicts with the
    payload kind.
    """
    aid = _to_uuid(assessment_id)

    assessment = db.query(Assessment).filter(Assessment.id == aid).first()
    if assessment is None:
        raise ValueError("Assessment not found")

    tenant_service.assert_membership(db, assessment.company_id, user_id)

    if assessment.status == "completed":
        raise ValueError("Assessment already completed")

    existing = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.question_id == payload.question_id,
        )
        .first()
    )

    if existing is not None and existing.kind != payload.kind:
        raise ValueError(
            f"Answer for question {payload.question_id} already exists with kind "
            f"'{existing.kind.value}' — cannot change to '{payload.kind.value}'"
        )

    if existing is not None:
        answer = existing
    else:
        answer = AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=payload.question_id,
            kind=payload.kind,
        )

    # Polymorphic UPSERT: set the correct column, null the other two.
    # Read response fields via getattr so this works whether AnswerUpsert is a
    # flat model or a discriminated-union subclass with only one resp field.
    answer.scale_resp = getattr(payload, "scale_resp", None)
    answer.gate_resp = getattr(payload, "gate_resp", None)
    answer.validation_resp = getattr(payload, "validation_resp", None)

    answer.notes = payload.notes
    answer.answered_at = datetime.now(timezone.utc)

    if existing is None:
        db.add(answer)

    db.flush()
    db.commit()
    return AnswerRead.model_validate(answer)


def update_assessment(
    db: Session, assessment_id, user_id: str, payload: AssessmentUpdate,
    background_tasks=None,
) -> AssessmentRead:
    """Update an assessment — primarily used to transition draft -> completed.

    When status == "completed", runs the scoring engine, persists per-block
    scores, and stamps overall_score / completed_at.

    Raises ValueError if the assessment is missing, the user is not a member,
    or completion is attempted when already completed.
    """
    aid = _to_uuid(assessment_id)

    assessment = db.query(Assessment).filter(Assessment.id == aid).first()
    if assessment is None:
        raise ValueError("Assessment not found")

    tenant_service.assert_membership(db, assessment.company_id, user_id)

    if payload.status == "completed":
        if assessment.status == "completed":
            raise ValueError("Assessment already completed")

        # Lazy import to avoid a circular dependency with scoring_service.
        from app.services import scoring_service

        overall_pct = scoring_service.compute_and_persist(db, assessment)
        assessment.overall_score = overall_pct
        assessment.completed_at = datetime.now(timezone.utc)
        assessment.status = "completed"

        # Enqueue AI recommendation generation as background task
        if background_tasks is not None:
            from app.ai.recommendation_pipeline import generate_recommendations_for_assessment
            background_tasks.add_task(
                generate_recommendations_for_assessment, str(assessment.id)
            )
    elif payload.status is not None:
        assessment.status = payload.status

    db.commit()
    db.refresh(assessment)
    # Ensure the answers attribute exists for the read model (no relationship).
    if not hasattr(assessment, "answers"):
        assessment.answers = []
    return AssessmentRead.model_validate(assessment)