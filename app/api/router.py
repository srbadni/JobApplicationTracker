from fastapi import APIRouter

from app.features.companies.router import router as companies_router
from app.features.health.router import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(companies_router)
