from fastapi import APIRouter

from ....infrastructure.auth.routes import router as auth_router
from ....modules.api_keys.routes import router as api_keys_router
from ....modules.city.routes import router as cities_router
from ....modules.company.routes import router as companies_router
from ....modules.employer.route import router as employers_router
from ....modules.job_categories.route import router as job_categories_router
from ....modules.job_posting.routes import router as job_postings_router
from ....modules.media.routes import router as media_router
from ....modules.province.routes import router as provinces_router
from ....modules.rate_limit.routes import router as rate_limits_router
from ....modules.tier.routes import router as tiers_router
from ....modules.user.routes import router as users_router
from ....modules.jobs_search.routes import router as jobs_router
from ....modules.company_activity.router import router as company_activity_router

router = APIRouter(prefix="/v1")
router.include_router(users_router, prefix="/users")
router.include_router(tiers_router, prefix="/tiers")
router.include_router(rate_limits_router, prefix="/rate-limits")
router.include_router(auth_router, prefix="/auth")
router.include_router(api_keys_router, prefix="/api-keys")
router.include_router(companies_router, prefix="/companies")
router.include_router(employers_router, prefix="/employers")
router.include_router(job_postings_router, prefix="/companies/job-postings", tags=["Companies"])
router.include_router(job_categories_router, prefix="/job-categories")
router.include_router(provinces_router, prefix="/provinces")
router.include_router(cities_router, prefix="/cities")
router.include_router(media_router, prefix="/media")
router.include_router(jobs_router, prefix="/jobs-search")
router.include_router(company_activity_router, prefix="/company_activities")
