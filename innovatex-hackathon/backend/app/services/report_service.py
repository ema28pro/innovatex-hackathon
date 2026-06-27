"""Report service — gathers data, delegates to PDF/Excel generators, manages share links.

All queries are tenant-scoped: the caller must already pass through
tenant_service.assert_membership before reaching any function here.
"""
from __future__ import annotations

import logging
import uuid as _uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.assessment_answer import AssessmentAnswer
from app.models.block import Block
from app.models.company import Company
from app.models.question import Question, QuestionKindEnum
from app.models.recommendation import Recommendation
from app.models.action_item import ActionItem
from app.models.share_link import ShareLink, ShareLinkStatusEnum

from app.schemas.report import (
    ReportData, ScoreSummary, BlockScoreRead,
    QuestionAnswerRead, RecommendationRead, ActionItemRead,
    ShareLinkCreate, ShareLinkRead, SharedReportView,
)
from app.services import scoring_service
from app.reports import generate_pdf_bytes, generate_excel_bytes

logger = logging.getLogger(__name__)


def _format_answer_value(a: AssessmentAnswer) -> str | None:
    """Return a human-readable string for an answer."""
    if a.scale_resp is not None:
        return f"{a.scale_resp}/100"
    if a.gate_resp is not None:
        return "Sí" if a.gate_resp else "No"
    if a.validation_resp is not None:
        return "Sí" if a.validation_resp else "No"
    return None


def gather_report_data(db: Session, assessment: Assessment) -> ReportData:
    """Collect all data needed to render a PDF/Excel report."""
    company = db.query(Company).filter(Company.id == assessment.company_id).first()
    if not company:
        raise ValueError("Company not found")

    questions = db.query(Question).order_by(Question.order_num).all()
    blocks = db.query(Block).order_by(Block.order_num).all()
    answers = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.assessment_id == assessment.id)
        .all()
    )
    recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.assessment_id == assessment.id)
        .order_by(Recommendation.priority)
        .all()
    )
    action_items = (
        db.query(ActionItem)
        .filter(ActionItem.assessment_id == assessment.id)
        .all()
    )

    # Scores — use scoring_service to compute fresh
    score_result = scoring_service.load_result(db, assessment)
    score_summary = ScoreSummary(
        overall_percentage=score_result.overall_percentage,
        maturity_level=score_result.maturity_level,
        maturity_label=score_result.maturity_label,
        blocks=[
            BlockScoreRead(
                block_slug=br.block_id,
                block_title=br.title,
                score=br.score,
                max_score=br.max_score,
                percentage=br.percentage,
            )
            for br in score_result.blocks
        ],
    )

    # Question answers (join with question text)
    q_by_slug = {q.slug: q for q in questions}
    b_by_slug = {b.slug: b for b in blocks}
    answer_list: list[QuestionAnswerRead] = []
    for q in questions:
        a = next((a for a in answers if a.question_id == q.slug), None)
        answer_list.append(QuestionAnswerRead(
            question_slug=q.slug,
            question_text=q.text,
            block_slug=q.block_id,
            kind=q.kind.value,
            answer_value=_format_answer_value(a) if a else None,
            scale_resp=a.scale_resp if a else None,
            gate_resp=a.gate_resp if a else None,
            validation_resp=a.validation_resp if a else None,
            notes=a.notes if a else None,
        ))

    return ReportData(
        company_name=company.name,
        company_nit=company.nit,
        company_sector=company.sector,
        company_size=company.size,
        assessment_id=assessment.id,
        assessment_status=assessment.status.value,
        completed_at=assessment.completed_at,
        scores=score_summary,
        answers=answer_list,
        recommendations=[
            RecommendationRead.model_validate(r) for r in recommendations
        ],
        action_items=[
            ActionItemRead.model_validate(ai) for ai in action_items
        ],
        generated_at=datetime.now(timezone.utc),
    )


