"""Authentication endpoints for password and OAuth JWT bearer flows."""

import secrets
from typing import Annotated, Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from crudauth import Principal
from crudauth.exceptions import UnauthorizedException
from crudauth.oauth import OAuthState
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from ...modules.user.crud import crud_users
from ...modules.user.enums import OAuthProvider
from ..dependencies import AsyncSessionDep, OAuth2FormDep
from ..logging import get_logger
from .dependencies import get_current_principal, get_optional_principal
from .oauth import (
    OAUTH_EXCHANGE_TTL_SECONDS,
    OAUTH_STATE_TTL_SECONDS,
    oauth_account_service,
    oauth_exchange_storage,
    oauth_providers,
    oauth_state_storage,
)
from .schemas import OAuthExchangeRecord, OAuthExchangeRequest, RefreshTokenRequest, TokenPair
from .setup import auth as crud_auth
from .tokens import issue_token_pair, refresh_token_pair, revoke_user_tokens

logger = get_logger()

router = APIRouter(tags=["Authentication"])


def _with_query_parameter(url: str, name: str, value: str) -> str:
    """Append a query parameter without discarding existing parameters/fragments."""
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    query.append((name, value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


@router.post(
    "/login",
    response_model=TokenPair,
    summary="User Login",
    description=(
        "Authenticate an email/password pair and return JWT access and refresh "
        "tokens. Send the access token as `Authorization: Bearer <token>`."
    ),
    responses={
        200: {"description": "Login successful; JWT token pair issued"},
        401: {"description": "Authentication failed"},
        429: {"description": "Too many login attempts, try again later"},
    },
)
async def login(
    request: Request,
    form_data: OAuth2FormDep,
    db: AsyncSessionDep,
) -> dict[str, Any]:
    """Exchange password credentials for a bearer access/refresh token pair."""
    user = await crud_auth.authenticate_password(
        db,
        form_data.username,
        form_data.password,
        request=request,
    )
    return issue_token_pair(user, scopes=form_data.scopes)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Refresh JWT Tokens",
    responses={401: {"description": "Refresh token is invalid, expired, or revoked"}},
)
async def refresh_tokens(
    body: RefreshTokenRequest,
    db: AsyncSessionDep,
) -> dict[str, Any]:
    """Exchange a valid refresh token for a new access/refresh pair."""
    return await refresh_token_pair(db, body.refresh_token)


@router.post(
    "/logout",
    summary="User Logout",
    description=(
        "Revoke all access and refresh tokens issued for the authenticated user by advancing the user's token version."
    ),
    responses={
        200: {"description": "All bearer tokens for the user were revoked"},
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    principal: Annotated[Principal, Depends(get_current_principal)],
    db: AsyncSessionDep,
) -> dict[str, str]:
    """Invalidate the current user's outstanding JWT credentials."""
    await revoke_user_tokens(db, principal.user)
    return {"message": "Logged out successfully"}


@router.get(
    "/oauth/google",
    summary="Initiate Google OAuth Login",
    responses={
        200: {"description": "Authorization URL generated successfully"},
        500: {"description": "Failed to initiate Google login"},
    },
)
async def oauth_google_login(
    redirect_uri: str | None = Query(None),
) -> dict[str, str]:
    """Build the Google authorization URL and store state plus PKCE verifier."""
    try:
        auth_data = oauth_providers["google"].get_authorization_url()
        state_obj = OAuthState(
            state=auth_data["state"],
            provider=OAuthProvider.GOOGLE.value,
            redirect_to=redirect_uri,
            code_verifier=auth_data.get("code_verifier"),
        )
        await oauth_state_storage.create(
            state_obj,
            session_id=auth_data["state"],
            expiration=OAUTH_STATE_TTL_SECONDS,
        )
        return {"url": auth_data["url"]}
    except Exception as exc:
        logger.error("Error initiating Google OAuth: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login",
        ) from exc


@router.get(
    "/oauth/callback/google",
    summary="Google OAuth Callback Handler",
    responses={
        200: {"description": "Authentication successful (JSON response)"},
        302: {"description": "Redirect with a one-time OAuth exchange code"},
        400: {"description": "Invalid OAuth state or provider"},
        500: {"description": "Server error during authentication"},
    },
)
async def oauth_google_callback(
    db: AsyncSessionDep,
    code: str = Query(...),
    state: str = Query(...),
    response_format: str = Query("redirect", description="Response format: 'redirect' or 'json'"),
):
    """Link/create the OAuth user and issue tokens directly or via a one-time code."""
    state_data = await oauth_state_storage.get_and_delete(state, OAuthState)

    if not state_data:
        logger.warning("Invalid OAuth state in callback: %s", state)
        if response_format == "json":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
        return RedirectResponse(
            url=f"/login?error=oauth_error&provider={OAuthProvider.GOOGLE.value}&reason=invalid_state",
            status_code=status.HTTP_302_FOUND,
        )

    if state_data.provider != OAuthProvider.GOOGLE.value:
        logger.warning(
            "Provider mismatch in OAuth callback: expected google, got %s",
            state_data.provider,
        )
        if response_format == "json":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider mismatch")
        return RedirectResponse(
            url=f"/login?error=oauth_error&provider={OAuthProvider.GOOGLE.value}&reason=provider_mismatch",
            status_code=status.HTTP_302_FOUND,
        )

    try:
        provider = oauth_providers["google"]
        token_data = await provider.exchange_code(code, code_verifier=state_data.code_verifier)
        user_info_raw = await provider.get_user_info(token_data["access_token"])
        user_info = await provider.process_user_info(user_info_raw)

        user, is_new_user = await oauth_account_service.get_or_create_user(user_info, db)
        user_id = crud_auth.repo.user_id(user)
        email = crud_auth.repo.get(user, "email")

        if response_format == "json":
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email,
                    "is_new_user": is_new_user,
                },
                **issue_token_pair(user),
            }

        exchange_code = secrets.token_urlsafe(32)
        await oauth_exchange_storage.create(
            OAuthExchangeRecord(user_id=user_id),
            session_id=exchange_code,
            expiration=OAUTH_EXCHANGE_TTL_SECONDS,
        )
        redirect_to = str(state_data.redirect_to) if state_data.redirect_to else "/"
        return RedirectResponse(
            url=_with_query_parameter(redirect_to, "oauth_code", exchange_code),
            status_code=status.HTTP_302_FOUND,
        )
    except Exception as exc:
        logger.error("Error in Google OAuth callback: %s", exc, exc_info=True)
        if response_format == "json":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth authentication failed",
            ) from exc
        return RedirectResponse(
            url=f"/login?error=oauth_error&provider={OAuthProvider.GOOGLE.value}",
            status_code=status.HTTP_302_FOUND,
        )


