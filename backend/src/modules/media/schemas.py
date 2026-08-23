from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import MediaCategory


class MediaCreate(BaseModel):
    """Metadata supplied with a new upload."""

    category: MediaCategory
    original_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=255)


class MediaRead(BaseModel):
    """Persisted media metadata; deliberately excludes a public file URL."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category: MediaCategory
    original_name: str
    mime_type: str
    size: int
    uploaded_by_id: int | None
    created_at: datetime
    updated_at: datetime | None
