from typing import Any

from fastapi import APIRouter, HTTPException, status

from ...infrastructure.dependencies import AsyncSessionDep
from ..common.exceptions import ResourceNotFoundError
from ..common.utils.error_handler import handle_exception
from .dependencies import CompanyServiceDep
from .schemas import CompanyCreate, CompanyRead

router = APIRouter()

@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int,
    db: AsyncSessionDep,
    company_service: CompanyServiceDep,
) -> dict[str, Any]:
    """Return a company profile by its system-generated ID."""
    try:
        return await company_service.get_by_id(company_id, db)
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    except Exception as error:
        http_exception = handle_exception(error)
        if http_exception:
            raise http_exception
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
