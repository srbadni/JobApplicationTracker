from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Provide one database session per request and always close it."""
    with get_session_factory()() as session:
        yield session


def dispose_engine() -> None:
    """Release pooled connections when the application shuts down."""
    if get_engine.cache_info().currsize:
        get_engine().dispose()
