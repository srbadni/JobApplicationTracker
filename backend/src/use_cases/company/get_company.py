from typing import Protocol

from ...domain.company import Company, CompanyNotFoundError


class CompanyReader(Protocol):
    """Output port implemented by an outer persistence adapter."""

    async def get_by_title(self, title: str) -> Company | None: ...


class GetCompanyByTitle:
    """Fetch a company without knowing which database or web framework is used."""

    def __init__(self, companies: CompanyReader) -> None:
        self._companies = companies

    async def execute(self, title: str) -> Company:
        company = await self._companies.get_by_title(title)
        if company is None:
            raise CompanyNotFoundError(f"Company with title {title!r} was not found")
        return company
