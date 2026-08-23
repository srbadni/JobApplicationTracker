from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...infrastructure.database import Base


class CompanyFolder(Base):
    __tablename__ = "company_folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[int] = mapped_column(String(120), nullable=False)
