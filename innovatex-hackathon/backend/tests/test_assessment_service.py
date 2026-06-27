"""Unit tests for assessment_service.

The db Session is mocked; tenant_service and scoring_service are patched.
No real database connection is used. Payload construction adapts to whether
``AnswerUpsert`` is a flat model or a discriminated-union contract.
"""
import uuid as _uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.models.assessment import Assessment
from app.models.assessment_answer import AssessmentAnswer
from app.models.base import AssessmentStatusEnum, QuestionKindEnum
from app.schemas.assessment import (
    AssessmentCreate, AssessmentRead, AssessmentUpdate, AnswerRead,
)
from app.schemas import assessment as _schema
from app.services import assessment_service


USER_ID = str(_uuid.uuid4())
COMPANY_ID = str(_uuid.uuid4())
ASSESSMENT_ID = _uuid.uuid4()


def _payload(kind: str, *, question_id: str = "P2", **resp):
    """Build an answer payload adaptive to the schema contract.

    Prefers the discriminated-union subclass (GateAnswer/ScaleAnswer/
    ValidationAnswer) when present, falling back to flat AnswerUpsert. Only the
    single relevant response field is supplied so validity holds in both shapes.
    """
    cls_name = {"gate": "GateAnswer", "scale": "ScaleAnswer",
                "validation": "ValidationAnswer"}[kind]
    cls = getattr(_schema, cls_name, None) or _schema.AnswerUpsert
    kwargs = {"question_id": question_id, "kind": kind}
    kwargs.update(resp)
    return cls(**kwargs)


def _make_assessment(
    status: AssessmentStatusEnum = AssessmentStatusEnum.draft,
    overall_score: float | None = None,
) -> Assessment:
    a = Assessment(
        company_id=_uuid.UUID(COMPANY_ID),
        created_by=_uuid.UUID(USER_ID),
        status=status,
        overall_score=overall_score,
    )
    object.__setattr__(a, "id", ASSESSMENT_ID)
    object.__setattr__(a, "created_at", datetime(2025, 1, 1, tzinfo=timezone.utc))
    object.__setattr__(a, "updated_at", datetime(2025, 1, 1, tzinfo=timezone.utc))
    return a


def _make_answer(kind: QuestionKindEnum, question_id: str = "P2", **resp) -> AssessmentAnswer:
    ans = AssessmentAnswer(
        assessment_id=ASSESSMENT_ID,
        question_id=question_id,
        kind=kind,
        **resp,
    )
    object.__setattr__(ans, "answered_at", datetime(2025, 1, 2, tzinfo=timezone.utc))
    object.__setattr__(ans, "created_at", datetime(2025, 1, 2, tzinfo=timezone.utc))
    object.__setattr__(ans, "updated_at", datetime(2025, 1, 2, tzinfo=timezone.utc))
    return ans


# ── start_assessment ──────────────────────────────────────────────────────
class TestStartAssessment:
    def test_start_assessment_creates_draft(self):
        db = MagicMock()
        new_id = _uuid.uuid4()
        # Simulate DB/server populating server_default columns + PK on refresh.
        db.refresh.side_effect = lambda obj: (
            object.__setattr__(obj, "id", new_id),
            object.__setattr__(obj, "created_at", datetime(2025, 1, 1, tzinfo=timezone.utc)),
            object.__setattr__(obj, "updated_at", datetime(2025, 1, 1, tzinfo=timezone.utc)),
        )
        payload = AssessmentCreate(company_id=COMPANY_ID)

        with patch("app.services.assessment_service.tenant_service.assert_membership") as m:
            result = assessment_service.start_assessment(db, USER_ID, payload)

        m.assert_called_once()
        assert db.add.called
        db.flush.assert_called_once()
        db.commit.assert_called_once()
        assert isinstance(result, AssessmentRead)
        assert result.status == AssessmentStatusEnum.draft
        assert str(result.company_id) == COMPANY_ID
        added = db.add.call_args[0][0]
        assert isinstance(added.company_id, _uuid.UUID)
        assert isinstance(added.created_by, _uuid.UUID)

    def test_start_assessment_membership_denied(self):
        db = MagicMock()
        payload = AssessmentCreate(company_id=COMPANY_ID)

        with patch("app.services.assessment_service.tenant_service.assert_membership",
                   side_effect=ValueError("Not a member")):
            with pytest.raises(ValueError, match="Not a member"):
                assessment_service.start_assessment(db, USER_ID, payload)
        assert not db.add.called

    def test_start_assessment_invalid_company_id(self):
        db = MagicMock()
        payload = AssessmentCreate(company_id="not-a-uuid")
        with pytest.raises(ValueError):
            assessment_service.start_assessment(db, USER_ID, payload)


