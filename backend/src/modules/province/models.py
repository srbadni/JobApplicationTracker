from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database import Base

if TYPE_CHECKING:
    from ..city.models import City
    from ..job_posting.models import JobPosting
    from ..company.models import Company


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    english_name: Mapped[str] = mapped_column(String, nullable=False)

    cities: Mapped["City"] = relationship("City", init=False, back_populates="province")
    job_postings: Mapped["JobPosting"] = relationship("JobPosting", init=False, back_populates="province")
    companies: Mapped["Company"] = relationship("Company", init=False, back_populates="province")
