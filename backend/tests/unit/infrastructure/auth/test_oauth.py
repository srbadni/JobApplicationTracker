from crudauth.oauth import OAuthUserInfo
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.auth.oauth import (
    OAUTH_PLACEHOLDER_PHONE_NUMBER,
    PhoneNumberOAuthAccountService,
    _oauth_new_user_fields,
)
from src.infrastructure.auth.setup import auth
from src.infrastructure.database.session import Base


async def test_oauth_provisions_user_without_username_column() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        service = PhoneNumberOAuthAccountService(
            repo=auth.repo,
            new_user_fields=_oauth_new_user_fields,
        )
        info = OAuthUserInfo(
            provider="google",
            provider_user_id="google-uid-123",
            email="OAuth.New@Example.com",
            email_verified=True,
            name="OAuth New User",
        )

        user, created = await service.get_or_create_user(info, session)
        same_user, created_again = await service.get_or_create_user(info, session)

        assert created is True
        assert created_again is False
        assert same_user.id == user.id
        assert user.email == "oauth.new@example.com"
        assert user.phone_number == OAUTH_PLACEHOLDER_PHONE_NUMBER
        assert user.name == "OAuth New User"
        assert user.google_id == "google-uid-123"
        assert not hasattr(user, "username")

    await engine.dispose()
