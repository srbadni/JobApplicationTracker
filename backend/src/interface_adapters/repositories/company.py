from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.company import Company
from ..modules.company.models import Company as CompanyRecord


class SqlAlchemyCompanyReader:
    """Translate SQLAlchemy records to domain entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_title(self, title: str) -> Company | None:
        record = await self._session.scalar(select(CompanyRecord).where(CompanyRecord.name == title))
        if record is None:
            return None
        return Company(
            id=record.id,
            name=record.name,
            persian_name=record.persian_name,
            province_id=record.province_id,
            city_id=record.city_id,
            activity_id=record.activity_id,
            personnel_count=record.personnel_count.value,
            logo_path=record.logo_path,
            phone_number=record.phone_number,
            description=record.description,
            website=record.website,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
