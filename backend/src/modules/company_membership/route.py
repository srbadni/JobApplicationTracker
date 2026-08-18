from fastapi import APIRouter, status

from ...infrastructure.dependencies import AsyncSessionDep
from ..common.utils.error_handler import handle_exception
from .schemas import EmployerRegistrationCreate, EmployerRegistrationRead
from .service import EmployerRegistrationService

router = APIRouter(tags=["Employer registration"])


@router.post("/employer", status_code=status.HTTP_201_CREATED, response_model=EmployerRegistrationRead)
async def register_employer(payload: EmployerRegistrationCreate, db: AsyncSessionDep) -> EmployerRegistrationRead:
    """Create the employer and company together; a failure rolls back the request transaction."""
    try:
        return await EmployerRegistrationService().create(payload, db)
    except Exception as error:
        await db.rollback()
        http_exception = handle_exception(error)
        if http_exception:
            raise http_exception
        raise
