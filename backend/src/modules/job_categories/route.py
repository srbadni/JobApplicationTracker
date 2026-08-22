from fastapi import APIRouter

from .dependencies import JobCategoriesServiceDep
from .schemas import JobCategoriesResponse
from ...infrastructure.dependencies import AsyncSessionDep

router = APIRouter(tags=["Job Categories"])


@router.get("", response_model=list[JobCategoriesResponse])
async def get_job_categories(
        db: AsyncSessionDep,
        service: JobCategoriesServiceDep,
        query: str | None = None
):
    return await service.get_categories(db, query)
