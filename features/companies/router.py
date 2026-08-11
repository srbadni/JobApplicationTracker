from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.schemas.response import ApiResponse
from db.database import get_db
from features.companies.models import Company
from features.companies.schemas import CompanyResponse

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("", response_model=ApiResponse[list[CompanyResponse]])
async def get_companies(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApiResponse[list[CompanyResponse]]:
    companies = (await session.scalars(select(Company).order_by(Company.id))).all()

    return ApiResponse(
        message="Companies retrieved successfully",
        result=[CompanyResponse.model_validate(company) for company in companies],
    )
