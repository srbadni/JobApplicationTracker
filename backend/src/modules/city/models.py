from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database import Base

if TYPE_CHECKING:
    from ..job_posting.models import JobPosting
    from ..province.models import Province


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    english_name: Mapped[str] = mapped_column(String, nullable=False)

    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    province: Mapped["Province"] = relationship("Province", back_populates="cities", init=False)
    job_postings: Mapped["JobPosting"] = relationship(
        "JobPosting",
        init=False,
        back_populates="city"
    )
