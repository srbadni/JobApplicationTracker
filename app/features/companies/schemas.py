from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    website: AnyHttpUrl | None = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class CompanyResult(BaseModel):
    id: int
    name: str
    description: str | None
    website: AnyHttpUrl | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
