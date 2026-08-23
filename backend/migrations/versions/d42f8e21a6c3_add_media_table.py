"""add media table

Revision ID: d42f8e21a6c3
Revises: 740a44a2bc26
Create Date: 2026-08-23
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d42f8e21a6c3"
down_revision: str | Sequence[str] | None = "740a44a2bc26"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "media",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "category IN ('company_logo', 'user_avatar', 'resume', 'attachment')",
            name="ck_media_category",
        ),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(op.f("ix_media_storage_key"), "media", ["storage_key"], unique=False)
    op.create_index(op.f("ix_media_uploaded_by_id"), "media", ["uploaded_by_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_media_uploaded_by_id"), table_name="media")
    op.drop_index(op.f("ix_media_storage_key"), table_name="media")
    op.drop_table("media")
