"""Helper functions for user API tests."""

import random
from datetime import datetime


def generate_unique_user_data(prefix: str = "user") -> dict:
    """Generate unique user data for testing."""
    timestamp = int(datetime.now().timestamp())
    random_suffix = random.randint(1000, 9999)
    phone_suffix = random.randint(0, 999_999_999)

    return {
        "name": f"{prefix.title()} User {random_suffix}",
        "phone_number": f"09{phone_suffix:09d}",
        "email": f"{prefix}_{timestamp}_{random_suffix}@example.com",
        "password": "Password123!",
    }


def generate_superuser_data(prefix: str = "admin") -> dict:
    """Generate superuser data for testing."""
    data = generate_unique_user_data(prefix)
    data["name"] = f"Admin {data['name']}"
    return data


def generate_oauth_user_data(provider: str = "google", prefix: str = "oauth") -> dict:
    """Generate OAuth user data for specific provider."""
    data = generate_unique_user_data(prefix)
    data.update({"oauth_provider": provider, "oauth_id": f"{provider}_{int(datetime.now().timestamp())}"})
    return data


def generate_bulk_users(count: int, prefix: str = "bulk") -> list[dict]:
    """Generate multiple user test data."""
    return [generate_unique_user_data(f"{prefix}_{i}") for i in range(count)]


def generate_test_user_update_data() -> dict:
    """Generate user update data for testing."""
    timestamp = int(datetime.now().timestamp())

    return {
        "name": f"Updated User {timestamp}",
        "phone_number": f"09{timestamp % 1_000_000_000:09d}",
    }
