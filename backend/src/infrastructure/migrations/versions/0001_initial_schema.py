"""Initial schema for foundational + US1/US2/US3 entities (T010).

Generated to match the SQLAlchemy models directly (InventoryPosition, IntegrationEvent,
ProductLocationPolicy, StockAlert, ReplenishmentRecommendation, StorePriorityProfile,
UserRoleAssignment, AuditLogEntry) rather than via autogenerate, since this is the first
revision.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inventory_positions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id", sa.String(64), index=True, nullable=False),
        sa.Column("location_id", sa.String(64), index=True, nullable=False),
        sa.Column("shelf_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("backroom_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_event_id", sa.String(36), nullable=True),
        sa.Column("freshness_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_freshness_warning", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("sku_id", "location_id", name="uq_inventory_sku_location"),
    )

    op.create_table(
        "integration_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_system", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("processing_state", sa.String(32), nullable=False, server_default="queued"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "product_location_policies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id", sa.String(64), index=True, nullable=False),
        sa.Column("location_id", sa.String(64), index=True, nullable=False),
        sa.Column("low_stock_threshold", sa.Integer, nullable=False),
        sa.Column("out_of_stock_threshold", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reorder_point", sa.Integer, nullable=False, server_default="0"),
        sa.Column("min_qty", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_qty", sa.Integer, nullable=False, server_default="0"),
        sa.Column("safety_stock", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("edit_lock_held", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("updated_by", sa.String(128), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("change_history", sa.JSON, nullable=True),
        sa.UniqueConstraint("sku_id", "location_id", name="uq_policy_sku_location"),
    )

    op.create_table(
        "stock_alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id", sa.String(64), index=True, nullable=False),
        sa.Column("location_id", sa.String(64), index=True, nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="Open"),
        sa.Column("owner_user_id", sa.String(128), nullable=True),
        sa.Column("routing_channel", sa.String(64), nullable=True),
        sa.Column("suppressed_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "replenishment_recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id", sa.String(64), index=True, nullable=False),
        sa.Column("location_id", sa.String(64), index=True, nullable=False),
        sa.Column("recommended_quantity", sa.Integer, nullable=False),
        sa.Column("recommended_by_date", sa.Date, nullable=False),
        sa.Column("policy_snapshot", sa.JSON, nullable=False),
        sa.Column("rationale", sa.JSON, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="proposed"),
        sa.Column("override_reason", sa.String(512), nullable=True),
        sa.Column("actionability_rating", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "store_priority_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(64), index=True, unique=True, nullable=False),
        sa.Column("region", sa.String(64), nullable=False),
        sa.Column("recent_consumption_rate", sa.Float, nullable=False, server_default="0"),
        sa.Column("region_weight", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("consumption_weight", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("current_priority_rank", sa.Integer, nullable=False, server_default="0"),
        sa.Column("priority_factors", sa.JSON, nullable=True),
    )

    op.create_table(
        "user_role_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(128), index=True, nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("location_scope", sa.JSON, nullable=True),
    )

    op.create_table(
        "audit_log_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_user_id", sa.String(128), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("before", sa.JSON, nullable=True),
        sa.Column("after", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_log_entries")
    op.drop_table("user_role_assignments")
    op.drop_table("store_priority_profiles")
    op.drop_table("replenishment_recommendations")
    op.drop_table("stock_alerts")
    op.drop_table("product_location_policies")
    op.drop_table("integration_events")
    op.drop_table("inventory_positions")
