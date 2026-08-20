from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import PermissionDeniedError
from ..company_membership.model import CompanyMembership
from .models import JobPosting
from .schemas import JobPostingRequest


class JobPostingService:
    async def create_job_posting(
        self,
        post: JobPostingRequest,
        db: AsyncSession,
        company_id: int,
        user_id: int,
    ) -> JobPosting:
        company_membership: CompanyMembership | None = await db.scalar(
            select(CompanyMembership).where(
                CompanyMembership.user_id == user_id,
                CompanyMembership.company_id == company_id,
            )
        )

        if company_membership is None or not company_membership.is_admin:
            raise PermissionDeniedError("Only company administrators can create job postings")

        job_posting = JobPosting(
            **post.model_dump(),
            company_id=company_id,
        )

        db.add(job_posting)

        await db.commit()
        await db.refresh(job_posting)

        return job_posting
