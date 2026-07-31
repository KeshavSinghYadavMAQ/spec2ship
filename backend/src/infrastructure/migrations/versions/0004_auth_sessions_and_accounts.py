"""Adds authentication tables for user accounts and server-side sessions (T007).

Introduces `user_accounts` and `auth_sessions` to support HttpOnly cookie sessions and
lockout-aware authentication workflows for feature 003.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_auth_sessions_and_accounts"
down_revision: str | None = "0003_sample_data_seed_records"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("login_identifier", sa.String(256), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_attempt_count_window", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_attempt_window_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("login_identifier", name="uq_user_accounts_login_identifier"),
    )
    op.create_index("ix_user_accounts_login_identifier", "user_accounts", ["login_identifier"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_account_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_account_id"], ["user_accounts.id"], name="fk_auth_sessions_user_account"),
    )
    op.create_index("ix_auth_sessions_user_account_id", "auth_sessions", ["user_account_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_account_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index("ix_user_accounts_login_identifier", table_name="user_accounts")
    op.drop_table("user_accounts")
