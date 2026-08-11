import pytest
from pydantic import ValidationError

from core.config import Settings


def test_api_prefix_is_normalized() -> None:
    configured = Settings(api_v1_prefix="/internal/v1/")

    assert configured.api_v1_prefix == "/internal/v1"


def test_api_prefix_must_be_absolute() -> None:
    with pytest.raises(ValidationError, match="must start with"):
        Settings(api_v1_prefix="api/v1")
