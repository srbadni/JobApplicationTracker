from pydantic import BaseModel, ConfigDict


class JobCategoriesResponse(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)