from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base


class Company(Base, TimestampMixin):
    """Persisted company profile."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    website: Mapped[str | None] = mapped_column(String(2048), default=None)
