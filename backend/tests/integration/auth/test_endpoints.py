"""Integration coverage for the JWT bearer authentication endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from crudauth import Principal, get_password_hash
from crudauth.oauth import OAuthState, OAuthUserInfo
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.auth.dependencies import get_optional_principal
from src.interfaces.main import app
from src.modules.user.models import User

ROUTES = "src.infrastructure.auth.routes"


async def _login(client: AsyncClient, user: dict) -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert response.status_code == 200
    return response.json()


def _bearer(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_login_success_returns_tokens_without_api_auth_cookies(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2
    assert body["refresh_token"].count(".") == 2
    assert "session_id" not in response.cookies
    assert "csrf_token" not in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_token_authenticates_check_auth(client: AsyncClient, test_user: dict):
    tokens = await _login(client, test_user)
    response = await client.get(
        "/api/v1/auth/check-auth",
        headers=_bearer(tokens["access_token"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["authenticated"] is True
    assert body["user"]["id"] == test_user["id"]
    assert body["authentication"]["transport"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_returns_new_token_pair(client: AsyncClient, test_user: dict):
    tokens = await _login(client, test_user)
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    refreshed = response.json()
    assert refreshed["token_type"] == "bearer"
    assert refreshed["access_token"].count(".") == 2
    assert refreshed["refresh_token"].count(".") == 2


@pytest.mark.asyncio
async def test_access_token_cannot_be_used_as_refresh_token(client: AsyncClient, test_user: dict):
    tokens = await _login(client, test_user)
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_access_and_refresh_tokens(client: AsyncClient, test_user: dict):
    tokens = await _login(client, test_user)

    logout = await client.post(
        "/api/v1/auth/logout",
        headers=_bearer(tokens["access_token"]),
    )
    assert logout.status_code == 200
    assert logout.json()["message"] == "Logged out successfully"

    check_auth = await client.get(
        "/api/v1/auth/check-auth",
        headers=_bearer(tokens["access_token"]),
    )
    assert check_auth.status_code == 200
    assert check_auth.json()["authenticated"] is False

    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_bearer_token_returns_401(client: AsyncClient):
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_check_auth_without_bearer_token_is_anonymous(client: AsyncClient):
    response = await client.get("/api/v1/auth/check-auth")
    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "message": "Not authenticated"}


@pytest.mark.asyncio
async def test_login_soft_deleted_user_rejected(
    client: AsyncClient,
    db_session: AsyncSession,
    test_tier: dict,
):
    user = User(
        name="Deleted User",
        phone_number="09111111111",
        email="deleted@example.com",
        hashed_password=get_password_hash("Password123!"),
        tier_id=test_tier["id"],
    )
    user.is_deleted = True
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "Password123!"},
    )
    assert response.status_code == 401


def test_openapi_declares_password_bearer_flow_for_protected_routes():
    schema = app.openapi()
    security_scheme = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    password_flow = security_scheme["flows"]["password"]

    assert password_flow["tokenUrl"] == "/api/v1/auth/login"
    job_posting = schema["paths"]["/api/v1/job_postings"]["post"]
    assert {"OAuth2PasswordBearer": []} in job_posting["security"]
    assert all(parameter["name"].lower() != "x-csrf-token" for parameter in job_posting.get("parameters", []))


@pytest.mark.asyncio
async def test_oauth_google_login(client: AsyncClient):
    mock_provider = MagicMock()
    mock_provider.get_authorization_url.return_value = {
        "url": "https://accounts.google.com/o/oauth2/v2/auth?dummy=params",
        "state": "test-state-value",
        "code_verifier": "test-code-verifier",
    }
    mock_storage = MagicMock()
    mock_storage.create = AsyncMock(return_value="test-state-value")

    with (
        patch(f"{ROUTES}.oauth_providers", {"google": mock_provider}),
        patch(f"{ROUTES}.oauth_state_storage", mock_storage),
    ):
        response = await client.get("/api/v1/auth/oauth/google")

    assert response.status_code == 200
    assert response.json()["url"] == "https://accounts.google.com/o/oauth2/v2/auth?dummy=params"
    mock_storage.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_oauth_callback_invalid_state(client: AsyncClient):
    mock_storage = MagicMock()
    mock_storage.get_and_delete = AsyncMock(return_value=None)

    with patch(f"{ROUTES}.oauth_state_storage", mock_storage):
        redirect = await client.get(
            "/api/v1/auth/oauth/callback/google",
            params={"code": "test-code", "state": "invalid-state"},
        )
        json_response = await client.get(
            "/api/v1/auth/oauth/callback/google",
            params={"code": "test-code", "state": "invalid-state", "response_format": "json"},
        )

    assert redirect.status_code == 302
    assert json_response.status_code == 400


@pytest.mark.asyncio
async def test_oauth_callback_provider_mismatch(client: AsyncClient):
    mismatched_state = OAuthState(
        state="test-state-value",
        provider="github",
        redirect_to="/",
        code_verifier="test-code-verifier",
    )
    mock_storage = MagicMock()
    mock_storage.get_and_delete = AsyncMock(return_value=mismatched_state)

    with patch(f"{ROUTES}.oauth_state_storage", mock_storage):
        response = await client.get(
            "/api/v1/auth/oauth/callback/google",
            params={"code": "test-code", "state": "test-state-value", "response_format": "json"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_oauth_callback_json_returns_bearer_tokens(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: dict,
):
    user = await db_session.get(User, test_user["id"])
    valid_state = OAuthState(
        state="good-state",
        provider="google",
        redirect_to="/",
        code_verifier="test-code-verifier",
    )
    mock_storage = MagicMock()
    mock_storage.get_and_delete = AsyncMock(return_value=valid_state)
    mock_provider = MagicMock()
    mock_provider.exchange_code = AsyncMock(return_value={"access_token": "provider-token"})
    mock_provider.get_user_info = AsyncMock(return_value={})
    mock_provider.process_user_info = AsyncMock(
        return_value=OAuthUserInfo(
            provider="google",
            provider_user_id="google-uid-123",
            email=test_user["email"],
            email_verified=True,
            name=test_user["name"],
        )
    )
    mock_account_service = MagicMock()
    mock_account_service.get_or_create_user = AsyncMock(return_value=(user, False))

    with (
        patch(f"{ROUTES}.oauth_state_storage", mock_storage),
        patch(f"{ROUTES}.oauth_providers", {"google": mock_provider}),
        patch(f"{ROUTES}.oauth_account_service", mock_account_service),
    ):
        response = await client.get(
            "/api/v1/auth/oauth/callback/google",
            params={"code": "test-code", "state": "good-state", "response_format": "json"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2
    assert body["refresh_token"].count(".") == 2


@pytest.mark.asyncio
async def test_oauth_redirect_uses_one_time_exchange_code(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: dict,
):
    user = await db_session.get(User, test_user["id"])
    state = OAuthState(
        state="good-state",
        provider="google",
        redirect_to="https://frontend.example/callback?source=google",
        code_verifier="verifier",
    )
    state_storage = MagicMock()
    state_storage.get_and_delete = AsyncMock(return_value=state)
    exchange_storage = MagicMock()
    exchange_storage.create = AsyncMock(return_value="exchange-code")
    provider = MagicMock()
    provider.exchange_code = AsyncMock(return_value={"access_token": "provider-token"})
    provider.get_user_info = AsyncMock(return_value={})
    provider.process_user_info = AsyncMock(return_value=MagicMock())
    account_service = MagicMock()
    account_service.get_or_create_user = AsyncMock(return_value=(user, False))

    with (
        patch(f"{ROUTES}.oauth_state_storage", state_storage),
        patch(f"{ROUTES}.oauth_exchange_storage", exchange_storage),
        patch(f"{ROUTES}.oauth_providers", {"google": provider}),
        patch(f"{ROUTES}.oauth_account_service", account_service),
        patch(f"{ROUTES}.secrets.token_urlsafe", return_value="one-time-code"),
    ):
        response = await client.get(
            "/api/v1/auth/oauth/callback/google",
            params={"code": "provider-code", "state": "good-state"},
        )

    assert response.status_code == 302
    assert response.headers["location"] == ("https://frontend.example/callback?source=google&oauth_code=one-time-code")
    exchange_storage.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_auth_dependency_contract(client: AsyncClient):
    mock_user = {"id": 1, "email": "test@example.com", "oauth_provider": "google"}
    original_deps = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[get_optional_principal] = lambda: Principal(
            user_id=1,
            transport="bearer",
        )
        with patch("src.modules.user.crud.crud_users.get", return_value=mock_user):
            response = await client.get("/api/v1/auth/check-auth")

        assert response.status_code == 200
        assert response.json()["authentication"]["transport"] == "bearer"
    finally:
        app.dependency_overrides = original_deps
