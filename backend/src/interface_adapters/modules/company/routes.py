from fastapi import APIRouter, HTTPException, status

from ....domain.company import Company, CompanyNotFoundError
from ..common.utils.error_handler import handle_exception
from .dependencies import GetCompanyByTitleDep
from .schemas import CompanyRead

router = APIRouter(tags=["Companies"])

@router.get("/{company_title}", response_model=CompanyRead)
async def get_company_by_title(
    company_title: str,
    get_company: GetCompanyByTitleDep,
) -> Company:
    try:
        return await get_company.execute(company_title)
    except CompanyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    except Exception as error:
        http_exception = handle_exception(error)
        if http_exception:
            raise http_exception
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
