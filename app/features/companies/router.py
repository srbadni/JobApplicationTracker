from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.features.companies.repository import CompanyRepository
from app.features.companies.schemas import CompanyCreate, CompanyResult
from app.features.companies.service import CompanyService
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post(
    "",
    response_model=ApiResponse[CompanyResult],
    status_code=status.HTTP_201_CREATED,
    summary="Create a company",
)
def create_company(
    payload: CompanyCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> ApiResponse[CompanyResult]:
    company = CompanyService(CompanyRepository(session)).create_company(payload)
    return ApiResponse(
        message="Company created successfully",
        result=CompanyResult.model_validate(company),
    )
