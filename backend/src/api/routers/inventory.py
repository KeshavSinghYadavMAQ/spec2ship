"""Inventory API router (T033, T034, US1).

`GET /v1/inventory/positions` (FR-001) and `POST /v1/inventory/events` (FR-012, FR-022,
rate-limited per FR-024 via `RateLimitMiddleware`). Ingesting an event also runs threshold
evaluation (US2, FR-002) so a breach raises a `StockAlert` in the same request rather than
requiring a separate background sweep.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.audit import AuditLogWriter
from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.alerting.evaluation_service import ThresholdEvaluationService
from src.domain.alerting.policy_service import PolicyService
from src.domain.inventory.integration_event import IntegrationEventInput
from src.domain.inventory.models import InventoryPosition, InventoryPositionRead
from src.domain.inventory.service import InventoryService
from src.domain.security.scope_service import ScopeResolutionService
from src.infrastructure.cache import CacheClient, get_cache_client
from src.infrastructure.cost_guardrails import cost_guardrails
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/positions", response_model=list[InventoryPositionRead])
async def list_positions(
    sku_id: str | None = None,
    location_id: str | None = None,
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(*Role)),
) -> list[InventoryPositionRead]:
    def _query() -> list[InventoryPositionRead]:
        scope = ScopeResolutionService(session).resolve_for_user(current_user.user_id)
        service = InventoryService(session)
        positions = service.list_positions(
            sku_id=sku_id,
            location_id=location_id,
            scoped_location_ids=set(scope.location_ids),
            all_locations=scope.all_locations,
        )
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


@router.get("/positions/{position_id}", response_model=InventoryPositionRead)
async def get_position(
    position_id: str,
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(*Role)),
) -> InventoryPositionRead:
    def _query() -> InventoryPositionRead:
        scope = ScopeResolutionService(session).resolve_for_user(current_user.user_id)
        position = session.get(InventoryPosition, position_id)
        if position is None:
            raise HTTPException(status_code=404, detail="Inventory position not found")
        if not scope.all_locations and position.location_id not in scope.location_ids:
            AuditLogWriter(session).record_rls_denied(
                actor_user_id=current_user.user_id,
                resource_type="inventory_position",
                resource_id=position_id,
                metadata={"location_id": position.location_id},
            )
            raise HTTPException(status_code=404, detail="Inventory position not found")
        return InventoryPositionRead.model_validate(position)

    return await run_in_threadpool(_query)


@router.post("/events", status_code=202)
async def ingest_event(
    event_input: IntegrationEventInput,
    session: Session = Depends(get_db_session),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, str]:
    def _ingest() -> dict[str, str]:
        service = InventoryService(session)
        event = service.ingest_event(event_input)
        cost_guardrails.record_ingested_event()
        _evaluate_thresholds(session, cache, event_input)
        return {"id": event.id, "processing_state": event.processing_state}

    return await run_in_threadpool(_ingest)


def _evaluate_thresholds(
    session: Session, cache: CacheClient, event_input: IntegrationEventInput
) -> None:
    """Run threshold evaluation for the affected sku/location after an event is applied,
    so a breach raises a `StockAlert` synchronously (US2, FR-002)."""
    policies = PolicyService(session).list_policies(
        sku_id=event_input.sku_id, location_id=event_input.location_id
    )
    policy = next((p for p in policies if p.is_active), None)
    if policy is None:
        return

    positions = InventoryService(session).list_positions(
        sku_id=event_input.sku_id, location_id=event_input.location_id
    )
    if not positions:
        return

    ThresholdEvaluationService(session, cache).evaluate(positions[0], policy)
