"""PDF report generator — reportlab Platypus document.

Produces a formal PDF with:
  - Cover/header: company name, NIT, sector, date
  - Global score + maturity badge
  - Per-block breakdown
  - Prioritized recommendations
  - Action items summary
"""
from __future__ import annotations

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, KeepTogether,
)

from app.schemas.report import ReportData

# ── Colours & Constants ───────────────────────────────────────────────────
BRAND_DARK = colors.HexColor("#1e293b")       # slate-800
BRAND_MUTED = colors.HexColor("#475569")       # slate-600
BRAND_LIGHT = colors.HexColor("#cbd5e1")      # slate-300
BRAND_BG = colors.HexColor("#f8fafc")         # slate-50
ACCENT_GREEN = colors.HexColor("#059669")
ACCENT_AMBER = colors.HexColor("#d97706")
ACCENT_RED = colors.HexColor("#dc2626")
ACCENT_BLUE = colors.HexColor("#2563eb")

MATURITY_COLOURS = {
    "optimizado": ACCENT_GREEN,
    "avanzado": ACCENT_BLUE,
    "basico": ACCENT_AMBER,
    "critico": ACCENT_RED,
}

WIDTH, HEIGHT = A4  # 595.27 x 841.89 pt


# ── Styles ─────────────────────────────────────────────────────────────────
_styles = getSampleStyleSheet()

style_title = ParagraphStyle("ReportTitle", parent=_styles["Title"],
                             fontSize=20, textColor=BRAND_DARK,
                             spaceAfter=6, alignment=TA_LEFT)
style_subtitle = ParagraphStyle("ReportSubtitle", parent=_styles["Normal"],
                                fontSize=10, textColor=BRAND_MUTED,
                                spaceAfter=16)
style_h1 = ParagraphStyle("ReportH1", parent=_styles["Heading2"],
                          fontSize=14, textColor=BRAND_DARK,
                          spaceBefore=18, spaceAfter=8)
style_h2 = ParagraphStyle("ReportH2", parent=_styles["Heading3"],
                          fontSize=12, textColor=BRAND_DARK,
                          spaceBefore=14, spaceAfter=6)
style_body = ParagraphStyle("ReportBody", parent=_styles["Normal"],
                            fontSize=10, textColor=BRAND_DARK,
                            leading=14, alignment=TA_JUSTIFY)
style_small = ParagraphStyle("ReportSmall", parent=_styles["Normal"],
                             fontSize=8, textColor=BRAND_MUTED)
style_score_big = ParagraphStyle("ScoreBig", parent=_styles["Normal"],
                                 fontSize=36, textColor=ACCENT_GREEN,
                                 alignment=TA_CENTER)
style_maturity_label = ParagraphStyle("MaturityLabel", parent=_styles["Normal"],
                                      fontSize=12, textColor=BRAND_MUTED,
                                      alignment=TA_CENTER)
style_table_header = ParagraphStyle("TableHeader", parent=_styles["Normal"],
                                    fontSize=9, textColor=colors.white,
                                    fontName="Helvetica-Bold")
style_table_cell = ParagraphStyle("TableCell", parent=_styles["Normal"],
                                  fontSize=9, textColor=BRAND_DARK)


# ── Helpers ────────────────────────────────────────────────────────────────

def _hdr(text: str, style=style_h1):
    return Paragraph(text, style)


def _para(text: str, style=style_body):
    return Paragraph(text, style)


def _small(text: str):
    return Paragraph(text, style_small)


def _maturity_pct(pct: float) -> str:
    """Return a maturity badge HTML snippet."""
    level = "optimizado" if pct >= 90 else ("avanzado" if pct >= 70 else ("basico" if pct >= 40 else "critico"))
    color = MATURITY_COLOURS.get(level, ACCENT_GREEN)
    hex_str = color.hexval()[2:]  # "059669"
    label = {"optimizado": "Optimizado", "avanzado": "Avanzado", "basico": "Básico", "critico": "Crítico"}.get(level, level)
    return (
        f'<font color="#{hex_str}" size="36"><b>{pct:.1f}%</b></font><br/>'
        f'<font color="#475569" size="12">Nivel {label}</font>'
    )


# ── Document builder ───────────────────────────────────────────────────────

