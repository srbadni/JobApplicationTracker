from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..company.models import Company
    from ..user.models import User


class CompanyMembership(Base):
    """Represents a user's membership in a company."""

    __tablename__ = "company_memberships"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        init=False,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        unique=True,
        nullable=False,
    )

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="company_membership",
        init=False,
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="company_memberships",
        init=False,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
