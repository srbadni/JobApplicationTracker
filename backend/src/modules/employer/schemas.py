from pydantic import BaseModel, ConfigDict

from ..company.schemas import CompanyCreate, CompanyRead
from ..company_membership.schemas import CompanyMembershipRead
from ..user.schemas import UserCreate, UserRead


class EmployerRegistration(BaseModel):
    """Employer and company registration payload."""

    model_config = ConfigDict(extra="forbid")

    user: UserCreate
    company: CompanyCreate


class EmployerRegistrationRead(BaseModel):
    """The three records atomically created for a new employer."""

    user: UserRead
    company: CompanyRead
    membership: CompanyMembershipRead
