import uuid
from collections.abc import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.storage import Storage
from ..common.exceptions import PermissionDeniedError, ResourceNotFoundError
from .models import Media
from .schemas import MediaCreate


class MediaService:
    """Coordinate media metadata with a replaceable storage backend."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    async def upload(
        self,
        db: AsyncSession,
        metadata: MediaCreate,
        content: AsyncIterable[bytes],
        uploaded_by_id: int | None = None,
    ) -> Media:
        storage_key = uuid.uuid4().hex
        size = await self.storage.save(storage_key, content)
        media = Media(
            category=metadata.category.value,
            original_name=metadata.original_name,
            storage_key=storage_key,
            mime_type=metadata.mime_type,
            size=size,
            uploaded_by_id=uploaded_by_id,
        )
        db.add(media)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            await self.storage.delete(storage_key)
            raise
        await db.refresh(media)
        return media

    async def get(
        self,
        db: AsyncSession,
        media_id: int,
        requester_id: int,
        is_superuser: bool = False,
    ) -> Media:
        media = await db.get(Media, media_id)
        if media is None:
            raise ResourceNotFoundError(f"Media with ID {media_id} not found")
        self._ensure_access(media, requester_id, is_superuser)
        return media

    async def download(
        self,
        db: AsyncSession,
        media_id: int,
        requester_id: int,
        is_superuser: bool = False,
    ) -> tuple[Media, bytes]:
        """Return private bytes to the uploader or a superuser."""
        media = await self.get(db, media_id, requester_id, is_superuser)
        return media, await self.storage.read(media.storage_key)

    async def delete(
        self,
        db: AsyncSession,
        media_id: int,
        requester_id: int,
        is_superuser: bool = False,
    ) -> None:
        media = await self.get(db, media_id, requester_id, is_superuser)
        storage_key = media.storage_key
        await db.delete(media)
        await db.commit()
        await self.storage.delete(storage_key)

    @staticmethod
    def _ensure_access(media: Media, requester_id: int, is_superuser: bool) -> None:
        if not is_superuser and media.uploaded_by_id != requester_id:
            raise PermissionDeniedError("You do not have access to this media")
