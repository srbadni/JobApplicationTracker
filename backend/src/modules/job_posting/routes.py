from fastapi import APIRouter, status

from ...infrastructure.dependencies import AsyncSessionDep, CSRFTokenHeaderDep, CurrentUserDep
from .dependencies import JobPostingServiceDep
from .schemas import JobPostingRequest, JobPostingResponse

router = APIRouter()

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=JobPostingResponse,
)
async def create_job_posting(
    post: JobPostingRequest,
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
