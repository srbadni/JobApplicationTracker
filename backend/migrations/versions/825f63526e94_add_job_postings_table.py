"""add job_postings table

Revision ID: 825f63526e94
Revises: c7a4e9d1f263
Create Date: 2026-08-20 13:03:30.652852

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "825f63526e94"
down_revision: str | Sequence[str] | None = "c7a4e9d1f263"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# PostgreSQL enums are independent schema objects. ``create_type=False`` keeps
# ``op.create_table`` from trying to create them a second time; ``upgrade``
# creates only the missing types explicitly with ``checkfirst=True``.
employment_type_enum = postgresql.ENUM(
    "full_time",
    "part_time",
    "internship",
    name="employmenttype",
    create_type=False,
)
work_mode_enum = postgresql.ENUM(
    "onsite",
    "remote",
    "hybrid",
    name="workmode",
    create_type=False,
)
work_experience_enum = postgresql.ENUM(
    "not_important",
    "less_than_3_years",
    "three_to_six_years",
    "more_than_6_years",
    name="relevantworkexperience",
    create_type=False,
)
minimum_education_enum = postgresql.ENUM(
    "not_important",
    "diploma",
    "associate",
    "bachelor",
    "master",
    "doctorate",
    name="minimumeducationlevel",
    create_type=False,
)
gender_enum = postgresql.ENUM(
    "not_important",
    "male",
    "female",
    name="gender",
    create_type=False,
)
military_status_enum = postgresql.ENUM(
    "not_important",
    "completed",
    "educational_exemption",
    "permanent_exemption",
    name="militaryservicestatus",
    create_type=False,
)

job_posting_enums = (
    employment_type_enum,
    work_mode_enum,
    work_experience_enum,
    minimum_education_enum,
    gender_enum,
    military_status_enum,
)


def upgrade() -> None:
    """Create job postings without duplicating a create_all-created table or enum."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # ``setup_initial_data`` may already have created the current ORM schema via
    # Base.metadata.create_all(). In that case Alembic only needs to record this
    # revision; trying to recreate the table would first recreate its enum types.
    if inspector.has_table("job_postings"):
        return

    for enum_type in job_posting_enums:
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("job_title", sa.String(length=150), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("company_overview", sa.Text(), nullable=False),
        sa.Column("employment_type", employment_type_enum, nullable=False),
        sa.Column("work_mode", work_mode_enum, nullable=False),
        sa.Column("minimum_salary", sa.BigInteger(), nullable=True),
        sa.Column("is_latin_text", sa.Boolean(), nullable=False),
        sa.Column("work_experience", work_experience_enum, nullable=False),
        sa.Column("minimum_education", minimum_education_enum, nullable=False),
        sa.Column("gender", gender_enum, nullable=False),
        sa.Column("military_status", military_status_enum, nullable=False),
        sa.Column("post_notifications", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop job postings and its PostgreSQL enum types when present."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("job_postings"):
        op.drop_table("job_postings")

    for enum_type in reversed(job_posting_enums):
        enum_type.drop(bind, checkfirst=True)
