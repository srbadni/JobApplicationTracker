from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.job_posting.schemas import JobPostingRequest
from src.modules.job_posting.service import JobPostingService


def _posting_request() -> JobPostingRequest:
    return JobPostingRequest(
        job_title="Backend Engineer",
        job_description="Build and maintain APIs.",
        company_overview="A product company.",
        job_category_id=3,
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
async def test_create_job_posting_uses_users_company_membership() -> None:
    membership = MagicMock(company_id=7)
    db = MagicMock()
    db.scalar = AsyncMock(return_value=membership)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await JobPostingService().create_job_posting(
        post=_posting_request(),
        db=db,
        user_id=11,
    )

    assert result.company_id == 7
    assert result.created_by_id == 11
    assert result.job_category_id == 3
    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_create_job_posting_rejects_user_without_company_membership() -> None:
    db = MagicMock()
    db.scalar = AsyncMock(return_value=None)
    db.commit = AsyncMock()

    with pytest.raises(ValueError, match="Company membership not found"):
        await JobPostingService().create_job_posting(
            post=_posting_request(),
            db=db,
            user_id=11,
        )

    db.add.assert_not_called()
    db.commit.assert_not_awaited()
