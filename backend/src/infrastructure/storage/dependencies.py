"""FastAPI dependency provider for the configured storage backend."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from ..config.enums import StorageBackend
from ..config.settings import settings
from .base import Storage
from .local import LocalStorage


@lru_cache
def get_storage() -> Storage:
    """Build the configured storage backend once per process."""
    if settings.STORAGE_BACKEND == StorageBackend.LOCAL.value:
        return LocalStorage(
            root=settings.LOCAL_STORAGE_ROOT,
            chunk_size_bytes=settings.STORAGE_CHUNK_SIZE_BYTES,
        )

    raise RuntimeError(f"Unsupported storage backend: {settings.STORAGE_BACKEND}")


StorageDep = Annotated[Storage, Depends(get_storage)]