# ── get_assessment ─────────────────────────────────────────────────────────
class TestGetAssessment:
    def test_get_assessment_not_found(self):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q

        with pytest.raises(ValueError, match="Assessment not found"):
            assessment_service.get_assessment(db, str(ASSESSMENT_ID), USER_ID)

    def test_get_assessment_returns_with_answers(self):
        assessment = _make_assessment()
        a1 = _make_answer(QuestionKindEnum.scale, scale_resp=70)
        a2 = _make_answer(QuestionKindEnum.gate, question_id="P1", gate_resp=True)

        db = MagicMock()
        assessment_q = MagicMock()
        assessment_q.filter.return_value.first.return_value = assessment
        answers_q = MagicMock()
        answers_q.join.return_value = answers_q
        answers_q.filter.return_value = answers_q
        answers_q.order_by.return_value.all.return_value = [a1, a2]
        db.query.side_effect = [assessment_q, answers_q]

        with patch("app.services.assessment_service.tenant_service.assert_membership") as m:
            result = assessment_service.get_assessment(db, str(ASSESSMENT_ID), USER_ID)

        m.assert_called_once_with(db, assessment.company_id, USER_ID)
        assert isinstance(result, AssessmentRead)
        assert len(result.answers) == 2
        assert isinstance(result.answers[0], AnswerRead)

    def test_get_assessment_membership_denied(self):
        assessment = _make_assessment()
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = assessment
        db.query.return_value = q

        with patch("app.services.assessment_service.tenant_service.assert_membership",
                   side_effect=ValueError("Not a member")):
            with pytest.raises(ValueError, match="Not a member"):
                assessment_service.get_assessment(db, str(ASSESSMENT_ID), USER_ID)


# ── upsert_answer ──────────────────────────────────────────────────────────
class TestUpsertAnswer:
    def _db_with_assessment(self, assessment):
        db = MagicMock()
        aq = MagicMock()
        aq.filter.return_value.first.return_value = assessment
        db.query.return_value = aq
        return db

    def test_upsert_assessment_not_found(self):
        db = MagicMock()
        aq = MagicMock()
        aq.filter.return_value.first.return_value = None
        db.query.return_value = aq

        payload = _payload("scale", scale_resp=70)
        with pytest.raises(ValueError, match="Assessment not found"):
            assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

    def test_upsert_already_completed(self):
        assessment = _make_assessment(status=AssessmentStatusEnum.completed, overall_score=50)
        db = self._db_with_assessment(assessment)

        payload = _payload("scale", scale_resp=70)
        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            with pytest.raises(ValueError, match="Assessment already completed"):
                assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

    def test_upsert_membership_denied(self):
        assessment = _make_assessment()
        db = self._db_with_assessment(assessment)

        payload = _payload("scale", scale_resp=70)
        with patch("app.services.assessment_service.tenant_service.assert_membership",
                   side_effect=ValueError("Not a member")):
            with pytest.raises(ValueError, match="Not a member"):
                assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

    def test_upsert_inserts_new_scale_answer(self):
        assessment = _make_assessment()
        ans_q = MagicMock()
        ans_q.filter.return_value.first.return_value = None
        aq = MagicMock()
        aq.filter.return_value.first.return_value = assessment
        db = MagicMock()
        db.query.side_effect = [aq, ans_q]

        payload = _payload("scale", scale_resp=70)
        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            result = assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

        assert isinstance(result, AnswerRead)
        assert result.scale_resp == 70
        assert result.gate_resp is None
        assert result.validation_resp is None
        db.flush.assert_called_once()
        db.commit.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.scale_resp == 70
        assert added.gate_resp is None
        assert added.validation_resp is None
        assert added.question_id == "P2"

    def test_upsert_inserts_new_gate_answer(self):
        assessment = _make_assessment()
        ans_q = MagicMock()
        ans_q.filter.return_value.first.return_value = None
        aq = MagicMock()
        aq.filter.return_value.first.return_value = assessment
        db = MagicMock()
        db.query.side_effect = [aq, ans_q]

        payload = _payload("gate", question_id="P1", gate_resp=False)
        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            result = assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

        assert result.gate_resp is False
        assert result.scale_resp is None
        assert result.validation_resp is None

    def test_upsert_inserts_new_validation_answer(self):
        assessment = _make_assessment()
        ans_q = MagicMock()
        ans_q.filter.return_value.first.return_value = None
        aq = MagicMock()
        aq.filter.return_value.first.return_value = assessment
        db = MagicMock()
        db.query.side_effect = [aq, ans_q]

        payload = _payload("validation", question_id="P11", validation_resp=True)
        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            result = assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

        assert result.validation_resp is True
        assert result.scale_resp is None
        assert result.gate_resp is None

    def test_upsert_updates_existing_same_kind_scale(self):
        assessment = _make_assessment()
        existing = _make_answer(QuestionKindEnum.scale, scale_resp=35)
        ans_q = MagicMock()
        ans_q.filter.return_value.first.return_value = existing
        aq = MagicMock()
        aq.filter.return_value.first.return_value = assessment
        db = MagicMock()
        db.query.side_effect = [aq, ans_q]

        payload = _payload("scale", scale_resp=100, notes="updated")
        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            result = assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)

        assert result.scale_resp == 100
        assert existing.scale_resp == 100
        assert existing.gate_resp is None
        assert existing.validation_resp is None
        assert existing.notes == "updated"
        assert existing.answered_at is not None
        # Updated in place — no new row added.
        assert not db.add.called

    def test_upsert_existing_kind_mismatch_raises(self):
        assessment = _make_assessment()
        existing = _make_answer(QuestionKindEnum.gate, question_id="P2", gate_resp=True)
        ans_q = MagicMock()
        ans_q.filter.return_value.first.return_value = existing
        aq = MagicMock()
        aq.filter.return_value.first.return_value = assessment
        db = MagicMock()
        db.query.side_effect = [aq, ans_q]

        payload = _payload("scale", scale_resp=70)
        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            with pytest.raises(ValueError, match="kind"):
                assessment_service.upsert_answer(db, str(ASSESSMENT_ID), USER_ID, payload)
        db.flush.assert_not_called()


