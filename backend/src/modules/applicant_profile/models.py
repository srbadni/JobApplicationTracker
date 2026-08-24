from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .enums import Gender, MartialStatus
from ..job_posting.enums import MilitaryServiceStatus
from ...infrastructure.database.session import Base
from ...infrastructure.database.models import TimestampMixin

if TYPE_CHECKING:
    from ..user.models import User
    from ..applicant_skill.models import ApplicantSkill
    from ..applicant_work_experience.models import WorkExperience
    from ..applicant_education_history.models import Education
    from ..applicant_language.models import LanguageSkill
    from ..job_preference.models import JobPreference


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
    address: Mapped[str | None] = mapped_column(Text, init=False)
    about: Mapped[str | None] = mapped_column(Text, init=False)

    applicant: Mapped["User"] = relationship("User", back_populates="applicant_profile", init=False)
    skills: Mapped[list["ApplicantSkill"]] = relationship("ApplicantSkill", cascade="all, delete-orphan",
                                                          back_populates="applicant_profile", init=False)
    work_experiences: Mapped[list["WorkExperience"]] = relationship("WorkExperience", cascade="all, delete-orphan", back_populates="applicant", init=False)
    educations: Mapped[list["Education"]] = relationship("Education", cascade="all, delete-orphan", back_populates="applicant", init=False)
    language_skills: Mapped[list["LanguageSkill"]] = relationship("LanguageSkill", cascade="all, delete-orphan", back_populates="applicant", init=False)

    job_preference: Mapped["JobPreference | None"] = relationship(
        "JobPreference",
        back_populates="applicant",
        cascade="all, delete-orphan",
        uselist=False,
        init=False,
    )
