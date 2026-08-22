import pytest
from httpx import AsyncClient

from src.modules.user.enums import UserType

from .helpers import generate_unique_user_data

pytestmark = pytest.mark.asyncio


async def test_create_user_success(client: AsyncClient) -> None:
    user_data = generate_unique_user_data()

    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == user_data["name"]
    assert body["phone_number"] == user_data["phone_number"]
    assert body["email"] == user_data["email"]
    assert body["user_type"] == UserType.APPLICANT
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


async def test_create_user_rejects_invalid_email(client: AsyncClient) -> None:
    user_data = generate_unique_user_data()
    user_data["email"] = "invalid-email"

    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 422


async def test_create_user_rejects_invalid_phone_number(client: AsyncClient) -> None:
    user_data = generate_unique_user_data()
    user_data["phone_number"] = "12345"

    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 422


async def test_create_user_rejects_duplicate_email(
    client: AsyncClient,
    test_user: dict,
) -> None:
    user_data = generate_unique_user_data()
    user_data["email"] = test_user["email"]

    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 422


async def test_create_user_rejects_privilege_escalation_fields(
    client: AsyncClient,
) -> None:
    user_data = generate_unique_user_data()
    payload = {**user_data, "is_superuser": True, "user_type": UserType.EMPLOYER}

    response = await client.post("/api/v1/users/", json=payload)

    assert response.status_code == 422
