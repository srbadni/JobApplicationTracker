from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..company.models import Company
    from ..job_posting.models import JobPosting
    from ..province.models import Province


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    english_name: Mapped[str] = mapped_column(String, nullable=False)

    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    province: Mapped["Province"] = relationship("Province", back_populates="cities", init=False)
    job_postings: Mapped[list["JobPosting"]] = relationship("JobPosting", init=False, back_populates="city")
    companies: Mapped[list["Company"]] = relationship("Company", init=False, back_populates="city")
