from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ...infrastructure.dependencies import AsyncSessionDep
from .models import Company
from .schemas import CompanyCreate, CompanyRead

router = APIRouter(tags=["Companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSessionDep) -> Company:
    """Create and persist a company profile."""
    company = Company(
        name=payload.name,
        description=payload.description,
        website=str(payload.website) if payload.website is not None else None,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int, db: AsyncSessionDep) -> Company:
    """Return a company profile by its system-generated ID."""
    company = await db.scalar(select(Company).where(Company.id == company_id))
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company
