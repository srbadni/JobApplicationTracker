from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import CompanyActivity
from .schemas import CompanyActivityCreate
from ...infrastructure.dependencies import AsyncSessionDep


class CompanyActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        stmt = select(CompanyActivity)
        result = await self.db.execute(stmt)
        all_items: Sequence[CompanyActivity] = result.scalars().all()
        return all_items

    async def create(self, activity: CompanyActivityCreate):
        new_company = CompanyActivity(**activity.model_dump())
        self.db.add(new_company)
        await self.db.commit()
        await self.db.refresh(new_company)
        return new_company

    async def update(self, activity_create: CompanyActivityCreate, activity_id: int):
        activity = await self.db.get(CompanyActivity, activity_id)

        if activity is None:
            return None

        data = activity_create.model_dump()

        for field, value in data.items():
            setattr(activity, field, value)

        await self.db.commit()
        await self.db.refresh(activity)

        return activity

    async def delete(self, activity_id: int):
        activity = await self.db.get(CompanyActivity, activity_id)

        if activity is None:
            return None

        await self.db.delete(activity)
        await self.db.commit()

        return activity

def get_company_activity_service(db: AsyncSessionDep):
    return CompanyActivityService(db=db)


CompanyActivityServiceDep = Annotated[CompanyActivityService, Depends(get_company_activity_service)]