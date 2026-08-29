from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....frameworks.dependencies import AsyncSessionDep
from .model import SalaryRange
from .schemas import SalaryRangeCreate


class SalaryRangeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[SalaryRange]:
        result = await self.db.execute(select(SalaryRange).order_by(SalaryRange.id))
        return result.scalars().all()

    async def get(self, salary_range_id: int) -> SalaryRange | None:
        return await self.db.get(SalaryRange, salary_range_id)

    async def create(self, salary_range: SalaryRangeCreate) -> SalaryRange:
        new_salary_range = SalaryRange(**salary_range.model_dump())
        self.db.add(new_salary_range)
        await self.db.commit()
        await self.db.refresh(new_salary_range)
        return new_salary_range

    async def update(self, salary_range_id: int, salary_range: SalaryRangeCreate) -> SalaryRange | None:
        existing_salary_range = await self.get(salary_range_id)
        if existing_salary_range is None:
            return None

        for field, value in salary_range.model_dump().items():
            setattr(existing_salary_range, field, value)

        await self.db.commit()
        await self.db.refresh(existing_salary_range)
        return existing_salary_range

    async def delete(self, salary_range_id: int) -> SalaryRange | None:
        salary_range = await self.get(salary_range_id)
        if salary_range is None:
            return None

        await self.db.delete(salary_range)
        await self.db.commit()
        return salary_range


def get_salary_range_service(db: AsyncSessionDep) -> SalaryRangeService:
    return SalaryRangeService(db=db)


SalaryRangeServiceDep = Annotated[SalaryRangeService, Depends(get_salary_range_service)]
