from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.company.models import Company


async def test_standalone_company_creation_is_not_exposed(client: AsyncClient) -> None:
    """Companies are created only as part of atomic employer registration."""
    response = await client.post("/api/v1/companies", json={"name": "Acme"})

    assert response.status_code == 404


async def test_get_company(client: AsyncClient, db_session: AsyncSession) -> None:
    company = Company(
        name="Acme Corporation",
        description="Makes useful things.",
        website="https://example.com/about",
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    response = await client.get(f"/api/v1/companies/{company.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == company.id
    assert body["name"] == company.name
    assert body["description"] == company.description
    assert body["website"] == company.website
    assert body["created_at"]
    assert body["updated_at"]


async def test_get_missing_company_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/companies/2147483647")

    assert response.status_code == 404
    assert response.json() == {"detail": "Company not found"}
