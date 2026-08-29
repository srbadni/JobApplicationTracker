"""Media upload, access-control, and lifecycle use cases."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ....frameworks.logging import get_logger
from ....frameworks.storage import Storage, StorageError, StorageLimitExceededError
from ..applicant_profile.models import ApplicantProfile
from ..user.enums import UserType
from .enums import MediaCategory
from .exceptions import MediaAccessDeniedError, MediaNotFoundError, MediaStorageError, MediaValidationError
from .models import Media
from .policies import MEDIA_POLICIES
from .schemas import MediaCategoryInfo
from .validation import UploadCandidate, validate_upload

logger = get_logger()


@dataclass(frozen=True, slots=True)
class MediaDownload:
    """Authorized metadata and byte stream for a download response."""

    filename: str
    mime_type: str
    size_bytes: int
    stream: AsyncIterator[bytes]


class MediaService:
    """Coordinate the database with a swappable object-storage backend."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def get_categories(self) -> list[MediaCategoryInfo]:
        """Describe the supported categories and their upload policies."""
        return [
            MediaCategoryInfo(
                category=category,
                max_size_bytes=policy.max_size_bytes,
                allowed_extensions=sorted(policy.file_types),
            )
            for category, policy in MEDIA_POLICIES.items()
        ]

    async def upload(
        self,
        *,
        db: AsyncSession,
        current_user: dict[str, Any],
        category: MediaCategory,
        upload: UploadCandidate,
    ) -> Media:
        """Store bytes and metadata, attaching resume uploads to ApplicantProfile."""
        self._ensure_category_permission(category, current_user)
        validated = await validate_upload(category, upload)
        storage_key = f"{uuid4().hex}{validated.extension}"

        try:
            stored = await self.storage.save(
                key=storage_key,
                source=upload,
                max_size_bytes=validated.max_size_bytes,
            )
        except StorageLimitExceededError as error:
            raise MediaValidationError(
                f"File exceeds the {error.limit_bytes // (1024 * 1024)} MiB limit for this category"
            ) from error
        except StorageError as error:
            raise MediaStorageError("The file could not be stored") from error

        if stored.size_bytes == 0:
            await self._cleanup_object(storage_key)
            raise MediaValidationError("Empty files are not allowed")

        media = Media(
            owner_id=current_user["id"],
            category=category.value,
            original_name=validated.original_name,
            storage_key=storage_key,
            mime_type=validated.mime_type,
            size_bytes=stored.size_bytes,
            checksum_sha256=stored.checksum_sha256,
        )
        replaced_storage_key: str | None = None

        try:
            db.add(media)
            await db.flush()

            if category is MediaCategory.RESUME:
                replaced_storage_key = await self._attach_resume(
                    db=db,
                    applicant_id=current_user["id"],
                    media=media,
                )

            await db.commit()
            await db.refresh(media)
        except (MediaAccessDeniedError, MediaValidationError):
            await db.rollback()
            await self._cleanup_object(storage_key)
            raise
        except SQLAlchemyError as error:
            await db.rollback()
            await self._cleanup_object(storage_key)
            raise MediaStorageError("The file metadata could not be saved") from error
        except Exception:
            await db.rollback()
            await self._cleanup_object(storage_key)
            raise

        if replaced_storage_key is not None:
            await self._cleanup_object(replaced_storage_key)

        return media

    async def download(
        self,
        *,
        db: AsyncSession,
        current_user: dict[str, Any],
        media_id: int,
    ) -> MediaDownload:
        """Authorize and stream one private media object."""
        media = await self._get_media(db, media_id)
        self._ensure_owner_or_superuser(media, current_user)

        try:
            exists = await self.storage.exists(media.storage_key)
        except StorageError as error:
            raise MediaStorageError("The stored file is currently unavailable") from error

        if not exists:
            logger.error(f"Media bytes missing for media_id={media.id}")
            raise MediaStorageError("The stored file is currently unavailable")

        return MediaDownload(
            filename=media.original_name,
            mime_type=media.mime_type,
            size_bytes=media.size_bytes,
            stream=self.storage.stream(media.storage_key),
        )

    async def delete(
        self,
        *,
        db: AsyncSession,
        current_user: dict[str, Any],
        media_id: int,
    ) -> None:
        """Delete owned metadata and then best-effort cleanup of its bytes."""
        media = await self._get_media(db, media_id)
        self._ensure_owner_or_superuser(media, current_user)
        storage_key = media.storage_key

        try:
            await db.execute(
                update(ApplicantProfile).where(ApplicantProfile.attached_resume_id == media.id).values(attached_resume_id=None)
            )
            await db.delete(media)
            await db.commit()
        except SQLAlchemyError as error:
            await db.rollback()
            raise MediaStorageError("The file metadata could not be deleted") from error

        await self._cleanup_object(storage_key)

    async def _attach_resume(self, *, db: AsyncSession, applicant_id: int, media: Media) -> str | None:
        profile = await db.scalar(
            select(ApplicantProfile).where(ApplicantProfile.applicant_id == applicant_id).with_for_update()
        )
        if profile is None:
            raise MediaAccessDeniedError("An applicant profile is required to upload a resume")

        previous_media_id = profile.attached_resume_id
        profile.attached_resume_id = media.id
        await db.flush()

        if previous_media_id is None:
            return None

        previous_media = await db.get(Media, previous_media_id)
        if previous_media is None:
            return None

        previous_storage_key = previous_media.storage_key
        await db.delete(previous_media)
        return previous_storage_key

    async def _get_media(self, db: AsyncSession, media_id: int) -> Media:
        media = await db.get(Media, media_id)
        if media is None:
            raise MediaNotFoundError(f"Media with ID {media_id} was not found")
        return media

    def _ensure_category_permission(self, category: MediaCategory, current_user: dict[str, Any]) -> None:
        user_type = current_user.get("user_type")
        if category is MediaCategory.RESUME and user_type != UserType.APPLICANT.value:
            raise MediaAccessDeniedError("Only applicants can upload resumes")
        if category is MediaCategory.COMPANY_LOGO and user_type != UserType.EMPLOYER.value:
            raise MediaAccessDeniedError("Only employers can upload company logos")

    @staticmethod
    def _ensure_owner_or_superuser(media: Media, current_user: dict[str, Any]) -> None:
        if media.owner_id != current_user.get("id") and not current_user.get("is_superuser", False):
            raise MediaAccessDeniedError("You do not have access to this file")

    async def _cleanup_object(self, storage_key: str) -> None:
        try:
            await self.storage.delete(storage_key)
        except StorageError:
            logger.exception(f"Failed to clean up storage object for key={storage_key}")
