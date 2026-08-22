from fastapi import APIRouter

from ....infrastructure.auth.routes import router as auth_router
from ....modules.api_keys.routes import router as api_keys_router
from ....modules.company.routes import router as companies_router
from ....modules.employer.route import router as employers_router
from ....modules.rate_limit.routes import router as rate_limits_router
from ....modules.tier.routes import router as tiers_router
from ....modules.user.routes import router as users_router
from ....modules.job_posting.routes import router as job_postings_router
from ....modules.job_categories.route import router as job_categories_router

router = APIRouter(prefix="/v1")
router.include_router(users_router, prefix="/users")
router.include_router(tiers_router, prefix="/tiers")
router.include_router(rate_limits_router, prefix="/rate-limits")
router.include_router(auth_router, prefix="/auth")
router.include_router(api_keys_router, prefix="/api-keys")
router.include_router(companies_router, prefix="/companies")
router.include_router(employers_router, prefix="/employers")
router.include_router(job_postings_router, prefix="/job_postings")
router.include_router(job_categories_router, prefix="/job_categories")
