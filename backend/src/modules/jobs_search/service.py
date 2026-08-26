from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..city.models import City
from ..company.models import Company
from ..job_categories.models import JobCategory
from ..job_posting.models import JobPosting, RelevantWorkExperience, WorkMode
from ..province.models import Province
from ..salary_range.model import SalaryRange
from .schemas import JobSearchRead


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
    ) -> list[JobSearchRead]:
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

        stmt = (
            select(
                *JobPosting.__table__.c,
                Company.name.label("company_title"),
                JobCategory.title.label("job_category_title"),
                Province.name.label("province_title"),
                SalaryRange.title.label("salary_range_title"),
                City.name.label("city_title"),
            )
            .join(Company, JobPosting.company_id == Company.id)
            .join(JobCategory, JobPosting.job_category_id == JobCategory.id)
            .join(Province, JobPosting.province_id == Province.id)
            .join(SalaryRange, JobPosting.salary_range_id == SalaryRange.id)
            .join(City, JobPosting.city_id == City.id)
            .where(*filters)
        )
        result = await self.db.execute(stmt)
        return [JobSearchRead.model_validate(row) for row in result.mappings().all()]
