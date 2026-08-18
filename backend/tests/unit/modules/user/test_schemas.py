import pytest
from pydantic import ValidationError

from src.modules.user.schemas import UserCreate


def test_user_create_accepts_iranian_mobile_number() -> None:
    user = UserCreate(
        name="Test User",
        email="test@example.com",
        phone_number="09123456789",
        password="Password123!",
    )

    assert user.phone_number == "09123456789"


@pytest.mark.parametrize("phone_number", ["", "9123456789", "+12025550123", "08123456789"])
def test_user_create_rejects_invalid_or_non_iranian_phone_number(phone_number: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="test@example.com",
            phone_number=phone_number,
            password="Password123!",
        )


def test_user_create_requires_phone_number_and_rejects_username() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="test@example.com",
            username="testuser",
            password="Password123!",
        )
