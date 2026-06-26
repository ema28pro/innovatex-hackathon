"""Question model — individual scoring/gate/validation question within a block."""

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, QuestionKindEnum, TimestampMixin


class Question(Base, TimestampMixin):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("block_id", "order_num", name="uq_question_block_order"),
    )

    slug: Mapped[str] = mapped_column(String(10), primary_key=True)
    block_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("blocks.slug", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    kind: Mapped[QuestionKindEnum] = mapped_column(
        SAEnum(QuestionKindEnum), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    order_num: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    gate_for: Mapped[list | None] = mapped_column(JSON, nullable=True)
