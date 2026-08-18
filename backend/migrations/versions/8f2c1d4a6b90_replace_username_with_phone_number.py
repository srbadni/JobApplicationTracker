"""replace username with required Iranian phone number

Revision ID: 8f2c1d4a6b90
Revises: 3b8adc2c9521
Create Date: 2026-08-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8f2c1d4a6b90"
down_revision: str | Sequence[str] | None = "3b8adc2c9521"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_column("user", "username")
    op.add_column("user", sa.Column("phone_number", sa.String(length=11), nullable=True))
    op.execute(sa.text("UPDATE \"user\" SET phone_number = '090' || LPAD((id % 100000000)::text, 8, '0')"))
    op.alter_column("user", "phone_number", existing_type=sa.String(length=11), nullable=False)


def downgrade() -> None:
    op.drop_column("user", "phone_number")
    op.add_column("user", sa.Column("username", sa.String(length=20), nullable=False))
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
