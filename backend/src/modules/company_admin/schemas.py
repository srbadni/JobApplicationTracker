from pydantic import BaseModel, ConfigDict

from ..company.schemas import CompanyCreate, CompanyRead
from ..user.schemas import UserCreate, UserRead


class CompanyAdminRegistration(BaseModel):

    model_config = ConfigDict(extra="forbid")

    user: UserCreate
    company: CompanyCreate


class CompanyAdminRegistrationRead(BaseModel):

    user: UserRead
    company: CompanyRead
