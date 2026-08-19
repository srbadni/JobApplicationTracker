from typing import Annotated

from fastapi import Depends

from .service import EmployerRegistrationService


def get_employer_registration_service() -> EmployerRegistrationService:
    return EmployerRegistrationService()


EmployerRegistrationServiceDep = Annotated[
    EmployerRegistrationService,
    Depends(get_employer_registration_service),
]
