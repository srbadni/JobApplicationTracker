from fastapi import APIRouter, status

from ..job_posting.dependencies import JobPostingServiceDep
from ..job_posting.schemas import JobPostingRead, JobPostingCreate
from ....frameworks.dependencies import AsyncSessionDep, CurrentUserDep, CSRFTokenHeaderDep
from .dependencies import CompanyAdminRegistrationServiceDep
from .schemas import CompanyAdminRegistration, CompanyAdminRegistrationRead

router = APIRouter(tags=["Company Admin"])


@router.post(
    "/register",
    response_model=CompanyAdminRegistrationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register an employer and company",
)
async def register_company_admin(
    payload: CompanyAdminRegistration,
    db: AsyncSessionDep,
    registration_service: CompanyAdminRegistrationServiceDep,
) -> CompanyAdminRegistrationRead:
    return await registration_service.create(payload, db)


@router.post(
    "/create-job-posting",
    status_code=status.HTTP_201_CREATED,
    response_model=JobPostingRead,
)
async def create_job_posting(
    post: JobPostingCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    service: JobPostingServiceDep,
    csrf_token_header: CSRFTokenHeaderDep = None,
):
    return await service.create_job_posting(
        db=db,
        user_id=current_user["id"],
        post=post,
    )
