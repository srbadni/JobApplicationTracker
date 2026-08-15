import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("name", ["", "   ", "x"])
async def test_create_company_rejects_invalid_name(client: AsyncClient, name: str) -> None:
    response = await client.post("/api/v1/companies", json={"name": name})

    assert response.status_code == 422


async def test_create_company_rejects_invalid_website(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/companies",
        json={"name": "Acme", "website": "ftp://example.com"},
    )

    assert response.status_code == 422


async def test_create_and_get_company(client: AsyncClient) -> None:
    payload = {
        "name": "  Acme Corporation  ",
        "description": "Makes useful things.",
        "website": "https://example.com/about",
    }
    created = await client.post("/api/v1/companies", json=payload)

    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Acme Corporation"
    assert body["description"] == payload["description"]
    assert body["website"] == payload["website"]
    assert body["id"] > 0
    assert body["created_at"]
    assert body["updated_at"]

    fetched = await client.get(f"/api/v1/companies/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


async def test_get_missing_company_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/companies/2147483647")

    assert response.status_code == 404
    assert response.json() == {"detail": "Company not found"}
