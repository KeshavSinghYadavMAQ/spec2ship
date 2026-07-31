"""Inventory API router (T033, T034, US1).

`GET /v1/inventory/positions` (FR-001) and `POST /v1/inventory/events` (FR-012, FR-022,
rate-limited per FR-024 via `RateLimitMiddleware`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.inventory.integration_event import IntegrationEventInput
from src.domain.inventory.models import InventoryPositionRead
from src.domain.inventory.service import InventoryService
from src.infrastructure.cost_guardrails import cost_guardrails
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/positions", response_model=list[InventoryPositionRead])
async def list_positions(
    sku_id: str | None = None,
    location_id: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[InventoryPositionRead]:
    def _query() -> list[InventoryPositionRead]:
        service = InventoryService(session)
        positions = service.list_positions(sku_id=sku_id, location_id=location_id)
        return [
            InventoryPositionRead(
                id=p.id,
                sku_id=p.sku_id,
                location_id=p.location_id,
                shelf_quantity=p.shelf_quantity,
                backroom_quantity=p.backroom_quantity,
                reconciled_total=p.reconciled_total,
                freshness_at=p.freshness_at,
                data_freshness_warning=p.data_freshness_warning,
            )
            for p in positions
        ]

    return await run_in_threadpool(_query)


@router.post("/events", status_code=202)
async def ingest_event(
    event_input: IntegrationEventInput,
    session: Session = Depends(get_db_session),
) -> dict[str, str]:
    def _ingest() -> dict[str, str]:
        service = InventoryService(session)
        event = service.ingest_event(event_input)
        cost_guardrails.record_ingested_event()
        return {"id": event.id, "processing_state": event.processing_state}

    return await run_in_threadpool(_ingest)