def generate_pdf_bytes(data: ReportData) -> bytes:
    """Build a PDF in memory and return the raw bytes."""
    buf = io.BytesIO()

    # ── DocTemplate with header/footer frames ──────────────────────────────
    frame = Frame(2 * cm, 2 * cm, WIDTH - 4 * cm, HEIGHT - 4 * cm, id="main")
    template = PageTemplate(id="report", frames=[frame],
                            onPage=_page_decorator)
    doc = BaseDocTemplate(buf, pagesize=A4, title=f"Diagnóstico — {data.company_name}",
                          author="Diagnóstico Ley 1581")
    doc.addPageTemplates([template])

    story: list = []

    # ── Title block ────────────────────────────────────────────────────────
    story.append(Paragraph(f"Diagnóstico de Cumplimiento<br/>Ley 1581 de 2012", style_title))
    story.append(Paragraph(
        f"{data.company_name}  ·  NIT {data.company_nit}  ·  {data.company_sector or '—'}  ·  {data.company_size or '—'}  ·  "
        f"{data.generated_at.strftime('%d/%m/%Y')}",
        style_subtitle))
    story.append(Spacer(1, 6))

    # ── Global score ──────────────────────────────────────────────────────
    story.append(_hdr("Resultado Global"))
    pct = data.scores.overall_percentage
    maturity_color = MATURITY_COLOURS.get(data.scores.maturity_level, ACCENT_GREEN)
    hex_c = maturity_color.hexval()[2:]

    score_table = Table([
        [Paragraph(
            f'<font color="#{hex_c}" size="36"><b>{pct:.1f}%</b></font><br/>'
            f'<font color="#475569" size="12">{data.scores.maturity_label}</font>',
            ParagraphStyle("ScoreCell", parent=_styles["Normal"], alignment=TA_CENTER))
         ],
    ], colWidths=[doc.width * 0.5])
    score_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_BG),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # ── Block breakdown ────────────────────────────────────────────────────
    if data.scores.blocks:
        story.append(_hdr("Resultados por Bloque"))
        block_data = [["Bloque", "Puntaje", "%", "Barra"]]
        for b in data.scores.blocks:
            bar_len = max(1, int(b.percentage / 100 * 20))
            bar_str = "█" * bar_len + "░" * (20 - bar_len)
            block_data.append([
                Paragraph(b.block_title, style_table_cell),
                Paragraph(f"{b.score:.1f} / {b.max_score:.1f}", style_table_cell),
                Paragraph(f"{b.percentage:.1f}%", style_table_cell),
                Paragraph(bar_str, ParagraphStyle("Bar", parent=style_table_cell,
                                                  fontName="Courier", fontSize=7)),
            ])
        bt = Table(block_data, colWidths=[doc.width * 0.35, doc.width * 0.2, doc.width * 0.1, doc.width * 0.35])
        bt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, BRAND_LIGHT),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_BG, colors.white]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(bt)
        story.append(Spacer(1, 14))

    # ── Recommendations ────────────────────────────────────────────────────
    if data.recommendations:
        story.append(_hdr("Recomendaciones"))
        recs = sorted(data.recommendations, key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r.priority.value, 3))
        for i, rec in enumerate(recs[:10], 1):  # top 10
            prio_color = {"high": ACCENT_RED, "medium": ACCENT_AMBER, "low": BRAND_MUTED}.get(rec.priority.value, BRAND_MUTED)
            prio_hex = prio_color.hexval()[2:]
            story.append(Paragraph(
                f'<font color="#{prio_hex}"><b>[{rec.priority.value.upper()}]</b></font> '
                f'{rec.ai_generated_text[:300]}{"..." if len(rec.ai_generated_text) > 300 else ""}',
                style_body))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 10))

    # ── Action Items ───────────────────────────────────────────────────────
    if data.action_items:
        story.append(_hdr("Plan de Acción"))
        ai_data = [["Ítem", "Estado"]]
        for ai in data.action_items:
            status_map = {"pending": "⏳ Pendiente", "in_progress": "🔄 En progreso", "completed": "✓ Completada"}
            ai_data.append([
                Paragraph(ai.title, style_table_cell),
                Paragraph(status_map.get(ai.status, ai.status), style_table_cell),
            ])
        ait = Table(ai_data, colWidths=[doc.width * 0.7, doc.width * 0.3])
        ait.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BRAND_LIGHT),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_BG, colors.white]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(ait)
        story.append(Spacer(1, 14))

    # ── Answers detail ─────────────────────────────────────────────────────
    if data.answers:
        story.append(_hdr("Detalle de Respuestas"))
        ans_data = [["#", "Pregunta", "Respuesta"]]
        for i, a in enumerate(data.answers, 1):
            ans_val = a.answer_value or "—"
            ans_data.append([
                Paragraph(str(i), style_table_cell),
                Paragraph(a.question_text[:120], style_table_cell),
                Paragraph(ans_val, style_table_cell),
            ])
        at = Table(ans_data, colWidths=[doc.width * 0.08, doc.width * 0.62, doc.width * 0.3])
        at.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BRAND_LIGHT),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_BG, colors.white]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(at)
        story.append(Spacer(1, 14))

    # ── Footer note ────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(_small(
        f"Documento generado automáticamente el {data.generated_at.strftime('%d/%m/%Y a las %H:%M')} UTC. "
        f"Plataforma Diagnóstico Ley 1581 de 2012."
    ))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def _page_decorator(canvas, doc):
    """Header and footer drawn on every page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(BRAND_MUTED)

    # Header line
    canvas.setStrokeColor(BRAND_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, HEIGHT - 1.5 * cm, WIDTH - 2 * cm, HEIGHT - 1.5 * cm)
    canvas.drawString(2 * cm, HEIGHT - 1.3 * cm, "Diagnóstico Ley 1581 de 2012 · Confidencial")

    # Footer
    canvas.line(2 * cm, 1.5 * cm, WIDTH - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.2 * cm, f"Página {canvas.getPageNumber()}")

    canvas.restoreState()
