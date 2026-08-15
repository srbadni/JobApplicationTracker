from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class CompanyCreate(BaseModel):
    """Payload accepted when creating a company."""

    name: Annotated[str, Field(min_length=2, max_length=120)]
    description: Annotated[str | None, Field(max_length=2000)] = None
    website: HttpUrl | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_and_validate_name(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("name must not be blank")
        return value


class CompanyCreateInternal(BaseModel):
    """Normalized company data passed to the persistence layer."""

    name: str
    description: str | None = None
    website: str | None = None


class CompanyRead(BaseModel):
    """Public representation of a persisted company."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    website: HttpUrl | None
    created_at: datetime
    updated_at: datetime
