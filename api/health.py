from fastapi import APIRouter
from pydantic import BaseModel

from common.schemas.response import ApiResponse

router = APIRouter(
    tags=["Health"],
)

class HealthResult(BaseModel):
    status: str
    service: str
    version: str

@router.get(
    "/health",
    response_model=ApiResponse[HealthResult],
)
def health_check():
    return ApiResponse(
        message="Service is healthy",
        result=HealthResult(
            status="ok",
            service="job-tracker-api",
            version="1.0.0",
        ),
    )