"""Integration test: threshold breach -> alert -> routing -> suppression journey (T040,
US2, FR-002, FR-003)."""

from __future__ import annotations

from src.domain.alerting.evaluation_service import ThresholdEvaluationService
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.integration_event import EventType, IntegrationEventInput
from src.domain.inventory.service import InventoryService


def _make_policy(db_session, **overrides) -> ProductLocationPolicy:
    import uuid

    policy = ProductLocationPolicy(
        id=str(uuid.uuid4()),
        sku_id=overrides.get("sku_id", "SKU-1"),
        location_id=overrides.get("location_id", "STORE-1"),
        low_stock_threshold=overrides.get("low_stock_threshold", 10),
        out_of_stock_threshold=overrides.get("out_of_stock_threshold", 0),
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
    )
    db_session.add(policy)
    db_session.flush()
    return policy


def test_low_stock_breach_creates_alert_and_suppresses_duplicates(db_session, fake_cache):
    policy = _make_policy(db_session, sku_id="SKU-1", location_id="STORE-1")
    inventory = InventoryService(db_session)
    inventory.ingest_event(
        IntegrationEventInput(
            source_system="pos-1",
            event_type=EventType.STOCK_UPDATE,
            sku_id="SKU-1",
            location_id="STORE-1",
            shelf_delta=8,
        )
    )
    position = inventory.list_positions(sku_id="SKU-1", location_id="STORE-1")[0]

    evaluator = ThresholdEvaluationService(db_session, fake_cache)
    first_alert = evaluator.evaluate(position, policy)
    assert first_alert is not None
    assert first_alert.severity == "low_stock"
    assert first_alert.status == "Open"

    # A second breach within the suppression window must not create a duplicate alert.
    second_alert = evaluator.evaluate(position, policy)
    assert second_alert is None
