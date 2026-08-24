from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...infrastructure.database import Base


class JobApplicationsFolder(Base):
    __tablename__ = "job_applications_folder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
