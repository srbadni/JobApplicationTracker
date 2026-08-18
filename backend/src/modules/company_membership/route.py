from fastapi import APIRouter, status

router = APIRouter(prefix="/company_membership")

@router.post("", status_code=status.HTTP_201_CREATED)
def add_company_membership():
    pass