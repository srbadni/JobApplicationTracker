from fastapi import APIRouter, HTTPException, Response, status

from ....frameworks.dependencies import AsyncSessionDep, CurrentSuperUserDep
from ..common.exceptions import ResourceExistsError, ResourceNotFoundError, ValidationError
from .dependencies import JobCategoriesServiceDep
from .schemas import JobCategoriesResponse, JobCategoryCreate, JobCategoryUpdate

router = APIRouter(tags=["Job Categories"])


@router.get("", response_model=list[JobCategoriesResponse])
async def get_job_categories(
    db: AsyncSessionDep,
    service: JobCategoriesServiceDep,
    query: str | None = None,
):
    return await service.get_categories(db, query)


@router.post("", response_model=JobCategoriesResponse, status_code=status.HTTP_201_CREATED)
async def create_job_category(
    category: JobCategoryCreate,
    db: AsyncSessionDep,
    service: JobCategoriesServiceDep,
    _: CurrentSuperUserDep,
):
    try:
        return await service.create_category(db, category)
    except ResourceExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.put("/{category_id}", response_model=JobCategoriesResponse)
async def update_job_category(
    category_id: int,
    category: JobCategoryUpdate,
    db: AsyncSessionDep,
    service: JobCategoriesServiceDep,
    _: CurrentSuperUserDep,
):
    try:
        return await service.update_category(db, category_id, category)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ResourceExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_category(
    category_id: int,
    db: AsyncSessionDep,
    service: JobCategoriesServiceDep,
    _: CurrentSuperUserDep,
) -> Response:
    try:
        await service.delete_category(db, category_id)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
