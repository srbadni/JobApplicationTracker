from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.config import Settings, get_settings
from app.features.health.schemas import HealthResult
from app.features.health.service import get_health
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=ApiResponse[HealthResult],
    status_code=status.HTTP_200_OK,
    summary="Check service health",
)
def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ApiResponse[HealthResult]:
    return ApiResponse(
        result=get_health(settings),
    )
