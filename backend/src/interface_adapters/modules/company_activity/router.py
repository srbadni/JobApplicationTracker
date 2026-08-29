from fastapi import APIRouter, status

from .service import CompanyActivityServiceDep
from ..company_activity.schemas import CompanyActivityRead, CompanyActivityCreate

router = APIRouter(tags=["Company Activities"])

@router.get("", response_model=list[CompanyActivityRead])
async def get_activities(
        service: CompanyActivityServiceDep
):
    return await service.get_all()

@router.post("", response_model=CompanyActivityRead, status_code=status.HTTP_201_CREATED)
async def get_activities(
        activity: CompanyActivityCreate,
        service: CompanyActivityServiceDep
):
    return await service.create(activity)

@router.put("/{activity_id}", response_model=CompanyActivityRead | None, status_code=status.HTTP_200_OK)
async def get_activities(
        activity_id: int,
        activity: CompanyActivityCreate,
        service: CompanyActivityServiceDep
):
    return await service.update(activity, activity_id=activity_id)

@router.delete("/{activity_id}", response_model=CompanyActivityRead, status_code=status.HTTP_200_OK)
async def get_activities(
        activity_id: int,
        service: CompanyActivityServiceDep
):
    return await service.delete(activity_id=activity_id)