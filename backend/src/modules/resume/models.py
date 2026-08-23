from typing import TYPE_CHECKING, Literal

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database import Base

if TYPE_CHECKING:
    from ..user.models import User
    from ..job_application.models import JobApplication


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Literal["uploaded", "builder"]] = mapped_column(String(20), nullable=False)

    applicant: Mapped["User"] = relationship("User", back_populates="resumes", init=False)
    job_applications: Mapped["JobApplication"] = relationship("JobApplication", back_populates="resume", init=False)