import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.session import Base
from src.modules.company.models import Company
from src.modules.company_membership.model import CompanyMembership
from src.modules.employer.schemas import EmployerRegistration
from src.modules.employer.service import EmployerRegistrationService
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
        membership = await session.scalar(select(CompanyMembership))
        assert membership is not None
        assert membership.user_id == result.user.id
        assert membership.company_id == result.company.id
        assert membership.is_admin is True
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


async def test_register_employer_rolls_back_every_record_when_membership_creation_fails(mocker) -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        original_flush = session.flush
        flush_count = 0

        async def fail_membership_flush(*args, **kwargs):
            nonlocal flush_count
            flush_count += 1
            if flush_count == 2:
                raise RuntimeError("membership creation failed")
            return await original_flush(*args, **kwargs)

        mocker.patch.object(session, "flush", side_effect=fail_membership_flush)
        payload = EmployerRegistration.model_validate(
            {
                "user": {
                    "name": "Example Employer",
                    "phone_number": "09123456789",
                    "email": "owner@example.com",
                    "password": "Password123!",
                },
                "company": {"name": "Example Company"},
            }
        )

        with pytest.raises(RuntimeError, match="membership creation failed"):
            await EmployerRegistrationService().create(payload, session)

        assert await session.scalar(select(func.count()).select_from(User)) == 0
        assert await session.scalar(select(func.count()).select_from(Company)) == 0
        assert await session.scalar(select(func.count()).select_from(CompanyMembership)) == 0

    await engine.dispose()
