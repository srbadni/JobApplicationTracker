from pydantic import BaseModel, ConfigDict

from ..company.schemas import CompanyCreate, CompanyRead
from ..user.schemas import UserCreate, UserRead


class EmployerRegistrationCreate(BaseModel):
    """The two frontend registration steps represented as one atomic payload."""

    model_config = ConfigDict(extra="forbid")

    user: UserCreate
    company: CompanyCreate


class EmployerRegistrationRead(BaseModel):
    user: UserRead
    company: CompanyRead
    membership_id: int
