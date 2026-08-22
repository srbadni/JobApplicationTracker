from fastapi import APIRouter, HTTPException, Response, status

from ...infrastructure.dependencies import AsyncSessionDep, CurrentSuperUserDep
from ..common.exceptions import ResourceExistsError, ResourceNotFoundError, ValidationError
from .dependencies import ProvinceServiceDep
from .schemas import ProvinceCreate, ProvinceResponse, ProvinceUpdate

router = APIRouter(tags=["Provinces"])


@router.get("", response_model=list[ProvinceResponse])
async def get_provinces(db: AsyncSessionDep, service: ProvinceServiceDep, query: str | None = None):
    return await service.get_provinces(db, query)


@router.get("/{province_id}", response_model=ProvinceResponse)
async def get_province(province_id: int, db: AsyncSessionDep, service: ProvinceServiceDep):
    try:
        return await service.get_province(db, province_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("", response_model=ProvinceResponse, status_code=status.HTTP_201_CREATED)
async def create_province(
    province: ProvinceCreate,
    db: AsyncSessionDep,
    service: ProvinceServiceDep,
    _: CurrentSuperUserDep,
):
    try:
        return await service.create_province(db, province)
    except ResourceExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.put("/{province_id}", response_model=ProvinceResponse)
async def update_province(
    province_id: int,
    province: ProvinceUpdate,
    db: AsyncSessionDep,
    service: ProvinceServiceDep,
    _: CurrentSuperUserDep,
):
    try:
        return await service.update_province(db, province_id, province)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ResourceExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.delete("/{province_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_province(
    province_id: int,
    db: AsyncSessionDep,
    service: ProvinceServiceDep,
    _: CurrentSuperUserDep,
) -> Response:
    try:
        await service.delete_province(db, province_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
