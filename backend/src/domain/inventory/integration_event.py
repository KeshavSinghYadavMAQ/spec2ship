"""`IntegrationEvent` model and queue-and-replay processing service (T019, FR-022).

Lifecycle: `queued -> processing -> applied`, or `queued -> dead_lettered -> replayed ->
applied` when the source system was unavailable (Clarifications 2026-07-31 Q2). Normalized
inbound inventory/sales/return events are persisted here for auditability and then applied
to `InventoryPosition` via the repository in `models.py`.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.domain.inventory.models import InventoryPositionRepository
from src.infrastructure.db import Base
from src.infrastructure.observability import get_logger, metrics

logger = get_logger(__name__)


class EventType(StrEnum):
    STOCK_UPDATE = "stock_update"
    SALE = "sale"
    RETURN = "return"


class ProcessingState(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    APPLIED = "applied"
    DEAD_LETTERED = "dead_lettered"
    REPLAYED = "replayed"


class IntegrationEvent(Base):
    __tablename__ = "integration_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_system: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    processing_state: Mapped[str] = mapped_column(String(32), default=ProcessingState.QUEUED)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IntegrationEventInput(BaseModel):
    source_system: str
    event_type: EventType
    sku_id: str
    location_id: str
    shelf_delta: int = 0
    backroom_delta: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


def _signed_deltas(event_type: EventType, shelf_delta: int, backroom_delta: int) -> tuple[int, int]:
    """Normalize deltas by event type: sales/returns reduce/increase shelf stock, while
    stock_update events carry an already-signed absolute adjustment."""
    if event_type == EventType.SALE:
        return -abs(shelf_delta) if shelf_delta else 0, -abs(backroom_delta) if backroom_delta else 0
    if event_type == EventType.RETURN:
        return abs(shelf_delta), abs(backroom_delta)
    return shelf_delta, backroom_delta


class IntegrationEventService:
    """Applies queued/replayed events to inventory positions (FR-022 queue-and-replay)."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = InventoryPositionRepository(session)

    def ingest(
        self, event_input: IntegrationEventInput, *, source_unavailable: bool = False
    ) -> IntegrationEvent:
        event = IntegrationEvent(
            id=str(uuid.uuid4()),
            source_system=event_input.source_system,
            event_type=event_input.event_type.value,
            payload=event_input.model_dump(mode="json"),
            processing_state=(
                ProcessingState.DEAD_LETTERED if source_unavailable else ProcessingState.QUEUED
            ),
            received_at=datetime.now(UTC),
        )
        self._session.add(event)
        self._session.flush()

        if not source_unavailable:
            self._apply(event, event_input, freshness_warning=False)
        else:
            metrics.increment("integration_event.dead_lettered")
            logger.warning(
                "Event dead-lettered pending replay",
                extra={"context": {"event_id": event.id, "source_system": event_input.source_system}},
            )

        return event

    def replay(self, event: IntegrationEvent) -> IntegrationEvent:
        """Replay a previously dead-lettered event once the source system recovers."""
        event_input = IntegrationEventInput.model_validate(event.payload)
        event.processing_state = ProcessingState.REPLAYED
        self._apply(event, event_input, freshness_warning=True)
        metrics.increment("integration_event.replayed")
        return event

    def _apply(
        self, event: IntegrationEvent, event_input: IntegrationEventInput, *, freshness_warning: bool
    ) -> None:
        event.processing_state = ProcessingState.PROCESSING
        shelf_delta, backroom_delta = _signed_deltas(
            event_input.event_type, event_input.shelf_delta, event_input.backroom_delta
        )
        self._repo.upsert_delta(
            sku_id=event_input.sku_id,
            location_id=event_input.location_id,
            shelf_delta=shelf_delta,
            backroom_delta=backroom_delta,
            event_id=event.id,
            freshness_warning=freshness_warning,
        )
        event.processing_state = ProcessingState.APPLIED
        event.applied_at = datetime.now(UTC)
        self._session.flush()
        metrics.increment("integration_event.applied")
