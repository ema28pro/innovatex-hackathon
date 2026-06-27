"""Test that main.py wires every Phase 3 router under the /api prefix.

We assert against the OpenAPI path map (version-agnostic, unlike walking
`app.routes` whose element type changed between FastAPI releases) to confirm
the exact public paths exist.
"""
import pytest


@pytest.fixture(scope="module")
def api_paths():
    # Importing app.main triggers registration of all routers in main.py.
    from app.main import app

    return set(app.openapi()["paths"].keys())


@pytest.mark.parametrize(
    "expected_path",
    [
        # questions router
        "/api/blocks",
        "/api/blocks/{block_slug}/questions",
        # assessments router
        "/api/assessments",
        "/api/assessments/{assessment_id}",
        "/api/assessments/{assessment_id}/answers",
        # reports router (sanity — also mounted under /api)
        "/api/assessments/{assessment_id}/export/pdf",
        "/api/assessments/{assessment_id}/export/excel",
        "/api/assessments/{assessment_id}/share",
        "/api/share/{token}",
        # companies + auth still registered (regression)
        "/api/companies/",
        "/api/companies/{company_id}",
        "/api/auth/me",
    ],
)
def test_api_path_registered(api_paths, expected_path):
    assert expected_path in api_paths, (
        f"Expected route {expected_path!r} not registered in main.py. "
        f"Got: {sorted(api_paths)}"
    )


def test_questions_router_has_no_api_prefix_inside_endpoints(api_paths):
    """The questions router must NOT duplicate /api inside its own paths.

    Agent B's router defines `/blocks` (no /api); the prefix is applied by
    include_router. A doubled prefix would surface as `/api/api/blocks`.
    """
    assert "/api/blocks" in api_paths
    assert "/api/api/blocks" not in api_paths


def test_assessments_router_has_no_api_prefix_inside_endpoints(api_paths):
    assert "/api/assessments" in api_paths
    assert "/api/api/assessments" not in api_paths