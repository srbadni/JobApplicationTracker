"""Bearer-auth dependencies and the application's dict-compatible user contract."""

from typing import Annotated, Any

from crudauth import Principal
from crudauth.exceptions import ForbiddenException, UnauthorizedException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ...modules.user.crud import crud_users
from ..database.session import async_session
from .setup import auth

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_principal(
    _access_token: Annotated[str | None, Depends(oauth2_bearer)],
    principal: Annotated[Principal, Depends(auth.current_user(transport="bearer"))],
) -> Principal:
    """Return the principal resolved from a valid bearer access token.

    ``oauth2_bearer`` exposes the password/bearer flow in OpenAPI so Swagger UI
    can obtain and attach the token. crudauth performs the actual JWT validation.
    """
    return principal


async def get_optional_principal(
    _access_token: Annotated[str | None, Depends(oauth2_bearer)],
    principal: Annotated[
        Principal | None,
        Depends(auth.current_user(optional=True, transport="bearer")),
    ],
) -> Principal | None:
    """Return the bearer principal, or ``None`` when no credential is present."""
    return principal


async def get_current_user(
    principal: Annotated[Principal | None, Depends(get_optional_principal)],
    db: Annotated[AsyncSession, Depends(async_session)],
) -> dict[str, Any]:
    """Get the current authenticated user as a dict (resolved by crudauth).

    crudauth validates the bearer token; this dependency re-loads the full row
    (filtering soft-deleted users) so handlers keep their existing user-dict API.

    Raises:
        UnauthorizedException: If not authenticated or the user doesn't exist.
    """
    credentials_exception = UnauthorizedException("Not authenticated")

    if principal is None:
        raise credentials_exception

    user = await crud_users.get(db=db, id=principal.user_id, is_deleted=False)

    if user is None:
        raise credentials_exception

    return user


async def get_optional_user(
    principal: Annotated[Principal | None, Depends(get_optional_principal)],
    db: Annotated[AsyncSession, Depends(async_session)],
) -> dict[str, Any] | None:
    """Get the current user as a dict if authenticated, None otherwise."""
    if principal is None:
        return None

    return await crud_users.get(db=db, id=principal.user_id, is_deleted=False)


async def get_current_superuser(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Get the current user as a dict, requiring superuser privileges (403 otherwise)."""
    if not current_user.get("is_superuser", False):
        raise ForbiddenException("Insufficient privileges")

    return current_user
