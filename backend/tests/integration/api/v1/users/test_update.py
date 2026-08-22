import pytest
from httpx import AsyncClient

from .helpers import generate_unique_user_data

pytestmark = pytest.mark.asyncio


async def test_update_user_profile_success(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    original_email = test_user["email"]
    update_data = {
        "name": "Updated Name",
        "phone_number": "09111111111",
        "email": "updated.email@example.com",
        "profile_image_url": "https://example.com/new-image.jpg",
    }

    response = await auth_client.patch(f"/api/v1/users/{original_email}", json=update_data)

    assert response.status_code == 200
    assert response.json() == {"message": "User updated successfully"}

    fetched = await auth_client.get(f"/api/v1/users/{update_data['email']}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["name"] == update_data["name"]
    assert body["phone_number"] == update_data["phone_number"]
    assert body["email"] == update_data["email"]


async def test_update_user_profile_rejects_invalid_email(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.patch(
        f"/api/v1/users/{test_user['email']}",
        json={"email": "invalid-email"},
    )

    assert response.status_code == 422


async def test_update_user_profile_rejects_invalid_phone_number(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    response = await auth_client.patch(
        f"/api/v1/users/{test_user['email']}",
        json={"phone_number": "12345"},
    )

    assert response.status_code == 422


async def test_update_user_profile_unauthorized(
    client: AsyncClient,
    test_user: dict,
) -> None:
    response = await client.patch(
        f"/api/v1/users/{test_user['email']}",
        json={"name": "Unauthorized Update"},
    )

    assert response.status_code == 401


async def test_update_user_profile_wrong_user(
    auth_client: AsyncClient,
) -> None:
    other_user_data = generate_unique_user_data("other")
    created = await auth_client.post("/api/v1/users/", json=other_user_data)
    assert created.status_code == 201

    response = await auth_client.patch(
        f"/api/v1/users/{other_user_data['email']}",
        json={"name": "Unauthorized Update"},
    )

    assert response.status_code == 403


async def test_update_user_profile_rejects_duplicate_email(
    auth_client: AsyncClient,
    test_user: dict,
) -> None:
    other_user_data = generate_unique_user_data("other")
    created = await auth_client.post("/api/v1/users/", json=other_user_data)
    assert created.status_code == 201

    response = await auth_client.patch(
        f"/api/v1/users/{test_user['email']}",
        json={"email": other_user_data["email"]},
    )

    assert response.status_code == 422


async def test_update_user_tier_superuser(
    superuser_auth_client: AsyncClient,
    test_user: dict,
    second_test_tier: dict,
) -> None:
    response = await superuser_auth_client.patch(
        f"/api/v1/users/{test_user['email']}/tier",
        json={"tier_id": second_test_tier["id"]},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "User tier updated successfully"}

    fetched = await superuser_auth_client.get(f"/api/v1/users/{test_user['email']}")
    assert fetched.status_code == 200
    assert fetched.json()["tier_id"] == second_test_tier["id"]


async def test_update_user_tier_regular_user(
    auth_client: AsyncClient,
    test_user: dict,
    second_test_tier: dict,
) -> None:
    response = await auth_client.patch(
        f"/api/v1/users/{test_user['email']}/tier",
        json={"tier_id": second_test_tier["id"]},
    )

    assert response.status_code == 403
