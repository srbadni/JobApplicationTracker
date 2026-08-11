from datetime import UTC, datetime

from fastapi.testclient import TestClient

from core.config import settings
from db.database import get_db
from features.companies.models import Company
from main import app


class FakeScalarResult:
    def all(self) -> list[Company]:
        timestamp = datetime(2026, 8, 11, tzinfo=UTC)
        return [
            Company(
                id=1,
                name="OpenAI",
                description="AI research and deployment company",
                website="https://openai.com",
                created_at=timestamp,
                updated_at=timestamp,
            )
        ]


class FakeSession:
    async def scalars(self, _statement: object) -> FakeScalarResult:
        return FakeScalarResult()


async def override_get_db():
    yield FakeSession()


def test_get_companies_returns_companies() -> None:
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            response = client.get(f"{settings.api_v1_prefix}/companies")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Companies retrieved successfully",
        "result": [
            {
                "id": 1,
                "name": "OpenAI",
                "description": "AI research and deployment company",
                "website": "https://openai.com/",
                "created_at": "2026-08-11T00:00:00Z",
                "updated_at": "2026-08-11T00:00:00Z",
            }
        ],
    }
