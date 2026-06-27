"""Tests for Phase 3 assessment schemas."""
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import BaseModel, ValidationError

from app.schemas.assessment import (
    AnswerRead,
    AnswerUpsert,
    AssessmentCreate,
    AssessmentRead,
    AssessmentUpdate,
    BlockRead,
    GateAnswer,
    QuestionRead,
    ScaleAnswer,
    ValidationAnswer,
)


# ── BlockRead ─────────────────────────────────────────────────────────────
class _BlockORM:
    """Mimics the SQLAlchemy model row with attribute access."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_block_read_from_attributes_decimal_coerced_to_float():
    row = _BlockORM(
        slug="govern",
        title="Gobernanza",
        description=None,
        weight=Decimal("25.00"),
        order_num=1,
        created_at=datetime(2025, 1, 1, 0, 0, 0),
        updated_at=datetime(2025, 1, 2, 0, 0, 0),
    )
    obj = BlockRead.model_validate(row)
    assert obj.slug == "govern"
    assert obj.weight == 25.0
    assert isinstance(obj.weight, float)
    assert obj.order_num == 1
    assert obj.description is None


def test_block_read_rejects_missing_updated_at():
    with pytest.raises(ValidationError):
        BlockRead(
            slug="govern",
            title="Gobernanza",
            weight=25.0,
            order_num=1,
            created_at=datetime(2025, 1, 1),
        )


# ── QuestionRead ──────────────────────────────────────────────────────────
def test_question_read_with_gate_for_list():
    obj = QuestionRead(
        slug="q1",
        block_id="govern",
        kind="gate",
        text="¿Tiene política?",
        weight=10.0,
        order_num=1,
        gate_for=["govern", "risk"],
    )
    assert obj.gate_for == ["govern", "risk"]


def test_question_read_rejects_invalid_kind():
    with pytest.raises(ValidationError):
        QuestionRead(
            slug="q1",
            block_id="govern",
            kind="nonsense",
            text="x",
            weight=1.0,
            order_num=1,
        )


# ── Discriminated union AnswerUpsert ──────────────────────────────────────
class _Wrapper(BaseModel):
    answer: AnswerUpsert


def test_answer_upsert_dispatches_gate():
    w = _Wrapper.model_validate({"answer": {"question_id": "q1", "kind": "gate", "gate_resp": True}})
    assert isinstance(w.answer, GateAnswer)
    assert w.answer.gate_resp is True
    assert w.answer.notes is None


def test_answer_upsert_dispatches_scale():
    w = _Wrapper.model_validate({"answer": {"question_id": "q2", "kind": "scale", "scale_resp": 70}})
    assert isinstance(w.answer, ScaleAnswer)
    assert w.answer.scale_resp == 70


def test_answer_scale_rejects_off_ladder_value():
    with pytest.raises(ValidationError):
        ScaleAnswer(question_id="q2", kind="scale", scale_resp=50)


def test_answer_upsert_dispatches_validation():
    w = _Wrapper.model_validate(
        {"answer": {"question_id": "q3", "kind": "validation", "validation_resp": False, "notes": "ok"}}
    )
    assert isinstance(w.answer, ValidationAnswer)
    assert w.answer.validation_resp is False
    assert w.answer.notes == "ok"


def test_answer_upsert_unknown_kind_rejected():
    with pytest.raises(ValidationError):
        _Wrapper.model_validate({"answer": {"question_id": "q1", "kind": "nope", "gate_resp": True}})


def test_gate_answer_missing_resp_rejected():
    with pytest.raises(ValidationError):
        GateAnswer(question_id="q1", kind="gate")


# ── AnswerRead ────────────────────────────────────────────────────────────
def test_answer_read_from_attributes():
    row = _BlockORM(
        question_id="q1",
        kind="gate",
        scale_resp=None,
        gate_resp=True,
        validation_resp=None,
        notes="ok",
        answered_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    obj = AnswerRead.model_validate(row)
    assert obj.gate_resp is True
    assert obj.answered_at == datetime(2025, 1, 1, 12, 0, 0)


# ── AssessmentCreate / Read / Update ──────────────────────────────────────
def test_assessment_create_requires_company_id():
    with pytest.raises(ValidationError):
        AssessmentCreate()


def test_assessment_read_with_answers_default_empty():
    obj = AssessmentRead(
        id="abc",
        company_id="c1",
        created_by="u1",
        status="draft",
        overall_score=None,
        completed_at=None,
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 1),
    )
    assert obj.answers == []


def test_assessment_read_completed_with_score_and_answers():
    obj = AssessmentRead(
        id="abc",
        company_id="c1",
        created_by="u1",
        status="completed",
        overall_score=82.5,
        completed_at=datetime(2025, 1, 2, 0, 0, 0),
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 2),
        answers=[
            AnswerRead(question_id="q1", kind="gate", gate_resp=True, answered_at=datetime(2025, 1, 1)),
        ],
    )
    assert obj.overall_score == 82.5
    assert len(obj.answers) == 1
    assert obj.answers[0].gate_resp is True


def test_assessment_read_rejects_invalid_status():
    with pytest.raises(ValidationError):
        AssessmentRead(
            id="x", company_id="c", created_by="u",
            status="pending",
            overall_score=None, completed_at=None,
            created_at=datetime(2025, 1, 1), updated_at=datetime(2025, 1, 1),
        )


def test_assessment_read_uuid_as_str_roundtrip():
    obj = AssessmentRead(
        id="55e7b4c2-7d3e-4f6a-9b0c-2d1e3f4a5b6c",
        company_id="c1",
        created_by="u1",
        status="draft",
        overall_score=None,
        completed_at=None,
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 1),
    )
    dumped = obj.model_dump()
    assert isinstance(dumped["id"], str)
    assert dumped["id"] == "55e7b4c2-7d3e-4f6a-9b0c-2d1e3f4a5b6c"


def test_assessment_update_defaults_none():
    obj = AssessmentUpdate()
    assert obj.status is None


def test_assessment_update_rejects_invalid_status():
    with pytest.raises(ValidationError):
        AssessmentUpdate(status="archived")


def test_assessment_update_accepts_both_statuses():
    assert AssessmentUpdate(status="draft").status == "draft"
    assert AssessmentUpdate(status="completed").status == "completed"