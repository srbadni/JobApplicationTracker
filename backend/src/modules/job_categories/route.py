from fastapi import APIRouter

from ...infrastructure.dependencies import AsyncSessionDep
from .dependencies import JobCategoriesServiceDep
from .schemas import JobCategoriesResponse

router = APIRouter(tags=["Job Categories"])


@router.get("", response_model=list[JobCategoriesResponse])
async def get_job_categories(
        db: AsyncSessionDep,
        service: JobCategoriesServiceDep,
        query: str | None = None
):
    return await service.get_categories(db, query)
