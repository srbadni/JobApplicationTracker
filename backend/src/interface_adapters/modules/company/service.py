from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError
from .crud import crud_companies
from .schemas import CompanyRead


class CompanyService:

    async def get_by_title(self, company_title: str, db: AsyncSession) -> dict[str, Any]:
        company = await crud_companies.get(db=db, name=company_title, schema_to_select=CompanyRead)
        if not company:
            raise ResourceNotFoundError(f"Company with title {company_title} not found")
        return company
