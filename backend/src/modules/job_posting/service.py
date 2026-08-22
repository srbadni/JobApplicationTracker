from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..company_membership.model import CompanyMembership
from .models import JobPosting
from .schemas import JobPostingRequest


class JobPostingService:
    async def create_job_posting(
            self,
            post: JobPostingRequest,
            db: AsyncSession,
            user_id: int
    ) -> JobPosting:
        company_membership: CompanyMembership | None = await db.scalar(
            select(CompanyMembership).where(
                CompanyMembership.user_id == user_id
            )
        )

        if company_membership is None:
            raise ValueError("Company membership not found")

        company_id = company_membership.company_id

        job_posting = JobPosting(
            **post.model_dump(),
            created_by_id=user_id,
            company_id=company_id,
        )

        db.add(job_posting)

        await db.commit()
        await db.refresh(job_posting)

        return job_posting
