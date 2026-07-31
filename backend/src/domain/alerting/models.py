"""`StockAlert` model with 5-state lifecycle (T042, US2, FR-002, FR-003).

Lifecycle (Clarifications 2026-07-31 Q4): Open -> Acknowledged -> Escalated -> Snoozed ->
Resolved. Valid transitions: Open->Acknowledged, Open->Escalated, Acknowledged->Escalated,
Acknowledged->Snoozed, Escalated->Snoozed, any of {Acknowledged, Escalated, Snoozed}->
Resolved. Resolved is terminal; a new breach opens a new alert record rather than
reopening a resolved one, preserving audit history (data-model.md).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class Severity(StrEnum):
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class AlertStatus(StrEnum):
    OPEN = "Open"
    ACKNOWLEDGED = "Acknowledged"
    ESCALATED = "Escalated"
    SNOOZED = "Snoozed"
    RESOLVED = "Resolved"


VALID_TRANSITIONS: dict[AlertStatus, set[AlertStatus]] = {
    AlertStatus.OPEN: {AlertStatus.ACKNOWLEDGED, AlertStatus.ESCALATED},
    AlertStatus.ACKNOWLEDGED: {AlertStatus.ESCALATED, AlertStatus.SNOOZED, AlertStatus.RESOLVED},
    AlertStatus.ESCALATED: {AlertStatus.SNOOZED, AlertStatus.RESOLVED},
    AlertStatus.SNOOZED: {AlertStatus.RESOLVED},
    AlertStatus.RESOLVED: set(),
}


class InvalidTransitionError(Exception):
    def __init__(self, current: AlertStatus, target: AlertStatus) -> None:
        super().__init__(f"Cannot transition alert from '{current}' to '{target}'")
        self.current = current
        self.target = target


class StockAlert(Base):
    __tablename__ = "stock_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    location_id: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default=AlertStatus.OPEN)
    owner_user_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    routing_channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    suppressed_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def transition_to(self, target: AlertStatus) -> None:
        current = AlertStatus(self.status)
        if target not in VALID_TRANSITIONS[current]:
            raise InvalidTransitionError(current, target)
        self.status = target.value
        self.updated_at = datetime.now(UTC)


class StockAlertRead(BaseModel):
    id: str
    sku_id: str
    location_id: str
    severity: Severity
    status: AlertStatus
    owner_user_id: str | None
    routing_channel: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StockAlertRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self, *, sku_id: str, location_id: str, severity: Severity, routing_channel: str | None
    ) -> StockAlert:
        now = datetime.now(UTC)
        alert = StockAlert(
            id=str(uuid.uuid4()),
            sku_id=sku_id,
            location_id=location_id,
            severity=severity.value,
            status=AlertStatus.OPEN.value,
            routing_channel=routing_channel,
            created_at=now,
            updated_at=now,
        )
        self._session.add(alert)
        self._session.flush()
        return alert

    def get(self, alert_id: str) -> StockAlert | None:
        return self._session.get(StockAlert, alert_id)

    def list(
        self,
        status: str | None = None,
        severity: str | None = None,
        scoped_location_ids: set[str] | None = None,
        all_locations: bool = True,
    ) -> list[StockAlert]:
        query = self._session.query(StockAlert)
        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)
        if not all_locations:
            scoped_location_ids = scoped_location_ids or set()
            if scoped_location_ids:
                query = query.filter(StockAlert.location_id.in_(scoped_location_ids))
            else:
                return []
        return query.order_by(StockAlert.created_at.desc()).all()

    def find_active_for_sku_location(self, sku_id: str, location_id: str) -> StockAlert | None:
        return (
            self._session.query(StockAlert)
            .filter(
                StockAlert.sku_id == sku_id,
                StockAlert.location_id == location_id,
                StockAlert.status != AlertStatus.RESOLVED.value,
            )
            .order_by(StockAlert.created_at.desc())
            .first()
        )
