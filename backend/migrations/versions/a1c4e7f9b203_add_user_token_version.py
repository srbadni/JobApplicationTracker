"""add user token version for JWT revocation

Revision ID: a1c4e7f9b203
Revises: 825f63526e94
Create Date: 2026-08-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1c4e7f9b203"
down_revision: str | Sequence[str] | None = "825f63526e94"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the credential epoch used to revoke stateless JWTs."""
    op.add_column(
        "user",
        sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
    )
    op.alter_column("user", "token_version", server_default=None)


def downgrade() -> None:
    """Remove the JWT credential epoch."""
    op.drop_column("user", "token_version")
