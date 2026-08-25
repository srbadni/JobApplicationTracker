from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..job_application.models import JobApplication


class JobApplicationsFolder(Base):
    __tablename__ = "job_applications_folder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)

    job_applications: Mapped[list["JobApplication"]] = relationship("JobApplication", back_populates="folder", init=False)
