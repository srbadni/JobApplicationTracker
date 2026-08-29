from typing import Annotated

from fastapi import Depends

from ..job_categories.service import JobCategoriesService

JobCategoriesServiceDep = Annotated[JobCategoriesService, Depends(JobCategoriesService)]