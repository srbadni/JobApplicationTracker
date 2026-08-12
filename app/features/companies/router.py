from typing import Annotated, List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.features.companies.repository import CompanyRepository
from app.features.companies.schemas import CompanyCreate, CompanyResult
from app.features.companies.service import CompanyService
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=ApiResponse[List[CompanyResult]], summary="Get all companies")
def get_all_companies(session: Annotated[Session, Depends(get_db_session)]):
    companies = CompanyService(CompanyRepository(session)).list_companies()
    return ApiResponse(
        result=[
            CompanyResult.model_validate(company)
            for company in companies
        ]
    )

@router.get("/{company_id}", response_model=ApiResponse[CompanyResult], summary="Get company")
def get_company_by_id(company_id: int, session: Annotated[Session, Depends(get_db_session)]):
    company = CompanyService(CompanyRepository(session)).get_company_by_id(company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return ApiResponse(
        result=CompanyResult.model_validate(company)
    )

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
        result=CompanyResult.model_validate(company),
    )
