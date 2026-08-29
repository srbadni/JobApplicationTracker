"""Media API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .enums import MediaCategory


class MediaResponse(BaseModel):
    """Safe media metadata; the internal storage key is intentionally omitted."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category: MediaCategory
    original_name: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    created_at: datetime
    updated_at: datetime | None


class MediaCategoryInfo(BaseModel):
    """Upload capabilities exposed to API clients."""

    category: MediaCategory
    max_size_bytes: int
    allowed_extensions: list[str]
