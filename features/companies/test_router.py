from fastapi.testclient import TestClient

from core.config import settings
from main import app


def test_companies_placeholder_preserves_current_contract() -> None:
    with TestClient(app) as client:
        response = client.get(f"{settings.api_v1_prefix}/companies")

    assert response.status_code == 200
    assert response.json() is None
