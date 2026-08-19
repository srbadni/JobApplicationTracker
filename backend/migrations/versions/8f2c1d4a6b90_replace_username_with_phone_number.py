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
    """Move legacy username databases to phone numbers.

    ``setup_initial_data`` historically creates tables from the latest ORM
    metadata before Alembic is run.  Such databases already have phone_number
    and no username index, so every operation must be conditional.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("user")}
    indexes = {index["name"] for index in inspector.get_indexes("user")}

    if "ix_user_username" in indexes:
        op.drop_index(op.f("ix_user_username"), table_name="user")
    if "username" in columns:
        op.drop_column("user", "username")
    if "phone_number" not in columns:
        op.add_column("user", sa.Column("phone_number", sa.String(length=11), nullable=True))
        op.execute(sa.text("UPDATE \"user\" SET phone_number = '090' || LPAD((id % 100000000)::text, 8, '0')"))
        op.alter_column("user", "phone_number", existing_type=sa.String(length=11), nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("user")}

    if "phone_number" in columns:
        op.drop_column("user", "phone_number")
    if "username" not in columns:
        op.add_column("user", sa.Column("username", sa.String(length=20), nullable=True))
        op.execute(sa.text("UPDATE \"user\" SET username = 'user' || id::text"))
        op.alter_column("user", "username", existing_type=sa.String(length=20), nullable=False)
        op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
