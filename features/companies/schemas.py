from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CompanyResponse(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    website: HttpUrl | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
