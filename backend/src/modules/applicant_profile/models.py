from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database import Base
from ...infrastructure.database.models import TimestampMixin

if TYPE_CHECKING:
    from ..user.models import User


class ApplicantProfile(Base, TimestampMixin):
    __tablename__ = "applicant_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    applicant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        unique=True,
    )

    applicant: Mapped["User"] = relationship("User", back_populates="applicant_profile", init=False)
