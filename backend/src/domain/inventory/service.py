"""Inventory reconciliation service (T032, US1, FR-001).

Thin facade over `InventoryPositionRepository` and `IntegrationEventService` used by the
API router, keeping HTTP concerns (routers/inventory.py) separate from persistence and
event-application logic.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.inventory.integration_event import IntegrationEventInput, IntegrationEventService
from src.domain.inventory.models import InventoryPosition, InventoryPositionRepository


class InventoryService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = InventoryPositionRepository(session)
        self._event_service = IntegrationEventService(session)

    def list_positions(
        self, sku_id: str | None = None, location_id: str | None = None
    ) -> list[InventoryPosition]:
        return self._repo.list(sku_id=sku_id, location_id=location_id)

    def ingest_event(self, event_input: IntegrationEventInput, *, source_unavailable: bool = False):
        return self._event_service.ingest(event_input, source_unavailable=source_unavailable)
