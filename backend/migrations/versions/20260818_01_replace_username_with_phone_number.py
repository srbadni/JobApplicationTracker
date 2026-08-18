"""replace username with required Iranian phone number

Revision ID: 20260818_01
Revises: 03c06dab4273
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260818_01"
down_revision: str | None = "03c06dab4273"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user", sa.Column("phone_number", sa.String(length=14), nullable=True))
    # Existing accounts receive a unique, syntactically valid placeholder so the
    # migration can safely make the new field mandatory. Users can replace it later.
    op.execute("UPDATE \"user\" SET phone_number = '0900' || LPAD(id::text, 7, '0')")
    op.alter_column("user", "phone_number", nullable=False)
    op.create_index(op.f("ix_user_phone_number"), "user", ["phone_number"], unique=True)
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_column("user", "username")


def downgrade() -> None:
    op.add_column("user", sa.Column("username", sa.String(length=20), nullable=True))
    op.execute("UPDATE \"user\" SET username = 'user' || id::text")
    op.alter_column("user", "username", nullable=False)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.drop_index(op.f("ix_user_phone_number"), table_name="user")
    op.drop_column("user", "phone_number")
