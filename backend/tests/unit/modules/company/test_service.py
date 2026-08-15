from unittest.mock import AsyncMock, patch

import pytest

from src.modules.common.exceptions import ResourceNotFoundError
from src.modules.company.schemas import CompanyCreate
from src.modules.company.service import CompanyService


@pytest.fixture
def company_service() -> CompanyService:
    return CompanyService()


async def test_create_normalizes_website(company_service: CompanyService) -> None:
    created = {
        "id": 1,
        "name": "Acme",
        "description": None,
        "website": "https://example.com/",
    }

    with patch("src.modules.company.service.crud_companies.create", new=AsyncMock(return_value=created)) as create:
        result = await company_service.create(CompanyCreate(name="Acme", website="https://example.com"), AsyncMock())

    assert result == created
    internal = create.await_args.kwargs["object"]
    assert internal.website == "https://example.com/"


async def test_get_by_id_returns_company(company_service: CompanyService) -> None:
    company = {"id": 7, "name": "Acme"}

    with patch("src.modules.company.service.crud_companies.get", new=AsyncMock(return_value=company)) as get:
        result = await company_service.get_by_id(7, AsyncMock())

    assert result == company
    assert get.await_args.kwargs["id"] == 7


async def test_get_by_id_raises_domain_error_when_missing(company_service: CompanyService) -> None:
    with patch("src.modules.company.service.crud_companies.get", new=AsyncMock(return_value=None)):
        with pytest.raises(ResourceNotFoundError, match="Company with ID 99 not found"):
            await company_service.get_by_id(99, AsyncMock())
