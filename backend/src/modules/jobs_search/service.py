from typing import Sequence

from fastapi import Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..job_posting.models import WorkMode, RelevantWorkExperience, JobPosting


class JobsSearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_job_postings(
            self,
            keywords: str | None = None,
            province_ids: list[int] | None = None,
            job_category_ids: list[int] | None = None,
            work_modes: list[WorkMode] | None = None,
            work_experiences: list[RelevantWorkExperience] | None = None,
            salary_range_ids: list[int] | None = None,
    ):
        stmt = select(JobPosting)
        result = await self.db.execute(stmt)
        job_postings: Sequence[JobPosting] = result.scalars().all()
        return job_postings