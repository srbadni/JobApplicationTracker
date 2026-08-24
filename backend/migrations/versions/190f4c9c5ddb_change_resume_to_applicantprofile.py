"""change Resume to ApplicantProfile

Revision ID: 190f4c9c5ddb
Revises: 25026458f98e
Create Date: 2026-08-24 12:27:42.148733
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "190f4c9c5ddb"
down_revision: Union[str, Sequence[str], None] = "25026458f98e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "job_applications_folder",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=120),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "applicant_profiles",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "applicant_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["applicant_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.drop_constraint(
        op.f("job_applications_resume_id_fkey"),
        "job_applications",
        type_="foreignkey",
    )

    op.drop_column(
        "job_applications",
        "resume_id",
    )

    op.drop_table("resumes")

    op.drop_table("company_folders")

    op.drop_constraint(
        op.f("job_postings_created_by_id_fkey"),
        "job_postings",
        type_="foreignkey",
    )

    op.drop_column(
        "job_postings",
        "created_by_id",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.create_table(
        "company_folders",
        sa.Column(
            "id",
            sa.INTEGER(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.VARCHAR(length=120),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("company_folders_pkey"),
        ),
    )

    op.create_table(
        "resumes",
        sa.Column(
            "id",
            sa.INTEGER(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "applicant_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "file_path",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.VARCHAR(length=20),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["applicant_id"],
            ["user.id"],
            name=op.f("resumes_applicant_id_fkey"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("resumes_pkey"),
        ),
    )

    op.add_column(
        "job_postings",
        sa.Column(
            "created_by_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
    )

    op.create_foreign_key(
        op.f("job_postings_created_by_id_fkey"),
        "job_postings",
        "user",
        ["created_by_id"],
        ["id"],
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "resume_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
    )

    op.create_foreign_key(
        op.f("job_applications_resume_id_fkey"),
        "job_applications",
        "resumes",
        ["resume_id"],
        ["id"],
    )

    op.drop_table("applicant_profiles")
    op.drop_table("job_applications_folder")