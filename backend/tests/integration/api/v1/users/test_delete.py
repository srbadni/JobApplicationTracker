import pytest
from httpx import AsyncClient

from .helpers import generate_unique_user_data

pytestmark = pytest.mark.asyncio


async def test_soft_delete_success(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.delete(f"/api/v1/users/{test_user['email']}")

    assert response.status_code == 200
    assert response.json() == {"message": "User account deactivated"}

    fetched = await auth_client.get(f"/api/v1/users/{test_user['email']}")
    assert fetched.status_code == 404


async def test_soft_delete_unauthorized(
    client: AsyncClient,
    test_user: dict,
) -> None:
    response = await client.delete(f"/api/v1/users/{test_user['email']}")

    assert response.status_code == 401


async def test_soft_delete_wrong_user(auth_client: AsyncClient) -> None:
    other_user_data = generate_unique_user_data("other")
    created = await auth_client.post("/api/v1/users/", json=other_user_data)
    assert created.status_code == 201

    response = await auth_client.delete(f"/api/v1/users/{other_user_data['email']}")

    assert response.status_code == 403


async def test_soft_delete_nonexistent_user(auth_client: AsyncClient) -> None:
    response = await auth_client.delete("/api/v1/users/missing@example.com")

    assert response.status_code == 404


async def test_gdpr_anonymize_success(
    superuser_auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await superuser_auth_client.delete(f"/api/v1/users/db/{test_user['email']}")

    assert response.status_code == 200
    assert response.json() == {"message": "User data anonymized in compliance with GDPR"}

    active = await superuser_auth_client.get(f"/api/v1/users/{test_user['email']}")
    assert active.status_code == 404

    retained = await superuser_auth_client.get(
        f"/api/v1/users/active-and-inactive/{test_user['email']}"
    )
    assert retained.status_code == 200
    body = retained.json()
    assert body["name"] == "[DELETED]"
    assert body["is_deleted"] is True


async def test_gdpr_anonymize_unauthorized(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.delete(f"/api/v1/users/db/{test_user['email']}")

    assert response.status_code == 403


async def test_gdpr_anonymize_soft_deleted_user(
    superuser_auth_client: AsyncClient,
    test_user: dict,
) -> None:
    soft_deleted = await superuser_auth_client.delete(f"/api/v1/users/{test_user['email']}")
    assert soft_deleted.status_code == 200

    anonymized = await superuser_auth_client.delete(f"/api/v1/users/db/{test_user['email']}")
    assert anonymized.status_code == 200

    retained = await superuser_auth_client.get(
        f"/api/v1/users/active-and-inactive/{test_user['email']}"
    )
    assert retained.status_code == 200
    assert retained.json()["is_deleted"] is True


async def test_gdpr_anonymize_nonexistent_user(
    superuser_auth_client: AsyncClient,
) -> None:
    response = await superuser_auth_client.delete("/api/v1/users/db/missing@example.com")

    assert response.status_code == 404


async def test_soft_delete_hides_tier_and_rate_limits(
    superuser_auth_client: AsyncClient,
    test_user: dict,
) -> None:
    email = test_user["email"]
    tier_before = await superuser_auth_client.get(f"/api/v1/users/{email}/tier")
    limits_before = await superuser_auth_client.get(f"/api/v1/users/{email}/rate-limits")
    assert tier_before.status_code == 200
    assert limits_before.status_code == 200

    deleted = await superuser_auth_client.delete(f"/api/v1/users/{email}")
    assert deleted.status_code == 200

    tier_after = await superuser_auth_client.get(f"/api/v1/users/{email}/tier")
    limits_after = await superuser_auth_client.get(f"/api/v1/users/{email}/rate-limits")
    assert tier_after.status_code == 404
    assert limits_after.status_code == 404
