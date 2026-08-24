from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database import Base

if TYPE_CHECKING:
    from ..user.models import User


class ApplicantProfile(Base, TimestampMixin):
    __tablename__ = "applicant_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    applicant: Mapped["User"] = relationship("User", back_populates="applicant_profile", init=False)