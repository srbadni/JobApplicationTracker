from crudauth import get_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import UserExistsError
from ..company.models import Company
from ..company.schemas import CompanyRead
from ..user.crud import crud_users
from ..user.models import User
from ..user.schemas import UserRead
from .model import CompanyMembership
from .schemas import CompanyMembershipRead, EmployerRegistrationCreate, EmployerRegistrationRead


class EmployerRegistrationService:
    """Register the employer aggregate in one database transaction."""

    async def register(self, payload: EmployerRegistrationCreate, db: AsyncSession) -> EmployerRegistrationRead:
        if await crud_users.exists(db=db, email=payload.user.email):
            raise UserExistsError("Email already registered")

        user_data = payload.user.model_dump(exclude={"password"})
        user = User(
            **user_data,
            hashed_password=get_password_hash(payload.user.password),
            user_type="employer",
        )
        company_data = payload.company.model_dump(mode="json")
        company = Company(**company_data)

        try:
            db.add_all((user, company))
            await db.flush()
            membership = CompanyMembership(user_id=user.id, company_id=company.id, is_admin=True)
            db.add(membership)
            await db.flush()
            await db.commit()
            await db.refresh(user)
            await db.refresh(company)
            await db.refresh(membership)
        except IntegrityError as error:
            await db.rollback()
            raise UserExistsError("Email already registered") from error
        except Exception:
            await db.rollback()
            raise

        return EmployerRegistrationRead(
            user=UserRead.model_validate(user, from_attributes=True),
            company=CompanyRead.model_validate(company),
            membership=CompanyMembershipRead.model_validate(membership, from_attributes=True),
        )
