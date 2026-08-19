from pydantic import BaseModel, ConfigDict


class CompanyMembershipRead(BaseModel):
    """Public membership fields returned after registration."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company_id: int
    is_admin: bool
