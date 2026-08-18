from pydantic import BaseModel, ConfigDict

from ..company.schemas import CompanyCreate, CompanyRead
from ..user.schemas import UserCreate, UserRead


class EmployerRegistrationCreate(BaseModel):
    """The two sections of the employer registration form."""

    model_config = ConfigDict(extra="forbid")

    user: UserCreate
    company: CompanyCreate


class CompanyMembershipRead(BaseModel):
    """Public membership details returned after employer registration."""

    id: int
    user_id: int
    company_id: int
    is_admin: bool


class EmployerRegistrationRead(BaseModel):
    """The employer, company, and linking membership created atomically."""

    user: UserRead
    company: CompanyRead
    membership: CompanyMembershipRead
