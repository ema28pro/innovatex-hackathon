"""Tests for app.routers.assessments — Phase 3 assessment API.

Mirrors the pattern in tests/test_questions_router.py: the service layer is
patched so no real database is used, and auth + db dependencies are overridden.
The error-code mapping asserted here matches the wiring contract:

    403 → "Forbidden" in message
    404 → "not found" in message
    409 → "already completed" in message
    400 → fallback
"""
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies import UserPayload
from app.routers import assessments


VALID_COMPANY = "00000000-0000-0000-0000-000000000001"
VALID_ASSESSMENT = "00000000-0000-0000-0000-000000000002"
VALID_USER = "00000000-0000-0000-0000-000000000003"


def _make_app() -> FastAPI:
    """Build a minimal app mounting only the assessments router under /api."""
    app = FastAPI()
    app.include_router(assessments.router, prefix="/api", tags=["Assessments"])
    return app


@pytest.fixture()
def client():
    app = _make_app()
    fake_user = UserPayload(user_id="u-1", email="u@example.com", role="authenticated")

    async def _override_user():
        return fake_user

    def _override_db():
        yield "DB_SESSION"

    app.dependency_overrides[assessments.get_current_user_required] = _override_user
    app.dependency_overrides[assessments.get_db] = _override_db

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _answer_body(kind: str = "scale") -> dict:
    if kind == "scale":
        return {"question_id": "P2", "kind": "scale", "scale_resp": 50}
    if kind == "gate":
        return {"question_id": "P2", "kind": "gate", "gate_resp": True}
    return {"question_id": "P2", "kind": "validation", "validation_resp": True}


# ── auth ─────────────────────────────────────────────────────────────────────


def test_post_assessments_requires_auth():
    app = _make_app()
    client = TestClient(app)
    resp = client.post("/api/assessments", json={"company_id": VALID_COMPANY})
    assert resp.status_code == 401


def test_get_assessment_requires_auth():
    app = _make_app()
    client = TestClient(app)
    resp = client.get(f"/api/assessments/{VALID_ASSESSMENT}")
    assert resp.status_code == 401


def test_post_answer_requires_auth():
    app = _make_app()
    client = TestClient(app)
    resp = client.post(
        f"/api/assessments/{VALID_ASSESSMENT}/answers", json=_answer_body()
    )
    assert resp.status_code == 401


def test_put_assessment_requires_auth():
    app = _make_app()
    client = TestClient(app)
    resp = client.put(f"/api/assessments/{VALID_ASSESSMENT}", json={"status": "completed"})
    assert resp.status_code == 401


# ── POST /assessments ───────────────────────────────────────────────────────


def test_create_assessment_returns_201(client):
    fake_read = {
        "id": VALID_ASSESSMENT,
        "company_id": VALID_COMPANY,
        "created_by": "00000000-0000-0000-0000-000000000003",
        "status": "draft",
        "overall_score": None,
        "completed_at": None,
        "created_at": "2025-01-01T00:00:00Z",
        "answers": [],
    }
    with patch.object(
        assessments.assessment_service, "start_assessment", return_value=fake_read
    ) as mock_start:
        resp = client.post("/api/assessments", json={"company_id": VALID_COMPANY})

    assert resp.status_code == 201
    assert resp.json() == fake_read
    mock_start.assert_called_once()
    # signature: (db, user_id, payload)
    assert mock_start.call_args.args[0] == "DB_SESSION"
    assert mock_start.call_args.args[1] == "u-1"


def test_create_assessment_forbidden_returns_403(client):
    with patch.object(
        assessments.assessment_service, "start_assessment",
        side_effect=ValueError("Forbidden: not a member"),
    ):
        resp = client.post("/api/assessments", json={"company_id": VALID_COMPANY})
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Forbidden: not a member"}


def test_create_assessment_other_error_returns_400(client):
    with patch.object(
        assessments.assessment_service, "start_assessment",
        side_effect=ValueError("bad company id"),
    ):
        resp = client.post("/api/assessments", json={"company_id": VALID_COMPANY})
    assert resp.status_code == 400


# ── GET /assessments/{id} ───────────────────────────────────────────────────


def test_get_assessment_returns_200(client):
    fake_read = {
        "id": VALID_ASSESSMENT, "company_id": VALID_COMPANY,
        "created_by": "00000000-0000-0000-0000-000000000003", "status": "draft", "overall_score": None,
        "completed_at": None, "created_at": "2025-01-01T00:00:00Z",
        "answers": [],
    }
    with patch.object(
        assessments.assessment_service, "get_assessment", return_value=fake_read
    ) as mock_get:
        resp = client.get(f"/api/assessments/{VALID_ASSESSMENT}")

    assert resp.status_code == 200
    assert resp.json() == fake_read
    assert mock_get.call_args.args[0] == "DB_SESSION"
    assert mock_get.call_args.args[1] == VALID_ASSESSMENT
    assert mock_get.call_args.args[2] == "u-1"


def test_get_assessment_not_found_returns_404(client):
    with patch.object(
        assessments.assessment_service, "get_assessment",
        side_effect=ValueError("Assessment not found"),
    ):
        resp = client.get(f"/api/assessments/{VALID_ASSESSMENT}")
    assert resp.status_code == 404


