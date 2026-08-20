from fastapi import APIRouter, status

from ...infrastructure.dependencies import AsyncSessionDep
from .dependencies import EmployerRegistrationServiceDep
from .schemas import EmployerRegistration, EmployerRegistrationRead

from ..job_posting.routes import router as job_posting_router

router = APIRouter(tags=["Employers"])

@router.post(
    "/register",
    response_model=EmployerRegistrationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register an employer and company",
)
async def register_employer(
    payload: EmployerRegistration,
    db: AsyncSessionDep,
    registration_service: EmployerRegistrationServiceDep,
) -> EmployerRegistrationRead:
    """Atomically create the employer, company, and founder membership."""
    return await registration_service.create(payload, db)

router.include_router(job_posting_router)