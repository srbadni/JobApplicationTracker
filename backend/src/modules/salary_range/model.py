from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database import Base

if TYPE_CHECKING:
    from ..job_posting.models import JobPosting


class SalaryRange(Base):
    __tablename__ = "salary_ranges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    min_salary: Mapped[int | None] = mapped_column(Integer, default=None)
    max_salary: Mapped[int | None] = mapped_column(Integer, default=None)

    job_postings: Mapped[list["JobPosting"]] = relationship("JobPosting", back_populates="salary_range", init=False)
