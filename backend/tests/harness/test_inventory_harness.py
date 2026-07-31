"""Harness scenario for User Story 1 (T031): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

from src.domain.inventory.integration_event import EventType, IntegrationEventInput
from src.domain.inventory.service import InventoryService

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def test_inventory_harness_scenarios(db_session):
    service = InventoryService(db_session)

    def happy_path() -> None:
        service.ingest_event(
            IntegrationEventInput(
                source_system="pos-1",
                event_type=EventType.STOCK_UPDATE,
                sku_id="SKU-H1",
                location_id="STORE-H1",
                shelf_delta=15,
            )
        )
        position = service.list_positions(sku_id="SKU-H1", location_id="STORE-H1")[0]
        assert position.reconciled_total == 15, "stock update should be visible immediately"

    def failure_path() -> None:
        # A malformed event (negative delta driving quantity below zero) must clamp to 0
        # rather than raising or corrupting state.
        service.ingest_event(
            IntegrationEventInput(
                source_system="pos-1",
                event_type=EventType.SALE,
                sku_id="SKU-H2",
                location_id="STORE-H1",
                shelf_delta=999,
            )
        )
        position = service.list_positions(sku_id="SKU-H2", location_id="STORE-H1")[0]
        assert position.shelf_quantity == 0, "quantities must never go negative"

    def data_quality_edge_case() -> None:
        # Duplicate/out-of-order events: replaying the same event_id must not double-apply.
        event = service.ingest_event(
            IntegrationEventInput(
                source_system="pos-1",
                event_type=EventType.STOCK_UPDATE,
                sku_id="SKU-H3",
                location_id="STORE-H1",
                shelf_delta=10,
            )
        )
        # Simulate a duplicate delivery of the same underlying event by reusing its id
        # directly against the repository (what the replay path would do on redelivery).
        from src.domain.inventory.models import InventoryPositionRepository

        repo = InventoryPositionRepository(db_session)
        repo.upsert_delta(
            sku_id="SKU-H3", location_id="STORE-H1", shelf_delta=10, event_id=event.id
        )
        position = service.list_positions(sku_id="SKU-H3", location_id="STORE-H1")[0]
        assert position.shelf_quantity == 10, "duplicate event_id must not double-apply"

    run_scenarios(
        [
            HarnessScenario("stock update visible immediately", ScenarioKind.HAPPY_PATH, happy_path),
            HarnessScenario("quantities never negative", ScenarioKind.FAILURE_PATH, failure_path),
            HarnessScenario(
                "duplicate/out-of-order events deduplicated",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