def test_get_assessment_forbidden_returns_403(client):
    with patch.object(
        assessments.assessment_service, "get_assessment",
        side_effect=ValueError("Forbidden: not a member"),
    ):
        resp = client.get(f"/api/assessments/{VALID_ASSESSMENT}")
    assert resp.status_code == 403


# ── POST /assessments/{id}/answers ──────────────────────────────────────────


def test_upsert_answer_returns_read(client):
    fake_answer = {
        "assessment_id": VALID_ASSESSMENT, "question_id": "P2",
        "kind": "scale", "scale_resp": 50, "gate_resp": None,
        "validation_resp": None, "notes": None,
        "answered_at": "2025-01-01T00:00:00Z",
    }
    with patch.object(
        assessments.assessment_service, "upsert_answer", return_value=fake_answer
    ) as mock_up:
        resp = client.post(
            f"/api/assessments/{VALID_ASSESSMENT}/answers",
            json=_answer_body("scale"),
        )

    assert resp.status_code == 200
    assert resp.json() == fake_answer
    assert mock_up.call_args.args[0] == "DB_SESSION"
    assert mock_up.call_args.args[1] == VALID_ASSESSMENT
    assert mock_up.call_args.args[2] == "u-1"


def test_upsert_answer_not_found_returns_404(client):
    with patch.object(
        assessments.assessment_service, "upsert_answer",
        side_effect=ValueError("Assessment not found"),
    ):
        resp = client.post(
            f"/api/assessments/{VALID_ASSESSMENT}/answers",
            json=_answer_body(),
        )
    assert resp.status_code == 404


def test_upsert_answer_forbidden_returns_403(client):
    with patch.object(
        assessments.assessment_service, "upsert_answer",
        side_effect=ValueError("Forbidden: not a member"),
    ):
        resp = client.post(
            f"/api/assessments/{VALID_ASSESSMENT}/answers",
            json=_answer_body(),
        )
    assert resp.status_code == 403


def test_upsert_answer_already_completed_returns_409(client):
    with patch.object(
        assessments.assessment_service, "upsert_answer",
        side_effect=ValueError("Assessment already completed"),
    ):
        resp = client.post(
            f"/api/assessments/{VALID_ASSESSMENT}/answers",
            json=_answer_body(),
        )
    assert resp.status_code == 409
    assert resp.json() == {"detail": "Assessment already completed"}


def test_upsert_answer_other_error_returns_400(client):
    with patch.object(
        assessments.assessment_service, "upsert_answer",
        side_effect=ValueError("some other problem"),
    ):
        resp = client.post(
            f"/api/assessments/{VALID_ASSESSMENT}/answers",
            json=_answer_body(),
        )
    assert resp.status_code == 400


# ── PUT /assessments/{id} ────────────────────────────────────────────────────


def test_update_assessment_returns_200(client):
    fake_read = {
        "id": VALID_ASSESSMENT, "company_id": VALID_COMPANY,
        "created_by": "00000000-0000-0000-0000-000000000003", "status": "completed", "overall_score": 72.5,
        "completed_at": "2025-01-02T00:00:00Z",
        "created_at": "2025-01-01T00:00:00Z", "answers": [],
    }
    with patch.object(
        assessments.assessment_service, "update_assessment", return_value=fake_read
    ) as mock_upd:
        resp = client.put(
            f"/api/assessments/{VALID_ASSESSMENT}", json={"status": "completed"}
        )

    assert resp.status_code == 200
    assert resp.json() == fake_read
    assert mock_upd.call_args.args[0] == "DB_SESSION"
    assert mock_upd.call_args.args[1] == VALID_ASSESSMENT
    assert mock_upd.call_args.args[2] == "u-1"


def test_update_assessment_not_found_returns_404(client):
    with patch.object(
        assessments.assessment_service, "update_assessment",
        side_effect=ValueError("Assessment not found"),
    ):
        resp = client.put(
            f"/api/assessments/{VALID_ASSESSMENT}", json={"status": "completed"}
        )
    assert resp.status_code == 404


def test_update_assessment_forbidden_returns_403(client):
    with patch.object(
        assessments.assessment_service, "update_assessment",
        side_effect=ValueError("Forbidden: not a member"),
    ):
        resp = client.put(
            f"/api/assessments/{VALID_ASSESSMENT}", json={"status": "completed"}
        )
    assert resp.status_code == 403


def test_update_assessment_already_completed_returns_409(client):
    with patch.object(
        assessments.assessment_service, "update_assessment",
        side_effect=ValueError("Assessment already completed"),
    ):
        resp = client.put(
            f"/api/assessments/{VALID_ASSESSMENT}", json={"status": "completed"}
        )
    assert resp.status_code == 409


def test_update_assessment_other_error_returns_400(client):
    with patch.object(
        assessments.assessment_service, "update_assessment",
        side_effect=ValueError("unexpected failure"),
    ):
        resp = client.put(
            f"/api/assessments/{VALID_ASSESSMENT}", json={"status": "completed"}
        )
    assert resp.status_code == 400