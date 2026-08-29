from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint, Table, Column, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .enums import PreferredEmploymentType, PreferredSeniorityLevel, PreferredJobBenefit
from ....frameworks.database.session import Base
from ..job_categories.models import JobCategory
from ..province.models import Province
from ..salary_range.model import SalaryRange

if TYPE_CHECKING:
    from ..applicant_profile.models import ApplicantProfile


job_preference_job_categories = Table(
    "job_preference_job_categories",
    Base.metadata,
    Column(
        "job_preference_id",
        Integer,
        ForeignKey("job_preferences.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "job_category_id",
        Integer,
        ForeignKey("job_categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


job_preference_provinces = Table(
    "job_preference_provinces",
    Base.metadata,
    Column(
        "job_preference_id",
        Integer,
        ForeignKey("job_preferences.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "province_id",
        Integer,
        ForeignKey("provinces.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class JobPreferenceEmploymentType(Base):
    __tablename__ = "job_preference_employment_types"

    job_preference_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_preferences.id", ondelete="CASCADE"),
        primary_key=True,
    )

    employment_type: Mapped[PreferredEmploymentType] = mapped_column(
        SQLEnum(
            PreferredEmploymentType,
            values_callable=lambda enum: [item.value for item in enum],
            name="preferred_employment_type",
        ),
        primary_key=True,
    )

    job_preference: Mapped["JobPreference"] = relationship(
        "JobPreference",
        back_populates="employment_types",
        init=False,
    )


class JobPreferenceSeniorityLevel(Base):
    __tablename__ = "job_preference_seniority_levels"

    job_preference_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_preferences.id", ondelete="CASCADE"),
        primary_key=True,
    )

    seniority_level: Mapped[PreferredSeniorityLevel] = mapped_column(
        SQLEnum(
            PreferredSeniorityLevel,
            values_callable=lambda enum: [item.value for item in enum],
            name="preferred_seniority_level",
        ),
        primary_key=True,
    )

    job_preference: Mapped["JobPreference"] = relationship(
        "JobPreference",
        back_populates="seniority_levels",
        init=False,
    )


class JobPreferenceBenefit(Base):
    __tablename__ = "job_preference_benefits"

    job_preference_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_preferences.id", ondelete="CASCADE"),
        primary_key=True,
    )

    benefit: Mapped[PreferredJobBenefit] = mapped_column(
        SQLEnum(
            PreferredJobBenefit,
            values_callable=lambda enum: [item.value for item in enum],
            name="preferred_job_benefit",
        ),
        primary_key=True,
    )

    job_preference: Mapped["JobPreference"] = relationship(
        "JobPreference",
        back_populates="benefits",
        init=False,
    )


class JobPreference(Base):
    __tablename__ = "job_preferences"
    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            name="uq_job_preferences_profile_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        init=False,
    )

    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("applicant_profiles.id", ondelete="CASCADE"),
        unique=True,
    )

    minimum_salary_range_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("salary_ranges.id", ondelete="SET NULL"),
        nullable=True,
    )

    applicant: Mapped["ApplicantProfile"] = relationship(
        "ApplicantProfile",
        back_populates="job_preference",
        init=False,
    )

    minimum_salary_range: Mapped["SalaryRange | None"] = relationship(
        "SalaryRange",
        init=False,
    )

    job_categories: Mapped[list["JobCategory"]] = relationship(
        "JobCategory",
        secondary="job_preference_job_categories",
        init=False,
    )

    provinces: Mapped[list["Province"]] = relationship(
        "Province",
        secondary="job_preference_provinces",
        init=False,
    )

    employment_types: Mapped[list["JobPreferenceEmploymentType"]] = relationship(
        "JobPreferenceEmploymentType",
        cascade="all, delete-orphan",
        init=False,
    )

    seniority_levels: Mapped[list["JobPreferenceSeniorityLevel"]] = relationship(
        "JobPreferenceSeniorityLevel",
        cascade="all, delete-orphan",
        init=False,
    )

    benefits: Mapped[list["JobPreferenceBenefit"]] = relationship(
        "JobPreferenceBenefit",
        cascade="all, delete-orphan",
        init=False,
    )