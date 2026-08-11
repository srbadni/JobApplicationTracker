from fastapi import APIRouter

from api.health import router as health_router
from core.config import settings
from features.companies.router import router as companies_router

api_router = APIRouter(
    prefix=settings.api_v1_prefix,
)

api_router.include_router(health_router)
api_router.include_router(companies_router)
