from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..company.models import Company


class CompanyActivity(Base):
    __tablename__ = "company_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)

    companies: Mapped[list["Company"]] = relationship("Company", back_populates="activity", init=False)
