from fastapi import APIRouter, HTTPException, Response, status

from .schemas import SalaryRangeCreate, SalaryRangeRead
from .service import SalaryRangeServiceDep

router = APIRouter(tags=["Salary Ranges"])


@router.get("", response_model=list[SalaryRangeRead])
async def get_salary_ranges(service: SalaryRangeServiceDep):
    return await service.get_all()


@router.get("/{salary_range_id}", response_model=SalaryRangeRead)
async def get_salary_range(salary_range_id: int, service: SalaryRangeServiceDep):
    salary_range = await service.get(salary_range_id)
    if salary_range is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary range not found")
    return salary_range


@router.post("", response_model=SalaryRangeRead, status_code=status.HTTP_201_CREATED)
async def create_salary_range(salary_range: SalaryRangeCreate, service: SalaryRangeServiceDep):
    return await service.create(salary_range)


@router.put("/{salary_range_id}", response_model=SalaryRangeRead)
async def update_salary_range(
    salary_range_id: int,
    salary_range: SalaryRangeCreate,
    service: SalaryRangeServiceDep,
):
    updated_salary_range = await service.update(salary_range_id, salary_range)
    if updated_salary_range is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary range not found")
    return updated_salary_range


@router.delete("/{salary_range_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_range(salary_range_id: int, service: SalaryRangeServiceDep) -> Response:
    deleted_salary_range = await service.delete(salary_range_id)
    if deleted_salary_range is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary range not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
