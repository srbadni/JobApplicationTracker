from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from ..company.enums import EmployeeCount


class CompanyCreate(BaseModel):
    """Payload accepted when creating a company."""

    name: Annotated[str, Field(min_length=2, max_length=120)]
    persian_name: Annotated[str, Field(min_length=2, max_length=120)]
    province_id: Annotated[int, Field(gt=0)]
    city_id: Annotated[int, Field(gt=0)]
    activity_id: Annotated[int, Field(gt=0)]
    personnel_count: Annotated[EmployeeCount, Field()]
    logo_path: str | None = None
    phone_number: Annotated[
        str,
        Field(
            pattern=r"^09\d{9}$",
            examples=["09123456789"],
            description="Iranian mobile number in 09XXXXXXXXX format",
        ),
    ]
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


class CompanyRead(BaseModel):
    """Public representation of a persisted company."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    persian_name: str
    province_id: int
    city_id: int
    activity_id: int
    personnel_count: EmployeeCount
    logo_path: str | None
    phone_number: str
    description: str | None
    website: HttpUrl | None
    created_at: datetime
    updated_at: datetime
