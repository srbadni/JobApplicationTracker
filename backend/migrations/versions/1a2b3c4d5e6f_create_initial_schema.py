"""create initial schema

Revision ID: 1a2b3c4d5e6f
Revises:
Create Date: 2026-08-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "1a2b3c4d5e6f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the tables that existed before Alembic started tracking changes."""
    op.create_table(
        "tiers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=100), nullable=False),
        sa.Column("profile_image_url", sa.String(), nullable=False),
        sa.Column("tier_id", sa.Integer(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("google_id", sa.String(length=50), nullable=True),
        sa.Column("github_id", sa.String(length=50), nullable=True),
        sa.Column("oauth_provider", sa.String(length=20), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("oauth_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("oauth_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["tier_id"], ["tiers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("github_id"),
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"])
    op.create_index(op.f("ix_user_github_id"), "user", ["github_id"])
    op.create_index(op.f("ix_user_google_id"), "user", ["google_id"])
    op.create_index(op.f("ix_user_tier_id"), "user", ["tier_id"])
    op.create_index(op.f("ix_user_username"), "user", ["username"])
    op.create_table(
        "rate_limits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tier_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("limit", sa.Integer(), nullable=False),
        sa.Column("period", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["tier_id"], ["tiers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_rate_limits_tier_id"), "rate_limits", ["tier_id"])

    permission_resource = postgresql.ENUM(
        "CONVERSATIONS",
        "CREDITS",
        "AI_USAGE",
        "USER_PROFILE",
        "ANALYTICS",
        "ADMIN",
        "BILLING",
        "API_KEYS",
        "WILDCARD",
        name="keypermissionresource",
    )
    permission_action = postgresql.ENUM(
        "READ",
        "WRITE",
        "DELETE",
        "CREATE",
        "UPDATE",
        "LIST",
        "ADMIN",
        "WILDCARD",
        name="keypermissionaction",
    )
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
        sa.Column("key_prefix", sa.String(length=20), nullable=False),
        sa.Column("permissions", postgresql.JSON(), nullable=False),
        sa.Column("usage_limits", postgresql.JSON(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_ip", sa.String(length=45), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("key_metadata", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index("idx_api_keys_expires_at", "api_keys", ["expires_at"])
    op.create_index("idx_api_keys_prefix", "api_keys", ["key_prefix"])
    op.create_index("idx_api_keys_user_active", "api_keys", ["user_id", "is_active"])
    op.create_index(op.f("ix_api_keys_key_hash"), "api_keys", ["key_hash"])
    op.create_index(op.f("ix_api_keys_key_prefix"), "api_keys", ["key_prefix"])
    op.create_index(op.f("ix_api_keys_user_id"), "api_keys", ["user_id"])
    op.create_table(
        "key_permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("api_key_id", sa.Integer(), nullable=False),
        sa.Column("resource", permission_resource, nullable=False),
        sa.Column("action", permission_action, nullable=False),
        sa.Column("conditions", postgresql.JSON(), nullable=True),
        sa.Column("is_allowed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_key_permissions_action"), "key_permissions", ["action"])
    op.create_index(op.f("ix_key_permissions_api_key_id"), "key_permissions", ["api_key_id"])
    op.create_index("idx_key_permissions_key_resource", "key_permissions", ["api_key_id", "resource", "action"], unique=True)
    op.create_index("idx_key_permissions_resource_action", "key_permissions", ["resource", "action"])
    op.create_index(op.f("ix_key_permissions_resource"), "key_permissions", ["resource"])
    op.create_table(
        "key_usage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("api_key_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("cost_microcents", sa.BigInteger(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("usage_metadata", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_key_usage_endpoint", "key_usage", ["endpoint"])
    op.create_index("idx_key_usage_key_created", "key_usage", ["api_key_id", "created_at"])
    op.create_index("idx_key_usage_status", "key_usage", ["status_code"])
    op.create_index("idx_key_usage_user_created", "key_usage", ["user_id", "created_at"])
    op.create_index(op.f("ix_key_usage_api_key_id"), "key_usage", ["api_key_id"])
    op.create_index(op.f("ix_key_usage_endpoint"), "key_usage", ["endpoint"])
    op.create_index(op.f("ix_key_usage_status_code"), "key_usage", ["status_code"])
    op.create_index(op.f("ix_key_usage_user_id"), "key_usage", ["user_id"])


def downgrade() -> None:
    op.drop_table("key_usage")
    op.drop_table("key_permissions")
    op.drop_table("api_keys")
    op.drop_table("rate_limits")
    op.drop_table("user")
    op.drop_table("tiers")
    postgresql.ENUM(name="keypermissionaction").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="keypermissionresource").drop(op.get_bind(), checkfirst=True)
