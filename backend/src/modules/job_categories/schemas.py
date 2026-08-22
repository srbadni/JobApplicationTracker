from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobCategoryWrite(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=255)]

    @field_validator("title")
    @classmethod
    def normalize_title(cls, title: str) -> str:
        """Reject whitespace-only titles and persist a normalized value."""
        title = title.strip()
        if not title:
            raise ValueError("title must not be blank")
        return title


class JobCategoryCreate(JobCategoryWrite):
    pass


class JobCategoryUpdate(JobCategoryWrite):
    pass


class JobCategoriesResponse(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)
