from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError
from .crud import crud_companies
from .schemas import CompanyRead


class CompanyService:
    """Coordinate company persistence and domain-level errors."""

    async def get_by_id(self, company_id: int, db: AsyncSession) -> dict[str, Any]:
        """Return a company profile by its system-generated ID."""
        company = await crud_companies.get(db=db, id=company_id, schema_to_select=CompanyRead)
        if not company:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        return company
