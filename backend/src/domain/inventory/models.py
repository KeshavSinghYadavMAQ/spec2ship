"""`InventoryPosition` model and repository (T020, US1, FR-001, FR-012).

Shared read dependency for US2-US8. Reconciliation logic (shelf+backroom totals,
dedupe/out-of-order handling) lives in `service.py`; this module holds the persistence
model, Pydantic I/O schemas, and a thin repository.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class InventoryPosition(Base):
    __tablename__ = "inventory_positions"
    __table_args__ = (UniqueConstraint("sku_id", "location_id", name="uq_inventory_sku_location"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    location_id: Mapped[str] = mapped_column(String(64), index=True)
    shelf_quantity: Mapped[int] = mapped_column(Integer, default=0)
    backroom_quantity: Mapped[int] = mapped_column(Integer, default=0)
    last_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    freshness_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    data_freshness_warning: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def reconciled_total(self) -> int:
        return self.shelf_quantity + self.backroom_quantity


class InventoryPositionRead(BaseModel):
    id: str
    sku_id: str
    location_id: str
    shelf_quantity: int
    backroom_quantity: int
    reconciled_total: int
    freshness_at: datetime
    data_freshness_warning: bool

    model_config = {"from_attributes": True}


class InventoryPositionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_sku_location(self, sku_id: str, location_id: str) -> InventoryPosition | None:
        return (
            self._session.query(InventoryPosition)
            .filter_by(sku_id=sku_id, location_id=location_id)
            .one_or_none()
        )

    def list(
        self,
        sku_id: str | None = None,
        location_id: str | None = None,
        scoped_location_ids: set[str] | None = None,
        all_locations: bool = True,
    ) -> list[InventoryPosition]:
        query = self._session.query(InventoryPosition)
        if sku_id:
            query = query.filter_by(sku_id=sku_id)
        if location_id:
            query = query.filter_by(location_id=location_id)
        if not all_locations:
            scoped_location_ids = scoped_location_ids or set()
            if scoped_location_ids:
                query = query.filter(InventoryPosition.location_id.in_(scoped_location_ids))
            else:
                return []
        return query.order_by(InventoryPosition.sku_id, InventoryPosition.location_id).all()

    def upsert_delta(
        self,
        *,
        sku_id: str,
        location_id: str,
        shelf_delta: int = 0,
        backroom_delta: int = 0,
        event_id: str,
        freshness_warning: bool = False,
    ) -> InventoryPosition:
        """Apply a signed quantity delta, deduplicating by (sku_id, location_id, last_event_id)
        to satisfy the duplicate/out-of-order events edge case."""
        position = self.get_by_sku_location(sku_id, location_id)
        if position is not None and position.last_event_id == event_id:
            return position  # duplicate event already applied

        if position is None:
            position = InventoryPosition(
                id=str(uuid.uuid4()),
                sku_id=sku_id,
                location_id=location_id,
                shelf_quantity=max(0, shelf_delta),
                backroom_quantity=max(0, backroom_delta),
                last_event_id=event_id,
                freshness_at=datetime.now(UTC),
                data_freshness_warning=freshness_warning,
            )
            self._session.add(position)
        else:
            position.shelf_quantity = max(0, position.shelf_quantity + shelf_delta)
            position.backroom_quantity = max(0, position.backroom_quantity + backroom_delta)
            position.last_event_id = event_id
            position.freshness_at = datetime.now(UTC)
            position.data_freshness_warning = freshness_warning

        self._session.flush()
        return position
