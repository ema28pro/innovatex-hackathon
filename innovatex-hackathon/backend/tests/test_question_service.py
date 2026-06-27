"""Tests for app.services.question_service — Phase 3 questions API."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base, QuestionKindEnum
from app.models.block import Block
from app.models.question import Question
from app.schemas.assessment import BlockRead, QuestionRead
from app.services import question_service


# ── Fixtures: in-memory SQLite ───────────────────────────────────────────────


@pytest.fixture()
def db_session():
    """Yield a Session bound to a fresh in-memory SQLite database.

    Only the blocks + questions tables are created (the full metadata contains
    models with index-name collisions on SQLite that are irrelevant here).
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine, tables=[Block.__table__, Question.__table__]
    )
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _ts() -> datetime:
    return datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def _make_block(db, slug="politica", order=1, weight=40.0):
    db.add(Block(
        slug=slug, title=f"Block {slug}", description="d", weight=weight,
        order_num=order, created_at=_ts(), updated_at=_ts(),
    ))
    db.flush()
    return slug


def _make_question(db, slug="P1", block_id="politica", kind=QuestionKindEnum.gate,
                   order=1, weight=0.0, gate_for=None):
    db.add(Question(
        slug=slug, block_id=block_id, kind=kind, text=f"Text {slug}",
        weight=weight, order_num=order, gate_for=gate_for,
    ))
    db.flush()


# ── list_blocks ──────────────────────────────────────────────────────────────


def test_list_blocks_returns_empty_when_no_rows(db_session):
    result = question_service.list_blocks(db_session)
    assert result == []


def test_list_blocks_maps_rows_to_blockread_ordered(db_session):
    _make_block(db_session, slug="b", order=2)
    _make_block(db_session, slug="a", order=1)

    result = question_service.list_blocks(db_session)

    assert len(result) == 2
    assert all(isinstance(r, BlockRead) for r in result)
    assert [r.slug for r in result] == ["a", "b"]  # ordered by order_num asc


def test_list_blocks_decimal_weight_coerced_to_float(db_session):
    _make_block(db_session, slug="x", order=1, weight=Decimal("36.00"))
    result = question_service.list_blocks(db_session)
    assert result[0].weight == 36.0
    assert isinstance(result[0].weight, float)


# ── list_questions_by_block ──────────────────────────────────────────────────


def test_list_questions_by_block_raises_when_block_missing(db_session):
    with pytest.raises(ValueError, match="Block not found"):
        question_service.list_questions_by_block(db_session, "nope")


def test_list_questions_by_block_returns_empty_when_no_questions(db_session):
    _make_block(db_session, slug="politica", order=1)
    result = question_service.list_questions_by_block(db_session, "politica")
    assert result == []


def test_list_questions_by_block_maps_and_orders(db_session):
    _make_block(db_session, slug="priv", order=2)
    _make_question(db_session, slug="P5", block_id="priv", order=5)
    _make_question(db_session, slug="P2", block_id="priv", order=2)
    _make_question(db_session, slug="P9", block_id="priv", order=9,
                  kind=QuestionKindEnum.scale, weight=Decimal("16.0"))

    result = question_service.list_questions_by_block(db_session, "priv")

    assert len(result) == 3
    assert all(isinstance(q, QuestionRead) for q in result)
    assert [q.slug for q in result] == ["P2", "P5", "P9"]
    assert result[-1].weight == 16.0


def test_list_questions_by_block_excludes_other_blocks(db_session):
    _make_block(db_session, slug="a", order=1)
    _make_block(db_session, slug="b", order=2)
    _make_question(db_session, slug="P1", block_id="a", order=1)
    _make_question(db_session, slug="P2", block_id="b", order=2)

    result = question_service.list_questions_by_block(db_session, "a")

    assert [q.slug for q in result] == ["P1"]


def test_list_questions_by_block_maps_gate_for_json(db_session):
    _make_block(db_session, slug="g", order=1)
    _make_question(db_session, slug="P1", block_id="g", order=1,
                   gate_for=["P2", "P3", "P4", "P5"])

    result = question_service.list_questions_by_block(db_session, "g")

    assert result[0].gate_for == ["P2", "P3", "P4", "P5"]