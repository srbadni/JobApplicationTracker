from fastapi import APIRouter, Query

from .dependencies import JobsSearchServiceDep
from ..job_posting.enums import WorkMode, RelevantWorkExperience

router = APIRouter(tags=["Jobs Search"])


@router.get("/")
async def get_jobs(
        service: JobsSearchServiceDep,
        keywords: str | None = None,
        province_ids: list[int] | None = Query(default=None),
        job_category_ids: list[int] | None = Query(default=None),
        work_modes: list[WorkMode] | None = Query(default=None),
        work_experiences: list[RelevantWorkExperience] | None = Query(default=None),
        salary_range_ids: list[int] | None = Query(default=None),
):
    return service.get_jobs(
        keywords,
        province_ids,
        job_category_ids,
        work_modes,
        work_experiences,
        salary_range_ids,
    )
