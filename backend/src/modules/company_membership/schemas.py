from pydantic import BaseModel, ConfigDict

from ..company.schemas import CompanyCreate, CompanyRead
from ..user.schemas import UserCreate, UserRead


class EmployerRegistration(BaseModel):
    """Two-step employer registration payload."""

    model_config = ConfigDict(extra="forbid")

    user: UserCreate
    company: CompanyCreate


class CompanyMembershipRead(BaseModel):
    """Public membership fields returned after registration."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company_id: int
    is_admin: bool


class EmployerRegistrationRead(BaseModel):
    """The three records atomically created for a new employer."""

    user: UserRead
    company: CompanyRead
    membership: CompanyMembershipRead
