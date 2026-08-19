from crudauth import get_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import UserExistsError
from ..company.models import Company
from ..user.crud import crud_users
from ..user.enums import UserType
from ..user.models import User
from .model import CompanyMembership
from .schemas import EmployerRegistration, EmployerRegistrationRead


class EmployerRegistrationService:
    """Create an employer, their company, and the owning membership as one unit."""

    async def create(self, payload: EmployerRegistration, db: AsyncSession) -> EmployerRegistrationRead:
        if await crud_users.exists(db=db, email=payload.user.email):
            raise UserExistsError("Email already registered")

        user_data = payload.user.model_dump(exclude={"password"})
        user = User(
            **user_data,
            hashed_password=get_password_hash(payload.user.password),
            user_type=UserType.EMPLOYER.value,
        )
        company = Company(**payload.company.model_dump(mode="json"))

        try:
            db.add_all((user, company))
            await db.flush()

            membership = CompanyMembership(
                user_id=user.id,
                company_id=company.id,
                is_admin=True,
            )
            db.add(membership)
            await db.flush()

            result = EmployerRegistrationRead(
                user=user,
                company=company,
                membership=membership,
            )
            await db.commit()
            return result
        except IntegrityError as error:
            await db.rollback()
            raise UserExistsError("Email already registered") from error
        except Exception:
            await db.rollback()
            raise