def build_pdf(db: Session, assessment: Assessment) -> bytes:
    """Gather data and build a PDF in memory."""
    data = gather_report_data(db, assessment)
    logger.info("Generating PDF for assessment %s", assessment.id)
    return generate_pdf_bytes(data)


def build_excel(db: Session, assessment: Assessment) -> bytes:
    """Gather data and build an Excel workbook in memory."""
    data = gather_report_data(db, assessment)
    logger.info("Generating Excel for assessment %s", assessment.id)
    return generate_excel_bytes(data)


def create_share_link(
    db: Session, assessment: Assessment, created_by: str, payload: ShareLinkCreate
) -> ShareLinkRead:
    """Create an expiring share link for an assessment.

    Returns the ShareLinkRead with the full URL included.
    """
    # Expire any previously active links for this assessment
    db.query(ShareLink).filter(
        ShareLink.assessment_id == assessment.id,
        ShareLink.status == ShareLinkStatusEnum.active,
    ).update({"status": ShareLinkStatusEnum.revoked}, synchronize_session=False)

    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    token = _uuid.uuid4()

    sl = ShareLink(
        assessment_id=assessment.id,
        token=token,
        created_by=_uuid.UUID(created_by),
        expires_at=expires_at,
        status=ShareLinkStatusEnum.active,
        view_count=0,
    )
    db.add(sl)
    db.commit()
    db.refresh(sl)

    # Build the full URL (base from config could be injected, but we keep it simple)
    from app.config import settings
    base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    url = f"{base}/share/{sl.token}"

    return ShareLinkRead(
        id=sl.id,
        assessment_id=sl.assessment_id,
        token=str(sl.token),
        expires_at=sl.expires_at,
        status=sl.status,
        view_count=sl.view_count,
        created_at=sl.created_at,
        url=url,
    )


def get_shared_assessment(db: Session, token: str) -> SharedReportView:
    """Validate a share token and return the public read-only report payload.

    Raises ValueError with appropriate messages for expired/revoked/invalid tokens.
    """
    try:
        token_uuid = _uuid.UUID(token)
    except ValueError:
        raise ValueError("Invalid share token")

    sl = (
        db.query(ShareLink)
        .filter(ShareLink.token == token_uuid)
        .first()
    )
    if sl is None:
        raise ValueError("Share link not found")

    if sl.status == ShareLinkStatusEnum.revoked:
        raise ValueError("Share link has been revoked")

    if sl.status == ShareLinkStatusEnum.expired or sl.expires_at < datetime.now(timezone.utc):
        if sl.status != ShareLinkStatusEnum.expired:
            sl.status = ShareLinkStatusEnum.expired
            db.commit()
        raise ValueError("Share link has expired")

    assessment = db.query(Assessment).filter(Assessment.id == sl.assessment_id).first()
    if not assessment:
        raise ValueError("Assessment not found")

    company = db.query(Company).filter(Company.id == assessment.company_id).first()
    score_result = scoring_service.load_result(db, assessment)

    action_items = (
        db.query(ActionItem)
        .filter(ActionItem.assessment_id == assessment.id)
        .all()
    )

    # Increment view count
    sl.view_count += 1
    db.commit()

    return SharedReportView(
        company_name=company.name if company else "—",
        assessment_status=assessment.status.value,
        completed_at=assessment.completed_at,
        scores=ScoreSummary(
            overall_percentage=score_result.overall_percentage,
            maturity_level=score_result.maturity_level,
            maturity_label=score_result.maturity_label,
            blocks=[
                BlockScoreRead(
                    block_slug=br.block_id,
                    block_title=br.title,
                    score=br.score,
                    max_score=br.max_score,
                    percentage=br.percentage,
                )
                for br in score_result.blocks
            ],
        ),
        action_items=[
            ActionItemRead.model_validate(ai) for ai in action_items
        ],
        expires_at=sl.expires_at,
        view_count=sl.view_count,
    )
