from fastapi import APIRouter

from ....modules.company.routes import router as company_router
from ....modules.job_posting.routes import router as job_postings_router

router = APIRouter(prefix="/companies", tags=["Companies"])
router.include_router(company_router)
router.include_router(job_postings_router, prefix="/job-postings")