@router.post(
    "/oauth/exchange",
    response_model=TokenPair,
    summary="Exchange OAuth Redirect Code",
    responses={401: {"description": "Exchange code is invalid, expired, or already used"}},
)
async def exchange_oauth_code(
    body: OAuthExchangeRequest,
    db: AsyncSessionDep,
) -> dict[str, Any]:
    """Consume a one-time redirect code and return a JWT token pair."""
    exchange = await oauth_exchange_storage.get_and_delete(body.code, OAuthExchangeRecord)
    if exchange is None:
        raise UnauthorizedException("Invalid or expired OAuth exchange code")

    user = await crud_auth.repo.get_by_id(db, exchange.user_id)
    if user is None or not crud_auth.repo.is_active(user):
        raise UnauthorizedException("Invalid or expired OAuth exchange code")
    return issue_token_pair(user)


@router.get("/check-auth")
async def check_auth(
    principal: Annotated[Principal | None, Depends(get_optional_principal)],
    db: AsyncSessionDep,
) -> dict[str, Any]:
    """Return bearer authentication status and basic user information."""
    if principal is None:
        return {"authenticated": False, "message": "Not authenticated"}

    try:
        user = await crud_users.get(db=db, id=principal.user_id, is_deleted=False)
        if not user:
            return {"authenticated": False, "message": "User not found"}

        return {
            "authenticated": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "oauth_provider": user.get("oauth_provider"),
            },
            "authentication": {
                "transport": principal.transport,
                "scopes": list(principal.scopes),
            },
        }
    except Exception as exc:
        logger.error("Error checking authentication: %s", exc, exc_info=True)
        return {"authenticated": False, "message": "Error checking authentication status"}
