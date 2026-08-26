from pydantic import BaseModel, ConfigDict

class CompanyActivityCreate(BaseModel):
    code: str
    title: str

class CompanyActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str