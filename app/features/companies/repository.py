from sqlalchemy.orm import Session

from app.features.companies.model import Company
from app.features.companies.schemas import CompanyCreate


class CompanyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: CompanyCreate) -> Company:
        company = Company(
            name=data.name,
            description=data.description,
            website=str(data.website) if data.website is not None else None,
        )
        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company
