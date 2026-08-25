"""Media service dependency provider."""

from typing import Annotated

from fastapi import Depends

from ...infrastructure.storage.dependencies import StorageDep
from .service import MediaService


def get_media_service(storage: StorageDep) -> MediaService:
    """Inject the configured storage backend into MediaService."""
    return MediaService(storage)


MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]
