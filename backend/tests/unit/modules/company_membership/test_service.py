import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.session import Base
from src.modules.company.models import Company
from src.modules.company_membership.model import CompanyMembership
from src.modules.company_membership.schemas import EmployerRegistration
from src.modules.company_membership.service import EmployerRegistrationService
from src.modules.user.enums import UserType
from src.modules.user.models import User


async def test_register_employer_creates_all_records_atomically() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        result = await EmployerRegistrationService().create(
            EmployerRegistration.model_validate(
                {
                    "user": {
                        "name": "Example Employer",
                        "phone_number": "09123456789",
                        "email": "owner@example.com",
                        "password": "Password123!",
                    },
                    "company": {
                        "name": "Example Company",
                        "description": "A useful company profile",
                        "website": "https://example.com",
                    },
                }
            ),
            session,
        )

        assert result.user.user_type == UserType.EMPLOYER
        assert result.membership.user_id == result.user.id
        assert result.membership.company_id == result.company.id
        assert result.membership.is_admin is True
        assert await session.scalar(select(func.count()).select_from(User)) == 1
        assert await session.scalar(select(func.count()).select_from(Company)) == 1
        assert await session.scalar(select(func.count()).select_from(CompanyMembership)) == 1

    await engine.dispose()


def test_employer_registration_does_not_accept_client_selected_user_type() -> None:
    payload = {
        "user": {
            "name": "Example Employer",
            "phone_number": "09123456789",
            "email": "owner@example.com",
            "password": "Password123!",
            "user_type": "applicant",
        },
        "company": {"name": "Example Company"},
    }

    with pytest.raises(ValueError, match="user_type"):
        EmployerRegistration.model_validate(payload)
