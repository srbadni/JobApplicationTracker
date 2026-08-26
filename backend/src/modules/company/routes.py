from typing import Any

from fastapi import APIRouter, HTTPException, status

from ...infrastructure.dependencies import AsyncSessionDep
from ..common.exceptions import ResourceNotFoundError
from ..common.utils.error_handler import handle_exception
from .dependencies import CompanyServiceDep
from .schemas import CompanyRead

router = APIRouter(tags=["Companies"])

@router.get("/{company_title}", response_model=CompanyRead)
async def get_company_by_title(
    company_title: str,
    db: AsyncSessionDep,
    company_service: CompanyServiceDep,
) -> dict[str, Any]:
    try:
        return await company_service.get_by_title(company_title, db)
    except ResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    except Exception as error:
        http_exception = handle_exception(error)
        if http_exception:
            raise http_exception
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
