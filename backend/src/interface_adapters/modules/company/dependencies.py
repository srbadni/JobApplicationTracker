from typing import Annotated

from fastapi import Depends

from ....frameworks.dependencies import AsyncSessionDep
from ....use_cases.company import GetCompanyByTitle
from ...repositories.company import SqlAlchemyCompanyReader


def get_company_use_case(db: AsyncSessionDep) -> GetCompanyByTitle:
    """Composition point joining the use case to its SQLAlchemy adapter."""
    return GetCompanyByTitle(SqlAlchemyCompanyReader(db))


GetCompanyByTitleDep = Annotated[GetCompanyByTitle, Depends(get_company_use_case)]
