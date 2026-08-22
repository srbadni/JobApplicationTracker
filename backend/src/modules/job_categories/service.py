from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceExistsError, ResourceNotFoundError, ValidationError
from ..job_categories.models import JobCategory
from .schemas import JobCategoryCreate, JobCategoryUpdate


class JobCategoriesService:
    async def get_categories(self, db: AsyncSession, query: str | None) -> Sequence[JobCategory]:
        stmt = select(JobCategory)

        if query:
            stmt = stmt.where(
                JobCategory.title.ilike(f"%{query}%")
            )

        result = await db.scalars(stmt)

        return result.all()

    async def create_category(self, db: AsyncSession, category: JobCategoryCreate) -> JobCategory:
        await self._ensure_unique_title(db, category.title)

        # SQLAlchemy supplies the generated primary key and relationship collection.
        job_category = JobCategory(title=category.title)  # type: ignore[call-arg]
        db.add(job_category)
        await db.commit()
        await db.refresh(job_category)
        return job_category

    async def update_category(
        self,
        db: AsyncSession,
        category_id: int,
        category: JobCategoryUpdate,
    ) -> JobCategory:
        job_category = await self._get_by_id(db, category_id)
        await self._ensure_unique_title(db, category.title, exclude_id=category_id)

        job_category.title = category.title
        await db.commit()
        await db.refresh(job_category)
        return job_category

    async def delete_category(self, db: AsyncSession, category_id: int) -> None:
        job_category = await self._get_by_id(db, category_id)
        await db.delete(job_category)
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ValidationError("Job category is in use and cannot be deleted") from error

    async def _get_by_id(self, db: AsyncSession, category_id: int) -> JobCategory:
        job_category = await db.get(JobCategory, category_id)
        if job_category is None:
            raise ResourceNotFoundError(f"Job category with ID {category_id} not found")
        return job_category

    async def _ensure_unique_title(
        self,
        db: AsyncSession,
        title: str,
        exclude_id: int | None = None,
    ) -> None:
        stmt = select(JobCategory.id).where(JobCategory.title.ilike(title))
        if exclude_id is not None:
            stmt = stmt.where(JobCategory.id != exclude_id)
        if await db.scalar(stmt) is not None:
            raise ResourceExistsError(f"Job category with title '{title}' already exists")
