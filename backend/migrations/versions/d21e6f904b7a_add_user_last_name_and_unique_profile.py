"""add user last name and make applicant profiles one-to-one

Revision ID: d21e6f904b7a
Revises: 190f4c9c5ddb
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d21e6f904b7a"
down_revision: str | Sequence[str] | None = "190f4c9c5ddb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add and backfill last names before enforcing both constraints."""
    op.add_column("user", sa.Column("last_name", sa.String(length=30), nullable=True))

    # Existing rows predate the separate last-name field. Copying their previous
    # display name retains that information and makes the NOT NULL change safe.
    op.execute(sa.text('UPDATE "user" SET last_name = name WHERE last_name IS NULL'))
    op.alter_column("user", "last_name", existing_type=sa.String(length=30), nullable=False)

    op.create_unique_constraint(
        "uq_applicant_profiles_applicant_id",
        "applicant_profiles",
        ["applicant_id"],
    )


def downgrade() -> None:
    """Remove the one-to-one constraint and last-name column."""
    op.drop_constraint(
        "uq_applicant_profiles_applicant_id",
        "applicant_profiles",
        type_="unique",
    )
    op.drop_column("user", "last_name")
