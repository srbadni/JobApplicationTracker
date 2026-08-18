"""add companies and one-company-per-user memberships

Revision ID: c9e34f6b2a11
Revises: 8f2c1d4a6b90
Create Date: 2026-08-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c9e34f6b2a11"
down_revision: str | Sequence[str] | None = "8f2c1d4a6b90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user", sa.Column("user_type", sa.String(length=20), nullable=False, server_default="applicant"))
    op.create_check_constraint("ck_user_user_type", "user", "user_type IN ('applicant', 'employer')")
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "company_memberships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_company_memberships_user_id"),
    )
    op.create_index("ix_company_memberships_company_id", "company_memberships", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_company_memberships_company_id", table_name="company_memberships")
    op.drop_table("company_memberships")
    op.drop_table("companies")
    op.drop_constraint("ck_user_user_type", "user", type_="check")
    op.drop_column("user", "user_type")
