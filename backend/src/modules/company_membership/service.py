from crudauth import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import UserExistsError
from ..company.models import Company
from ..company.schemas import CompanyRead
from ..user.models import User
from ..user.schemas import UserRead
from .model import CompanyMembership
from .schemas import EmployerRegistrationCreate, EmployerRegistrationRead


class EmployerRegistrationService:
    """Atomically provision an employer, their company, and ownership membership."""

    async def create(self, payload: EmployerRegistrationCreate, db: AsyncSession) -> EmployerRegistrationRead:
        email_exists = await db.scalar(select(User.id).where(User.email == str(payload.user.email)))
        if email_exists is not None:
            raise UserExistsError("Email already registered")
        phone_exists = await db.scalar(select(User.id).where(User.phone_number == payload.user.phone_number))
        if phone_exists is not None:
            raise UserExistsError("Phone number already registered")

        user = User(
            name=payload.user.name,
            email=str(payload.user.email),
            phone_number=payload.user.phone_number,
            hashed_password=get_password_hash(password=payload.user.password),
            user_type="employer",
        )
        company_data = payload.company.model_dump(mode="json")
        company = Company(**company_data)
        db.add_all([user, company])
        await db.flush()

        membership = CompanyMembership(user_id=user.id, company_id=company.id, is_admin=True)
        db.add(membership)
        await db.commit()
        await db.refresh(user)
        await db.refresh(company)
        await db.refresh(membership)

        return EmployerRegistrationRead(
            user=UserRead.model_validate(user, from_attributes=True),
            company=CompanyRead.model_validate(company),
            membership_id=membership.id,
        )
