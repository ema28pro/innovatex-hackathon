"""Phase 3 smoke tests — FastAPI TestClient end-to-end through the real app.

Auth + DB dependencies are overridden so no Postgres or Supabase JWT is
required. Service-layer calls are monkeypatched so no real queries run.
"""
import os

# Provide minimal env so app.database (imported transitively via app.main)
# does not raise "DATABASE_URL is required" at import time. These values are
# never used at runtime — get_db is overridden below.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("DATABASE_URL_POOLER", "sqlite:///./test.db")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.dependencies import get_current_user_required  # noqa: E402
from app.database import get_db  # noqa: E402


# ── Fake auth user + fake DB session ────────────────────────────────────────

fake_user = type(
    "User",
    (),
    {
        "user_id": "00000000-0000-0000-0000-0000000000aa",
        "email": "test@test.com",
        "role": "authenticated",
    },
)()


async def override_auth():
    return fake_user


class _FakeDB:
    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


def override_db():
    return _FakeDB()


app.dependency_overrides[get_current_user_required] = override_auth
app.dependency_overrides[get_db] = override_db

client = TestClient(app)


# ── 1. Health check ─────────────────────────────────────────────────────────


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "ok"


# ── 2. List blocks ──────────────────────────────────────────────────────────


def test_list_blocks(monkeypatch):
    from app.services import question_service

    def mock_list(db):
        return [
            {
                "slug": "politica",
                "title": "Test",
                "description": None,
                "weight": 40,
                "order_num": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        ]

    monkeypatch.setattr(question_service, "list_blocks", mock_list)
    r = client.get("/api/blocks")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 1
    assert r.json()[0]["slug"] == "politica"


# ── 3. Block questions ──────────────────────────────────────────────────────


def test_block_questions(monkeypatch):
    from app.services import question_service

    def mock_questions(db, block_slug):
        return [
            {
                "slug": "P1",
                "block_id": block_slug,
                "kind": "gate",
                "text": "¿Existe política?",
                "weight": 0,
                "order_num": 1,
                "gate_for": ["P2"],
            }
        ]

    monkeypatch.setattr(question_service, "list_questions_by_block", mock_questions)
    r = client.get("/api/blocks/politica/questions")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 1
    assert r.json()[0]["slug"] == "P1"


def test_block_questions_404(monkeypatch):
    from app.services import question_service

    def mock_missing(db, block_slug):
        raise ValueError("Block not found")

    monkeypatch.setattr(question_service, "list_questions_by_block", mock_missing)
    r = client.get("/api/blocks/missing/questions")
    assert r.status_code == 404
    assert r.json()["detail"] == "Block not found"


# ── 4. Start assessment ─────────────────────────────────────────────────────


def test_start_assessment(monkeypatch):
    from app.services import assessment_service

    def mock_start(db, user_id, payload):
        return {
            "id": "00000000-0000-0000-0000-000000000001",
            "company_id": "00000000-0000-0000-0000-000000000002",
            "created_by": user_id,
            "status": "draft",
            "overall_score": None,
            "completed_at": None,
            "created_at": "2024-01-01T00:00:00",
            "answers": [],
        }

    monkeypatch.setattr(assessment_service, "start_assessment", mock_start)
    r = client.post(
        "/api/assessments",
        json={"company_id": "00000000-0000-0000-0000-000000000002"},
    )
    assert r.status_code == 201, r.json()
    assert r.json()["status"] == "draft"


def test_start_assessment_forbidden(monkeypatch):
    from app.services import assessment_service

    def mock_start(db, user_id, payload):
        raise ValueError("Forbidden: not a member")

    monkeypatch.setattr(assessment_service, "start_assessment", mock_start)
    r = client.post(
        "/api/assessments",
        json={"company_id": "00000000-0000-0000-0000-000000000002"},
    )
    assert r.status_code == 403
    assert "Forbidden" in r.json()["detail"]


# ── 5. Get assessment ───────────────────────────────────────────────────────


def test_get_assessment(monkeypatch):
    from app.services import assessment_service

    def mock_get(db, assessment_id, user_id):
        return {
            "id": assessment_id,
            "company_id": "00000000-0000-0000-0000-000000000002",
            "created_by": user_id,
            "status": "draft",
            "overall_score": None,
            "completed_at": None,
            "created_at": "2024-01-01T00:00:00",
            "answers": [],
        }

    monkeypatch.setattr(assessment_service, "get_assessment", mock_get)
    r = client.get("/api/assessments/00000000-0000-0000-0000-000000000001")
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "draft"


def test_get_assessment_not_found(monkeypatch):
    from app.services import assessment_service

    def mock_get(db, assessment_id, user_id):
        raise ValueError("Assessment not found")

    monkeypatch.setattr(assessment_service, "get_assessment", mock_get)
    r = client.get("/api/assessments/00000000-0000-0000-0000-000000000099")
    assert r.status_code == 404
    assert r.json()["detail"] == "Assessment not found"


def test_get_assessment_forbidden(monkeypatch):
    from app.services import assessment_service

    def mock_get(db, assessment_id, user_id):
        raise ValueError("Forbidden")

    monkeypatch.setattr(assessment_service, "get_assessment", mock_get)
    r = client.get("/api/assessments/00000000-0000-0000-0000-000000000001")
    assert r.status_code == 403


# ── 6. Upsert answer ────────────────────────────────────────────────────────


def test_upsert_answer(monkeypatch):
    from app.services import assessment_service

    def mock_upsert(db, assessment_id, user_id, payload):
        return {
            "assessment_id": assessment_id,
            "question_id": payload.question_id if hasattr(payload, 'question_id') else payload.get("question_id", "P2"),
            "kind": payload.kind if hasattr(payload, 'kind') else payload.get("kind", "scale"),
            "scale_resp": payload.scale_resp if hasattr(payload, 'scale_resp') else payload.get("scale_resp"),
            "gate_resp": None,
            "validation_resp": None,
            "notes": None,
            "answered_at": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(assessment_service, "upsert_answer", mock_upsert)
    r = client.post(
        "/api/assessments/00000000-0000-0000-0000-000000000001/answers",
        json={"question_id": "P2", "kind": "scale", "scale_resp": 70},
    )
    assert r.status_code == 201, r.json()
    assert r.json()["question_id"] == "P2"
    assert r.json()["scale_resp"] == 70


def test_upsert_answer_not_found(monkeypatch):
    from app.services import assessment_service

    def mock_upsert(db, assessment_id, user_id, payload):
        raise ValueError("Assessment not found")

    monkeypatch.setattr(assessment_service, "upsert_answer", mock_upsert)
    r = client.post(
        "/api/assessments/00000000-0000-0000-0000-000000000099/answers",
        json={"question_id": "P2", "kind": "scale", "scale_resp": 70},
    )
    assert r.status_code == 404


def test_upsert_answer_forbidden(monkeypatch):
    from app.services import assessment_service

    def mock_upsert(db, assessment_id, user_id, payload):
        raise ValueError("Forbidden")

    monkeypatch.setattr(assessment_service, "upsert_answer", mock_upsert)
    r = client.post(
        "/api/assessments/00000000-0000-0000-0000-000000000001/answers",
        json={"question_id": "P2", "kind": "scale", "scale_resp": 70},
    )
    assert r.status_code == 403


# ── 7. Update assessment (complete) ─────────────────────────────────────────


def test_update_assessment(monkeypatch):
    from app.services import assessment_service

    def mock_update(db, assessment_id, user_id, payload):
        return {
            "id": assessment_id,
            "company_id": "00000000-0000-0000-0000-000000000002",
            "created_by": user_id,
            "status": "completed",
            "overall_score": 72.5,
            "completed_at": "2024-01-01T00:00:00",
            "created_at": "2024-01-01T00:00:00",
            "answers": [],
        }

    monkeypatch.setattr(assessment_service, "update_assessment", mock_update)
    r = client.put(
        "/api/assessments/00000000-0000-0000-0000-000000000001",
        json={"status": "completed"},
    )
    assert r.status_code == 200, r.json()
    assert r.json()["status"] == "completed"
    assert r.json()["overall_score"] == 72.5


def test_update_assessment_not_found(monkeypatch):
    from app.services import assessment_service

    def mock_update(db, assessment_id, user_id, payload):
        raise ValueError("Assessment not found")

    monkeypatch.setattr(assessment_service, "update_assessment", mock_update)
    r = client.put(
        "/api/assessments/00000000-0000-0000-0000-000000000099",
        json={"status": "completed"},
    )
    assert r.status_code == 404


def test_update_assessment_already_completed(monkeypatch):
    from app.services import assessment_service

    def mock_update(db, assessment_id, user_id, payload):
        raise ValueError("Assessment already completed")

    monkeypatch.setattr(assessment_service, "update_assessment", mock_update)
    r = client.put(
        "/api/assessments/00000000-0000-0000-0000-000000000001",
        json={"status": "completed"},
    )
    assert r.status_code == 409
    assert "already completed" in r.json()["detail"]


# ── 8. Auth required — no token = 401 ───────────────────────────────────────


def test_auth_required():
    app.dependency_overrides.pop(get_current_user_required, None)
    r = client.get("/api/blocks")
    assert r.status_code == 401 or r.status_code == 403  # 401 for missing header
    app.dependency_overrides[get_current_user_required] = override_auth