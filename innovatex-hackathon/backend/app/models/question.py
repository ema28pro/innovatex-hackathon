"""Question — individual questionnaire question (P1-P11)."""
from sqlalchemy import String, Text, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, QuestionKindEnum


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    slug: Mapped[str] = mapped_column(String(10), primary_key=True)
    block_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("blocks.slug", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    kind: Mapped[QuestionKindEnum] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=0,
        comment="Per-question weight: P2-P5=10, P6-P8=12, P9=16, P10=8, P1/P11=0"
    )
    order_num: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    gate_for: Mapped[list | None] = mapped_column(
        JSON, nullable=True,
        comment='For gate questions: list of slugs affected when answer is "No" (e.g. ["P2","P3","P4","P5"])'
    )

    __table_args__ = (
        UniqueConstraint("block_id", "order_num", name="uq_question_block_order"),
    )
