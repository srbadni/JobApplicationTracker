from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base
from .enums import EducationLevel

if TYPE_CHECKING:
    from ..applicant_profile.models import ApplicantProfile


class Education(Base):
    __tablename__ = "educations"
    __table_args__ = (
        CheckConstraint(
            "(is_currently_studying = true AND end_year IS NULL) "
            "OR (is_currently_studying = false AND end_year IS NOT NULL)",
            name="ck_education_current_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)

    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("applicant_profiles.id")
    )

    institution_name: Mapped[str] = mapped_column(String(200))
    field_of_study: Mapped[str] = mapped_column(String(200))

    education_level: Mapped[EducationLevel] = mapped_column(
        Enum(EducationLevel),
        nullable=False
    )

    start_year: Mapped[int] = mapped_column(Integer)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_currently_studying: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        init=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    applicant: Mapped["ApplicantProfile"] = relationship(
        "ApplicantProfile",
        back_populates="educations",
        init=False
    )