"""JWT token lifecycle helpers shared by auth routes."""

from typing import Any

from crudauth.exceptions import UnauthorizedException
from crudauth.transports.bearer.tokens import TokenType, verify_token
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.settings import settings
from .setup import auth

_INVALID_REFRESH_TOKEN = "Invalid or expired refresh token"


def issue_token_pair(user: Any, *, scopes: list[str] | None = None) -> dict[str, Any]:
    """Issue an access/refresh pair through the configured bearer transport."""
    return auth.issue_tokens(user, scopes=scopes)


async def refresh_token_pair(db: AsyncSession, refresh_token: str) -> dict[str, Any]:
    """Validate a refresh JWT and issue a new token pair."""
    payload = verify_token(
        refresh_token,
        settings.SECRET_KEY,
        TokenType.REFRESH,
        algorithm=settings.JWT_ALGORITHM,
    )
    if payload is None:
        raise UnauthorizedException(_INVALID_REFRESH_TOKEN)

    user = await auth.repo.get_by_id(db, payload["sub"])
    if user is None or not auth.repo.is_active(user):
        raise UnauthorizedException(_INVALID_REFRESH_TOKEN)
    if payload.get("ver", 0) != auth.repo.token_version(user):
        raise UnauthorizedException(_INVALID_REFRESH_TOKEN)

    raw_scopes = payload.get("scopes")
    scopes = raw_scopes if isinstance(raw_scopes, list) else []
    return issue_token_pair(user, scopes=scopes)


async def revoke_user_tokens(db: AsyncSession, user: Any) -> None:
    """Invalidate every outstanding access and refresh token for ``user``."""
    await auth.repo.increment_token_version(db, user)
