from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database import Base

if TYPE_CHECKING:
    from ..user.models import User
    from ..job_posting.models import JobPosting
    from ..resume.models import Resume


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_postings.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    applicant: Mapped["User"] = relationship("User", back_populates="job_applications", init=False)
    job_posting: Mapped["JobPosting"] = relationship("JobPosting", back_populates="job_applications", init=False)
    resume: Mapped["Resume"] = relationship("Resume", back_populates="job_applications", init=False)