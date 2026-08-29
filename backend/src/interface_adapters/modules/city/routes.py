from fastapi import APIRouter, HTTPException, Response, status

from ....frameworks.dependencies import AsyncSessionDep, CurrentSuperUserDep
from ..common.exceptions import ResourceExistsError, ResourceNotFoundError, ValidationError
from .dependencies import CityServiceDep
from .schemas import CityCreate, CityResponse, CityUpdate

router = APIRouter(tags=["Cities"])


@router.get("", response_model=list[CityResponse])
async def get_cities(
    db: AsyncSessionDep,
    service: CityServiceDep,
    query: str | None = None,
    province_id: int | None = None,
):
    return await service.get_cities(db, query, province_id)


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(city_id: int, db: AsyncSessionDep, service: CityServiceDep):
    try:
        return await service.get_city(db, city_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(
    city: CityCreate,
    db: AsyncSessionDep,
    service: CityServiceDep,
    _: CurrentSuperUserDep,
):
    try:
        return await service.create_city(db, city)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ResourceExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.put("/{city_id}", response_model=CityResponse)
async def update_city(
    city_id: int,
    city: CityUpdate,
    db: AsyncSessionDep,
    service: CityServiceDep,
    _: CurrentSuperUserDep,
):
    try:
        return await service.update_city(db, city_id, city)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ResourceExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(
    city_id: int,
    db: AsyncSessionDep,
    service: CityServiceDep,
    _: CurrentSuperUserDep,
) -> Response:
    try:
        await service.delete_city(db, city_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
