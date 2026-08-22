from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CityWrite(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    english_name: Annotated[str, Field(min_length=1, max_length=255)]
    province_id: Annotated[int, Field(gt=0)]

    @field_validator("name", "english_name")
    @classmethod
    def normalize_names(cls, value: str) -> str:
        """Reject blank names and store names without surrounding whitespace."""
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class CityCreate(CityWrite):
    pass


class CityUpdate(CityWrite):
    pass


class CityResponse(CityWrite):
    id: int

    model_config = ConfigDict(from_attributes=True)
