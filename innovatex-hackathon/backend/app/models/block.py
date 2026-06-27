"""Block — questionnaire block (e.g. política, privacidad_diseño, gobernanza)."""
from sqlalchemy import String, Text, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"

    slug: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False,
        comment="Block weight as percentage of total (40, 36, 24)"
    )
    order_num: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True
    )
