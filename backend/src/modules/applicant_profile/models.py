from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .enums import Gender, MartialStatus
from ..job_posting.enums import MilitaryServiceStatus
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

    specialization: Mapped[str | None] = mapped_column(String(100), init=False)
    birth_year: Mapped[int | None] = mapped_column(Integer, init=False)
    gender: Mapped[Gender | None] = mapped_column(String(20), init=False)
    military_status: Mapped[MilitaryServiceStatus | None] = mapped_column(String(50), init=False)
    martial_status: Mapped[MartialStatus | None] = mapped_column(String(20), init=False)
    province: Mapped[str | None] = mapped_column(String(50), init=False)
    address: Mapped[str | None] = mapped_column(String, init=False)
    about: Mapped[str | None] = mapped_column(String, init=False)

    applicant: Mapped["User"] = relationship("User", back_populates="applicant_profile", init=False)
