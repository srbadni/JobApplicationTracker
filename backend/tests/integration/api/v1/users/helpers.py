"""Factories for user API integration tests."""

import uuid


def generate_unique_user_data(prefix: str = "user") -> dict[str, str]:
    """Return a valid payload for the current email-based user contract."""
    unique_id = uuid.uuid4().hex[:8]
    phone_suffix = uuid.uuid4().int % 1_000_000_000

    return {
        "name": f"Test {prefix.capitalize()}",
        "phone_number": f"09{phone_suffix:09d}",
        "email": f"{prefix}.{unique_id}@example.com",
        "password": "Password123!",
    }
