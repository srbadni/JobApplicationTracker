"""replace username with Iranian mobile phone number

Revision ID: 20260818_02
Revises: 03c06dab4273
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260818_02"
down_revision: str | Sequence[str] | None = "03c06dab4273"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nullable supports legacy/OAuth accounts; all password registration schemas
    # require and validate a phone number.
    op.add_column("user", sa.Column("phone_number", sa.String(length=11), nullable=True))
    op.create_index(op.f("ix_user_phone_number"), "user", ["phone_number"], unique=True)
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_constraint(op.f("uq_user_username"), "user", type_="unique")
    op.drop_column("user", "username")


def downgrade() -> None:
    op.add_column("user", sa.Column("username", sa.String(length=20), nullable=True))
    op.execute(sa.text("UPDATE \"user\" SET username = 'user_' || id"))
    op.alter_column("user", "username", nullable=False)
    op.create_unique_constraint(op.f("uq_user_username"), "user", ["username"])
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.drop_index(op.f("ix_user_phone_number"), table_name="user")
    op.drop_column("user", "phone_number")
