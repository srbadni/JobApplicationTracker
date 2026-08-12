from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db_session
from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)

    def override_session() -> Generator[Session, None, None]:
        with test_session() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db_session] = override_session
    with TestClient(application) as test_client:
        yield test_client
    engine.dispose()


def test_create_company(client: TestClient):
    response = client.post(
        "/api/v1/companies",
        json={
            "name": "OpenAI",
            "description": "AI research and deployment company",
            "website": "https://openai.com",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["result"] == {
        "id": 1,
        "name": "OpenAI",
        "description": "AI research and deployment company",
        "website": "https://openai.com/",
        "created_at": body["result"]["created_at"],
        "updated_at": body["result"]["updated_at"],
    }


def test_create_company_rejects_whitespace_only_name(client: TestClient):
    response = client.post("/api/v1/companies", json={"name": "   \t  "})

    assert response.status_code == 422
    assert any(error["loc"][-1] == "name" for error in response.json()["detail"])


def test_create_company_trims_name(client: TestClient):
    response = client.post("/api/v1/companies", json={"name": "  OpenAI  "})

    assert response.status_code == 201
    assert response.json()["result"]["name"] == "OpenAI"


def test_get_all_companies(client: TestClient):
    first_company = client.post(
        "/api/v1/companies",
        json={"name": "OpenAI", "website": "https://openai.com"},
    ).json()["result"]
    second_company = client.post(
        "/api/v1/companies",
        json={"name": "Anthropic", "description": "AI safety company"},
    ).json()["result"]

    response = client.get("/api/v1/companies")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "result": [first_company, second_company],
    }


def test_get_company_by_id(client: TestClient):
    company = client.post(
        "/api/v1/companies",
        json={
            "name": "OpenAI",
            "description": "AI research and deployment company",
            "website": "https://openai.com",
        },
    ).json()["result"]

    response = client.get(f"/api/v1/companies/{company['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "result": company,
    }


def test_get_company_by_id_returns_404_when_company_does_not_exist(
    client: TestClient,
):
    response = client.get("/api/v1/companies/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Company not found"}


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"name": "A"}, "name"),
        ({"name": "A" * 121}, "name"),
        ({"name": "Valid", "description": "x" * 2001}, "description"),
        ({"name": "Valid", "website": "ftp://example.com"}, "website"),
        ({"name": "Valid", "id": 10}, "id"),
    ],
)
def test_create_company_rejects_invalid_input(
    client: TestClient, payload: dict[str, object], field: str
):
    response = client.post("/api/v1/companies", json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == field for error in response.json()["detail"])
