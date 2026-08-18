import pytest
from pydantic import ValidationError

from src.modules.user.schemas import UserCreate


def _payload(phone_number: str) -> UserCreate:
    return UserCreate(
        name="Test User",
        email="test@example.com",
        phone_number=phone_number,
        password="Password1!",
    )


@pytest.mark.parametrize(
    ("raw", "normalized"),
    [("09123456789", "09123456789"), ("+989123456789", "09123456789"), ("00989123456789", "09123456789")],
)
def test_normalizes_iranian_mobile_numbers(raw: str, normalized: str) -> None:
    assert _payload(raw).phone_number == normalized


def test_rejects_non_mobile_iranian_number() -> None:
    with pytest.raises(ValidationError):
        _payload("08123456789")
