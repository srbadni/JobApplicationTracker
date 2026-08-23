from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base
from .enums import (
    EmploymentType,
    Gender,
    MilitaryServiceStatus,
    MinimumEducationLevel,
    RelevantWorkExperience,
    WorkMode, JobPostingStatus,
)

if TYPE_CHECKING:
    from ..company.models import Company
    from ..job_categories.models import JobCategory
    from ..user.models import User
    from ..province.models import Province
    from ..city.models import City
    from ..salary_range.model import SalaryRange


class JobPosting(Base, TimestampMixin):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False, autoincrement=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
    )

    job_category_id: Mapped[int] = mapped_column(
        ForeignKey("job_categories.id"),
        nullable=False,
    )

    province_id: Mapped[int] = mapped_column(
        ForeignKey("provinces.id"),
        nullable=False,
    )

    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id"),
        nullable=False,
    )

    job_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    job_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    company_overview: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(
            EmploymentType,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    work_mode: Mapped[WorkMode] = mapped_column(
        Enum(
            WorkMode,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    salary_range_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("salary_ranges.id"),
        nullable=False
    )

    salary_range: Mapped["SalaryRange"] = relationship("SalaryRange", back_populates="job_postings", init=False)

    is_latin_text: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    status: Mapped[JobPostingStatus] = mapped_column(
        Enum(
            JobPostingStatus,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=JobPostingStatus.NEEDS_REVIEW,
        server_default=JobPostingStatus.NEEDS_REVIEW.value,
        init=False
    )

    work_experience: Mapped[RelevantWorkExperience] = mapped_column(
        Enum(
            RelevantWorkExperience,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    minimum_education: Mapped[MinimumEducationLevel] = mapped_column(
        Enum(
            MinimumEducationLevel,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    gender: Mapped[Gender] = mapped_column(
        Enum(
            Gender,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    military_status: Mapped[MilitaryServiceStatus] = mapped_column(
        Enum(
            MilitaryServiceStatus,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    post_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="job_postings",
        init=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="job_postings",
        init=False
    )

    job_category: Mapped["JobCategory"] = relationship(
        "JobCategory",
        init=False,
        back_populates="job_postings"
    )

    province: Mapped["Province"] = relationship(
        "Province",
        init=False,
        back_populates="job_postings"
    )

    city: Mapped["City"] = relationship(
        "City",
        init=False,
        back_populates="job_postings"
    )
