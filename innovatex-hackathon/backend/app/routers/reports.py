"""Report endpoints — PDF/Excel export + shareable links.

Mounted in main.py as:
    app.include_router(reports.router, prefix="/api", tags=["Reports"])
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_required, get_current_user_optional, UserPayload
from app.models.assessment import Assessment
from app.schemas.report import ShareLinkCreate, ShareLinkRead, SharedReportView
from app.services import report_service, tenant_service

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Helpers ────────────────────────────────────────────────────────────────

def _get_assessment_or_404(db: Session, assessment_id: str, user_id: str) -> Assessment:
    """Fetch an assessment and verify tenant membership. Returns Assessment or raises HTTP 404."""
    import uuid as _uuid
    try:
        aid = _uuid.UUID(assessment_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment = db.query(Assessment).filter(Assessment.id == aid).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")

    try:
        tenant_service.assert_membership(db, assessment.company_id, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


def _map_value_error(exc: ValueError) -> HTTPException:
    msg = str(exc)
    if "not found" in msg.lower():
        code = 404
    elif "expired" in msg.lower():
        code = 410
    elif "revoked" in msg.lower():
        code = 410
    elif "forbidden" in msg.lower():
        code = 403
    else:
        code = 400
    return HTTPException(status_code=code, detail=msg)


# ── PDF Export ──────────────────────────────────────────────────────────────

@router.get("/assessments/{assessment_id}/export/pdf")
def export_pdf(
    assessment_id: str,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Download a formal PDF report for the assessment."""
    assessment = _get_assessment_or_404(db, assessment_id, user.user_id)

    try:
        pdf_bytes = report_service.build_pdf(db, assessment)
    except ValueError as exc:
        raise _map_value_error(exc)
    except Exception:
        logger.exception("PDF generation failed for assessment %s", assessment_id)
        raise HTTPException(status_code=500, detail="PDF generation failed")

    filename = f"diagnostico-{assessment_id[:8]}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Excel Export ────────────────────────────────────────────────────────────

@router.get("/assessments/{assessment_id}/export/excel")
def export_excel(
    assessment_id: str,
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Download a detailed Excel report for the assessment."""
    assessment = _get_assessment_or_404(db, assessment_id, user.user_id)

    try:
        xlsx_bytes = report_service.build_excel(db, assessment)
    except ValueError as exc:
        raise _map_value_error(exc)
    except Exception:
        logger.exception("Excel generation failed for assessment %s", assessment_id)
        raise HTTPException(status_code=500, detail="Excel generation failed")

    filename = f"diagnostico-{assessment_id[:8]}.xlsx"
    return StreamingResponse(
        iter([xlsx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Share Link ──────────────────────────────────────────────────────────────

@router.post(
    "/assessments/{assessment_id}/share",
    response_model=ShareLinkRead,
    status_code=status.HTTP_201_CREATED,
)
def create_share(
    assessment_id: str,
    payload: ShareLinkCreate = ShareLinkCreate(),
    user: UserPayload = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create/refresh an expiring shareable link for this assessment.

    Any previously active share link for this assessment is revoked automatically.
    """
    assessment = _get_assessment_or_404(db, assessment_id, user.user_id)

    try:
        return report_service.create_share_link(db, assessment, user.user_id, payload)
    except ValueError as exc:
        raise _map_value_error(exc)
    except Exception:
        logger.exception("Share link creation failed for assessment %s", assessment_id)
        raise HTTPException(status_code=500, detail="Share link creation failed")


# ── Public Share View ───────────────────────────────────────────────────────

@router.get("/share/{token}", response_model=SharedReportView)
def view_shared_report(
    token: str,
    db: Session = Depends(get_db),
):
    """Public endpoint — view a shared assessment report by its token.

    No authentication required. Returns 404 for invalid tokens, 410 for
    expired or revoked tokens.
    """
    try:
        return report_service.get_shared_assessment(db, token)
    except ValueError as exc:
        raise _map_value_error(exc)
    except Exception:
        logger.exception("Shared report view failed for token %s", token[:8])
        raise HTTPException(status_code=500, detail="Failed to load shared report")
