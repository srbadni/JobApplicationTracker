from typing import Annotated

from fastapi import Depends

from .service import CompanyService


def get_company_service() -> CompanyService:
    """Provide the company application service."""
    return CompanyService()


CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
