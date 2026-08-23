from typing import Annotated

from fastapi import Depends

from ...infrastructure.config.settings import settings
from ...infrastructure.storage import LocalStorage, Storage
from .service import MediaService


def get_storage() -> Storage:
    return LocalStorage(settings.STORAGE_UPLOAD_DIR)


def get_media_service(storage: Annotated[Storage, Depends(get_storage)]) -> MediaService:
    return MediaService(storage)


MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]
