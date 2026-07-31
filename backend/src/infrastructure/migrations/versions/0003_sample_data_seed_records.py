"""Adds the `sample_data_seed_records` ledger table (T005, feature 002, US1).

Standalone table, no foreign keys to existing domain tables (research.md item 2 -
isolation decision): `entity_type`/`entity_id` reference other tables logically only.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_sample_data_seed_records"
down_revision: str | None = "0002_us4_us5_us8_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sample_data_seed_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(256), nullable=False),
        sa.Column("seed_batch_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", name="uq_sample_data_seed_entity"),
    )
    op.create_index(
        "ix_sample_data_seed_records_entity_type",
        "sample_data_seed_records",
        ["entity_type"],
    )
    op.create_index(
        "ix_sample_data_seed_records_entity_id",
        "sample_data_seed_records",
        ["entity_id"],
    )
    op.create_index(
        "ix_sample_data_seed_records_seed_batch_id",
        "sample_data_seed_records",
        ["seed_batch_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_sample_data_seed_records_seed_batch_id", table_name="sample_data_seed_records")
    op.drop_index("ix_sample_data_seed_records_entity_id", table_name="sample_data_seed_records")
    op.drop_index("ix_sample_data_seed_records_entity_type", table_name="sample_data_seed_records")
    op.drop_table("sample_data_seed_records")
