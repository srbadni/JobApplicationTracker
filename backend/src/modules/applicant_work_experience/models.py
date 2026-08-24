from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String, Text, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..applicant_profile.models import ApplicantProfile


class WorkExperience(Base):
    __tablename__ = "work_experiences"
    __table_args__ = (
        CheckConstraint(
            "(is_current = true AND end_month IS NULL AND end_year IS NULL) "
            "OR (is_current = false AND end_month IS NOT NULL AND end_year IS NOT NULL) "
            "OR (is_current IS NULL)",
            name="ck_work_experience_end_date_consistency",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("applicant_profiles.id"))

    position_title: Mapped[str] = mapped_column(String(200))
    workplace_name: Mapped[str] = mapped_column(String)

    start_month: Mapped[int] = mapped_column(Integer)
    start_year: Mapped[int] = mapped_column(Integer)
    end_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_current: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    experience_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    applicant: Mapped["ApplicantProfile"] = relationship("ApplicantProfile", back_populates="work_experiences", init=False)