# ── update_assessment ──────────────────────────────────────────────────────
class TestUpdateAssessment:
    def _db_with_assessment(self, assessment):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = assessment
        db.query.return_value = q
        return db

    def test_update_not_found(self):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q

        with pytest.raises(ValueError, match="Assessment not found"):
            assessment_service.update_assessment(
                db, str(ASSESSMENT_ID), USER_ID,
                AssessmentUpdate(status=AssessmentStatusEnum.draft))

    def test_update_membership_denied(self):
        assessment = _make_assessment()
        db = self._db_with_assessment(assessment)

        with patch("app.services.assessment_service.tenant_service.assert_membership",
                   side_effect=ValueError("Not a member")):
            with pytest.raises(ValueError, match="Not a member"):
                assessment_service.update_assessment(
                    db, str(ASSESSMENT_ID), USER_ID,
                    AssessmentUpdate(status=AssessmentStatusEnum.completed))

    def test_update_complete_runs_scoring(self):
        assessment = _make_assessment()
        db = self._db_with_assessment(assessment)

        with patch("app.services.assessment_service.tenant_service.assert_membership"), \
             patch("app.services.scoring_service.compute_and_persist", return_value=75.0) as cs:
            result = assessment_service.update_assessment(
                db, str(ASSESSMENT_ID), USER_ID,
                AssessmentUpdate(status=AssessmentStatusEnum.completed))

        cs.assert_called_once_with(db, assessment)
        assert float(assessment.overall_score) == 75.0
        assert assessment.status == AssessmentStatusEnum.completed
        assert assessment.completed_at is not None
        db.commit.assert_called_once()
        assert isinstance(result, AssessmentRead)
        assert result.status == AssessmentStatusEnum.completed
        assert float(result.overall_score) == 75.0

    def test_update_complete_when_already_completed_raises(self):
        assessment = _make_assessment(
            status=AssessmentStatusEnum.completed, overall_score=55.0)
        db = self._db_with_assessment(assessment)

        with patch("app.services.assessment_service.tenant_service.assert_membership"):
            with pytest.raises(ValueError, match="already completed"):
                assessment_service.update_assessment(
                    db, str(ASSESSMENT_ID), USER_ID,
                    AssessmentUpdate(status=AssessmentStatusEnum.completed))

    def test_update_to_draft_keeps_status_no_scoring(self):
        assessment = _make_assessment()
        db = self._db_with_assessment(assessment)

        with patch("app.services.assessment_service.tenant_service.assert_membership"), \
             patch("app.services.scoring_service.compute_and_persist") as cs:
            result = assessment_service.update_assessment(
                db, str(ASSESSMENT_ID), USER_ID,
                AssessmentUpdate(status=AssessmentStatusEnum.draft))

        cs.assert_not_called()
        assert assessment.status == AssessmentStatusEnum.draft
        assert assessment.completed_at is None
        db.commit.assert_called_once()
        assert result.status == AssessmentStatusEnum.draft