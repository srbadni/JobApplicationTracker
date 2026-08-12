from app.features.companies.model import Company
from app.features.companies.repository import CompanyRepository
from app.features.companies.schemas import CompanyCreate


class CompanyService:
    def __init__(self, repository: CompanyRepository) -> None:
        self.repository = repository

    def create_company(self, data: CompanyCreate) -> Company:
        return self.repository.create(data)

    def list_companies(self) -> list[Company]:
        return self.repository.list()

    def get_company_by_id(self, data: int) -> Company | None:
        return self.repository.get_by_id(data)
