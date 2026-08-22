import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_user_by_email_success(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.get(f"/api/v1/users/{test_user['email']}")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == test_user["email"]
    assert body["phone_number"] == test_user["phone_number"]
    assert body["id"] == test_user["id"]


async def test_get_user_by_email_not_found(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/users/missing@example.com")

    assert response.status_code == 404


async def test_get_users_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/")

    assert response.status_code == 401


async def test_get_users_superuser_success(superuser_auth_client: AsyncClient) -> None:
    response = await superuser_auth_client.get("/api/v1/users/")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert "total_count" in body
    assert "page" in body
    assert "items_per_page" in body


async def test_get_users_pagination(superuser_auth_client: AsyncClient) -> None:
    response = await superuser_auth_client.get("/api/v1/users/?page=1&items_per_page=5")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) <= 5
    assert body["page"] == 1
    assert body["items_per_page"] == 5


async def test_get_current_user_profile(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.get("/api/v1/users/me")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == test_user["email"]
    assert body["phone_number"] == test_user["phone_number"]


async def test_get_user_tier_info(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.get(f"/api/v1/users/{test_user['email']}/tier")

    assert response.status_code == 200
    assert "tier" in response.json()


async def test_get_user_rate_limits(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.get(f"/api/v1/users/{test_user['email']}/rate-limits")

    assert response.status_code == 200
    assert "rate_limits" in response.json()
