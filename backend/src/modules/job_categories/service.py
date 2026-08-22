from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..job_categories.models import JobCategory


class JobCategoriesService:
    async def get_categories(self, db: AsyncSession, query: str | None) -> Sequence[JobCategory]:
        stmt = select(JobCategory)

        if query:
            stmt = stmt.where(
                JobCategory.title.ilike(f"%{query}%")
            )

        result = await db.scalars(stmt)

        return result.all()