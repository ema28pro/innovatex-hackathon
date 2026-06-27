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

    def _override_db():
        yield "DB_SESSION"

    app.dependency_overrides[questions.get_current_user_required] = _override_user
    app.dependency_overrides[questions.get_db] = _override_db

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── auth ─────────────────────────────────────────────────────────────────────


def test_get_blocks_requires_auth():
    """Without an auth override and no Authorization header → 401."""
    app = _make_app()
    client = TestClient(app)
    resp = client.get("/api/blocks")
    assert resp.status_code == 401


def test_get_block_questions_requires_auth():
    app = _make_app()
    client = TestClient(app)
    resp = client.get("/api/blocks/politica/questions")
    assert resp.status_code == 401


# ── GET /blocks ──────────────────────────────────────────────────────────────


def test_get_blocks_returns_list(client):
    fake_blocks = [
        {"slug": "politica", "title": "Política", "description": None,
         "weight": 40.0, "order_num": 1, "created_at": "2025-01-01T00:00:00Z",
         "updated_at": "2025-01-01T00:00:00Z"},
    ]
    with patch.object(questions.question_service, "list_blocks",
                      return_value=fake_blocks) as mock_ls:
        resp = client.get("/api/blocks")

    assert resp.status_code == 200
    assert resp.json() == fake_blocks
    mock_ls.assert_called_once()
    # the db session dependency was injected as the sentinel string
    assert mock_ls.call_args.args[0] == "DB_SESSION"


# ── GET /blocks/{block_slug}/questions ───────────────────────────────────────


def test_get_block_questions_returns_list(client):
    fake_qs = [
        {"slug": "P1", "block_id": "politica", "kind": "gate",
         "text": "T", "weight": 0.0, "order_num": 1, "gate_for": ["P2"]},
    ]
    with patch.object(questions.question_service, "list_questions_by_block",
                      return_value=fake_qs) as mock_q:
        resp = client.get("/api/blocks/politica/questions")

    assert resp.status_code == 200
    assert resp.json() == fake_qs
    mock_q.assert_called_once()
    assert mock_q.call_args.args[0] == "DB_SESSION"
    assert mock_q.call_args.args[1] == "politica"


def test_get_block_questions_404_when_block_missing(client):
    with patch.object(questions.question_service, "list_questions_by_block",
                      side_effect=ValueError("Block not found")):
        resp = client.get("/api/blocks/missing/questions")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Block not found"}