from typing import Annotated

from fastapi import Depends

from ...infrastructure.dependencies import AsyncSessionDep
from .service import JobsSearchService

def get_jobs_search_service(
    db: AsyncSessionDep,
) -> JobsSearchService:
    return JobsSearchService(db)

JobsSearchServiceDep = Annotated[
    JobsSearchService,
    Depends(get_jobs_search_service)
]