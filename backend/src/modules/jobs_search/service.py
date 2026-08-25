from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..job_posting.models import WorkMode, RelevantWorkExperience


class JobsSearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_jobs(
            self,
            keywords: str | None = None,
            province_ids: list[int] | None = Query(default=None),
            job_category_ids: list[int] | None = Query(default=None),
            work_modes: list[WorkMode] | None = Query(default=None),
            work_experiences: list[RelevantWorkExperience] | None = Query(default=None),
            salary_range_ids: list[int] | None = Query(default=None),
    ):
        pass