from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings
from db.base import Base

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)


SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables() -> None:
    """Create database tables that do not already exist.

    Importing the model modules registers their tables on ``Base.metadata`` before
    SQLAlchemy emits the PostgreSQL DDL.
    """
    from features.companies import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
