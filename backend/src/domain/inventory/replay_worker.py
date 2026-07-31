"""Replay/reconciliation worker with data-freshness warning flag (T035, FR-022).

Consumes dead-lettered `IntegrationEvent` records once the source system reconnects and
replays them through `IntegrationEventService`, marking affected `InventoryPosition`
rows with `data_freshness_warning=True` until the backlog is fully reconciled (edge case:
"a store syncs delayed transactions after temporary offline operation").
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.inventory.integration_event import (
    IntegrationEvent,
    IntegrationEventService,
    ProcessingState,
)
from src.infrastructure.observability import get_logger

logger = get_logger(__name__)


def replay_dead_lettered_events(session: Session, *, batch_size: int = 100) -> int:
    """Replay all dead-lettered events for the given session. Returns the number replayed.

    Intended to run as a scheduled/background task once a source system's outage clears;
    see FR-022 (queue-and-replay resilience) and the corresponding edge case in spec.md.
    """
    service = IntegrationEventService(session)
    dead_lettered = (
        session.execute(
            select(IntegrationEvent)
            .where(IntegrationEvent.processing_state == ProcessingState.DEAD_LETTERED)
            .limit(batch_size)
        )
        .scalars()
        .all()
    )

    for event in dead_lettered:
        service.replay(event)

    if dead_lettered:
        logger.info(
            "Replayed dead-lettered events",
            extra={"context": {"count": len(dead_lettered)}},
        )

    return len(dead_lettered)
