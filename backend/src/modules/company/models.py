from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..company_membership.model import CompanyMembership


class Company(Base, TimestampMixin):
    """Persisted company profile."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        init=False,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        default=None,
    )

    website: Mapped[str | None] = mapped_column(
        String(2048),
        default=None,
    )

    company_memberships: Mapped[list["CompanyMembership"]] = relationship(
        "CompanyMembership",
        back_populates="company",
        init=False,
    )
