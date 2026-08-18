from fastapi import APIRouter, status

from ...infrastructure.dependencies import AsyncSessionDep
from .dependencies import EmployerRegistrationServiceDep
from .schemas import EmployerRegistrationCreate, EmployerRegistrationRead

router = APIRouter(tags=["Employers"])


@router.post("", response_model=EmployerRegistrationRead, status_code=status.HTTP_201_CREATED)
async def register_employer(
    payload: EmployerRegistrationCreate,
    db: AsyncSessionDep,
    service: EmployerRegistrationServiceDep,
) -> EmployerRegistrationRead:
    """Create an employer, their company, and the owning membership together."""
    return await service.register(payload, db)
