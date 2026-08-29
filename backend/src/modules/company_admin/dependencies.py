from typing import Annotated

from fastapi import Depends

from .service import CompanyAdminRegistrationService


def get_company_admin_registration_service() -> CompanyAdminRegistrationService:
    return CompanyAdminRegistrationService()


CompanyAdminRegistrationServiceDep = Annotated[
    CompanyAdminRegistrationService,
    Depends(get_company_admin_registration_service),
]
