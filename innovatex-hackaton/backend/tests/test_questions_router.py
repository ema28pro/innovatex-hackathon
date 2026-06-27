"""Tests for app.routers.questions — Phase 3 questions API."""
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies import UserPayload
from app.routers import questions


def _make_app() -> FastAPI:
    """Build a minimal app mounting only the questions router under /api."""
    app = FastAPI()
    app.include_router(questions.router, prefix="/api", tags=["Questions"])
    return app


@pytest.fixture()
def client():
    app = _make_app()

    fake_user = UserPayload(user_id="u-1", email="u@example.com", role="authenticated")

    async def _override_user():
        return fake_user

    app.dependency_overrides[questions.get_current_user_required] = _override_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_blocks_requires_auth():
    """No auth dependency override → request without token should be 401."""
    app = _make_app()
    # Provide a real (non-overridden) auth requirement by clearing overrides.
    client = TestClient(app)
    resp = client.get("/api/blocks")
    assert resp.status_code == 401


def test_get_blocks_returns_list(client):
    fake_blocks = [
        {"slug": "politica", "title": "Política", "description": None,
         "weight": 40.0, "order_num": 1},
    ]
    with patch.object(questions.question_service, "list_blocks",
                      return_value=fake_blocks) as mock_ls, \
         patch.object(questions, "get_db") as get_db_dep:
        get_db_dep.return_value = object()  # not used; service is mocked
        resp = client.get("/api/blocks")

    assert resp.status_code == 200
    assert resp.json() == fake_blocks
    mock_ls.assert_called_once()


def test_get_blocks_passes_db_session(client):
    captured = {}

    def fake_list_blocks(db):
        captured["db"] = db
        return []

    with patch.object(questions, "get_db") as get_db_dep, \
         patch.object(questions.question_service, "list_blocks",
                      side_effect=fake_list_blocks):
        # Wire the real get_db override to yield a sentinel session.
        def _real_db():
            yield "SENTINEL_SESSION"
        get_db_dep.side_effect = None
        app = client.app
        app.dependency_overrides[questions.get_db] = _real_db
        resp = client.get("/api/blocks")

    assert resp.status_code == 200
    assert captured["db"] == "SENTINEL_SESSION"


def test_get_block_questions_returns_list(client):
    fake_qs = [
        {"slug": "P1", "block_id": "politica", "kind": "gate",
         "text": "T", "weight": 0.0, "order_num": 1, "gate_for": ["P2"]},
    ]
    with patch.object(questions.question_service, "list_questions_by_block",
                      return_value=fake_qs) as mock_q, \
         patch.object(questions, "get_db"):
        resp = client.get("/api/blocks/politica/questions")

    assert resp.status_code == 200
    assert resp.json() == fake_qs
    mock_q.assert_called_once()
    # second positional arg is the block_slug path param
    assert mock_q.call_args.args[1] == "politica"


def test_get_block_questions_404_when_block_missing(client):
    with patch.object(questions.question_service, "list_questions_by_block",
                      side_effect=ValueError("Block not found")), \
         patch.object(questions, "get_db"):
        resp = client.get("/api/blocks/missing/questions")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Block not found"}


def test_get_block_questions_passes_db_and_slug(client):
    captured = {}

    def fake_list(db, block_slug):
        captured["db"] = db
        captured["slug"] = block_slug
        return []

    with patch.object(questions, "get_db") as get_db_dep, \
         patch.object(questions.question_service, "list_questions_by_block",
                      side_effect=fake_list):
        def _real_db():
            yield "S"
        app = client.app
        app.dependency_overrides[questions.get_db] = _real_db

        resp = client.get("/api/blocks/politica/questions")

    assert resp.status_code == 200
    assert captured == {"db": "S", "slug": "politica"}