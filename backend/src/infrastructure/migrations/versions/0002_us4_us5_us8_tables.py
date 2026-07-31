"""Schema additions for US4 forecasting, US5 transfer balance, and US8 priority
narration (T058/T066, US4/US5/US8).

Adds `demand_forecasts` and `transfer_suggestions` tables, plus a `narration` column on
`store_priority_profiles` for the T107 explainer agent's output.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_us4_us5_us8_tables"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "demand_forecasts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id", sa.String(64), index=True, nullable=False),
        sa.Column("location_id", sa.String(64), index=True, nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("forecast_quantity", sa.Float, nullable=False),
        sa.Column("trend_factor", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("seasonality_factor", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("promotion_factor", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("history_points_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_indicator", sa.String(32), nullable=False),
        sa.Column("factors", sa.JSON, nullable=True),
        sa.Column("narration", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "transfer_suggestions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id", sa.String(64), index=True, nullable=False),
        sa.Column("source_location_id", sa.String(64), index=True, nullable=False),
        sa.Column("destination_location_id", sa.String(64), index=True, nullable=False),
        sa.Column("suggested_quantity", sa.Integer, nullable=False),
        sa.Column("feasibility_status", sa.String(32), nullable=False),
        sa.Column("feasibility_reason", sa.String(256), nullable=True),
        sa.Column("priority_rank", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="proposed"),
        sa.Column("factors", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.add_column(
        "store_priority_profiles", sa.Column("narration", sa.String(1024), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("store_priority_profiles", "narration")
    op.drop_table("transfer_suggestions")
    op.drop_table("demand_forecasts")
