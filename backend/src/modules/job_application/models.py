from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..user.models import User
    from ..job_posting.models import JobPosting
    from ..job_applications_folder.models import JobApplicationsFolder


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    folder_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("job_applications_folder.id"), nullable=True)
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_postings.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    applicant: Mapped["User"] = relationship("User", back_populates="job_applications", init=False)
    job_posting: Mapped["JobPosting"] = relationship("JobPosting", back_populates="job_applications", init=False)
    folder: Mapped["JobApplicationsFolder | None"] = relationship("JobApplicationsFolder", back_populates="job_applications", init=False)