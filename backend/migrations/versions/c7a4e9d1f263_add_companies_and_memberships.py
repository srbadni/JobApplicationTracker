"""add companies, memberships, and user type

Revision ID: c7a4e9d1f263
Revises: 8f2c1d4a6b90
Create Date: 2026-08-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c7a4e9d1f263"
down_revision: str | Sequence[str] | None = "8f2c1d4a6b90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("user_type", sa.String(length=20), server_default="applicant", nullable=False),
    )
    op.create_check_constraint(
        "ck_user_user_type",
        "user",
        "user_type IN ('applicant', 'employer')",
    )
    op.alter_column("user", "user_type", server_default=None)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
    )
    op.create_table(
        "company_memberships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_company_memberships_company_id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_company_memberships_user_id"),
        sa.PrimaryKeyConstraint("id", name="pk_company_memberships"),
        sa.UniqueConstraint("user_id", name="uq_company_memberships_user_id"),
    )


def downgrade() -> None:
    op.drop_table("company_memberships")
    op.drop_table("companies")
    op.drop_constraint("ck_user_user_type", "user", type_="check")
    op.drop_column("user", "user_type")
