from typing import Annotated

from fastapi import Depends

from ..job_posting.service import JobPostingService

JobPostingServiceDep = Annotated[
    JobPostingService,
    Depends(JobPostingService),
]