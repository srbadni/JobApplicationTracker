from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError
from .crud import crud_companies
from .schemas import CompanyCreate, CompanyCreateInternal, CompanyRead


class CompanyService:
    """Coordinate company persistence and domain-level errors."""

    async def create(self, company: CompanyCreate, db: AsyncSession) -> dict[str, Any]:
        """Create and return a company profile."""
        company_internal = CompanyCreateInternal(**company.model_dump(mode="json"))
        created_company = await crud_companies.create(
            db=db,
            object=company_internal,
            schema_to_select=CompanyRead,
        )
        if not created_company:
            raise RuntimeError("Failed to create company")
        return created_company

    async def get_by_id(self, company_id: int, db: AsyncSession) -> dict[str, Any]:
        """Return a company profile by its system-generated ID."""
        company = await crud_companies.get(db=db, id=company_id, schema_to_select=CompanyRead)
        if not company:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        return company
