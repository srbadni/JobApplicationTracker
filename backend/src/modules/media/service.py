import uuid
from collections.abc import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.storage import Storage
from ..common.exceptions import ResourceNotFoundError
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

    async def get(self, db: AsyncSession, media_id: int) -> Media:
        media = await db.get(Media, media_id)
        if media is None:
            raise ResourceNotFoundError(f"Media with ID {media_id} not found")
        return media

    async def download(self, db: AsyncSession, media_id: int) -> tuple[Media, bytes]:
        """Return private bytes; callers must authorize access before invoking this."""
        media = await self.get(db, media_id)
        return media, await self.storage.read(media.storage_key)

    async def delete(self, db: AsyncSession, media_id: int) -> None:
        media = await self.get(db, media_id)
        storage_key = media.storage_key
        await db.delete(media)
        await db.commit()
        await self.storage.delete(storage_key)
