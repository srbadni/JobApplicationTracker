from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import dispose_engine


def create_app() -> FastAPI:
    """Build and configure a FastAPI application instance."""
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        dispose_engine()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
