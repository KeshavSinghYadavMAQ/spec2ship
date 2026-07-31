"""`ProductLocationPolicy` model (T021, FR-016, FR-023).

Shared read dependency for US2/US3 (alert thresholds + replenishment control values).
Full admin CRUD/validation (US7) is implemented in `policy_service.py` in a later phase;
this module defines the persistence model needed now so alerting/replenishment can read
threshold configuration.
"""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db import Base


class ProductLocationPolicy(Base):
    __tablename__ = "product_location_policies"
    __table_args__ = (UniqueConstraint("sku_id", "location_id", name="uq_policy_sku_location"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    location_id: Mapped[str] = mapped_column(String(64), index=True)
    low_stock_threshold: Mapped[int] = mapped_column(Integer)
    out_of_stock_threshold: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, default=0)
    min_qty: Mapped[int] = mapped_column(Integer, default=0)
    max_qty: Mapped[int] = mapped_column(Integer, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    edit_lock_held: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    change_history: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
