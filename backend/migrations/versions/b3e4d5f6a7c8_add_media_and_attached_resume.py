"""add media and attached resume

Revision ID: b3e4d5f6a7c8
Revises: 5a135fbf35d9
Create Date: 2026-08-24 22:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3e4d5f6a7c8"
down_revision: str | Sequence[str] | None = "5a135fbf35d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create private media metadata and connect resumes to applicant profiles."""
    op.create_table(
        "media",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=127), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "category IN ('company_logo', 'user_avatar', 'resume', 'attachment')",
            name="ck_media_category",
        ),
        sa.CheckConstraint("size_bytes > 0", name="ck_media_size_bytes_positive"),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_category"), "media", ["category"], unique=False)
    op.create_index(op.f("ix_media_owner_id"), "media", ["owner_id"], unique=False)
    op.create_index(op.f("ix_media_storage_key"), "media", ["storage_key"], unique=True)

    op.add_column("applicant_profiles", sa.Column("attached_resume_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(
        "uq_applicant_profiles_attached_resume_id",
        "applicant_profiles",
        ["attached_resume_id"],
    )
    op.create_foreign_key(
        "fk_applicant_profiles_attached_resume_id_media",
        "applicant_profiles",
        "media",
        ["attached_resume_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Remove attached resumes and private media metadata."""
    op.drop_constraint(
        "fk_applicant_profiles_attached_resume_id_media",
        "applicant_profiles",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_applicant_profiles_attached_resume_id",
        "applicant_profiles",
        type_="unique",
    )
    op.drop_column("applicant_profiles", "attached_resume_id")

    op.drop_index(op.f("ix_media_storage_key"), table_name="media")
    op.drop_index(op.f("ix_media_owner_id"), table_name="media")
    op.drop_index(op.f("ix_media_category"), table_name="media")
    op.drop_table("media")
