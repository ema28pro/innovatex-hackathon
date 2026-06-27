"""Block model — questionnaire block/section (e.g. "Política", "Diseño", "Gobernanza")."""

from sqlalchemy import Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"

    slug: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
