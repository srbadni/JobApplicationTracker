from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..job_posting.models import JobPosting, RelevantWorkExperience, WorkMode


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
        filters = []

        if keywords:
            filters.append(JobPosting.job_title.ilike(f"%{keywords}%"))
        if province_ids:
            filters.append(JobPosting.province_id.in_(province_ids))
        if job_category_ids:
            filters.append(JobPosting.job_category_id.in_(job_category_ids))
        if work_modes:
            filters.append(JobPosting.work_mode.in_(work_modes))
        if work_experiences:
            filters.append(JobPosting.work_experience.in_(work_experiences))
        if salary_range_ids:
            filters.append(JobPosting.salary_range_id.in_(salary_range_ids))

        stmt = select(JobPosting).where(*filters)
        result = await self.db.execute(stmt)
        job_postings: Sequence[JobPosting] = result.scalars().all()
        return job_postings
