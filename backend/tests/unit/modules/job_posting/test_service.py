from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.common.exceptions import PermissionDeniedError
from src.modules.job_posting.schemas import JobPostingRequest
from src.modules.job_posting.service import JobPostingService


def _posting_request() -> JobPostingRequest:
    return JobPostingRequest(
        job_title="Backend Engineer",
        job_description="Build and maintain APIs.",
        company_overview="A product company.",
        employment_type="full_time",
        work_mode="remote",
        minimum_salary=1000,
        is_latin_text=True,
        work_experience="less_than_3_years",
        minimum_education="bachelor",
        gender="not_important",
        military_status="not_important",
    )


@pytest.mark.asyncio
async def test_create_job_posting_for_company_admin() -> None:
    membership = MagicMock(company_id=7, is_admin=True)
    db = MagicMock()
    db.scalar = AsyncMock(return_value=membership)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    service = JobPostingService()

    result = await service.create_job_posting(
        post=_posting_request(),
        db=db,
        company_id=7,
        user_id=11,
    )

    assert result.company_id == 7
    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
@pytest.mark.parametrize("membership", [None, MagicMock(company_id=7, is_admin=False)])
async def test_create_job_posting_rejects_non_admin(membership) -> None:
    db = MagicMock()
    db.scalar = AsyncMock(return_value=membership)
    db.commit = AsyncMock()
    service = JobPostingService()

    with pytest.raises(PermissionDeniedError):
        await service.create_job_posting(
            post=_posting_request(),
            db=db,
            company_id=7,
            user_id=11,
        )

    db.add.assert_not_called()
    db.commit.assert_not_awaited()
