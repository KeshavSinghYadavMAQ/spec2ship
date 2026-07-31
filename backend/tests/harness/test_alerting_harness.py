"""Harness scenario for User Story 2 (T041): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.alerting import routing as routing_module
from src.domain.alerting.evaluation_service import ThresholdEvaluationService
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def _position(sku_id: str, location_id: str, shelf: int, backroom: int = 0) -> InventoryPosition:
    return InventoryPosition(
        id=str(uuid.uuid4()),
        sku_id=sku_id,
        location_id=location_id,
        shelf_quantity=shelf,
        backroom_quantity=backroom,
        freshness_at=datetime.now(UTC),
    )


def _policy(
    sku_id: str, location_id: str, low_stock: int = 10, out_of_stock: int = 0
) -> ProductLocationPolicy:
    return ProductLocationPolicy(
        id=str(uuid.uuid4()),
        sku_id=sku_id,
        location_id=location_id,
        low_stock_threshold=low_stock,
        out_of_stock_threshold=out_of_stock,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
    )


def test_alerting_harness_scenarios(db_session, fake_cache, monkeypatch):
    evaluator = ThresholdEvaluationService(db_session, fake_cache)

    def happy_path() -> None:
        position = _position("SKU-A1", "STORE-A1", shelf=5)
        policy = _policy("SKU-A1", "STORE-A1")
        alert = evaluator.evaluate(position, policy)
        assert alert is not None and alert.severity == "low_stock", "low-stock alert routed"

    def failure_path() -> None:
        # Notification dispatch failure must not prevent the alert from being persisted.
        def _raise(*args, **kwargs):
            raise RuntimeError("channel unavailable")

        monkeypatch.setattr(
            routing_module,
            "dispatch_notification",
            lambda **kw: routing_module.RoutingResult(kw["channel"], False),
        )
        position = _position("SKU-A2", "STORE-A1", shelf=0)
        policy = _policy("SKU-A2", "STORE-A1")
        alert = evaluator.evaluate(position, policy)
        assert alert is not None, "alert persists even if the routing channel is unavailable"

    def data_quality_edge_case() -> None:
        # Repeated breaches in a short window must be suppressed (no duplicate alerts).
        position = _position("SKU-A3", "STORE-A1", shelf=5)
        policy = _policy("SKU-A3", "STORE-A1")
        first = evaluator.evaluate(position, policy)
        second = evaluator.evaluate(position, policy)
        assert first is not None and second is None, "duplicate breaches suppressed per policy"

    run_scenarios(
        [
            HarnessScenario("low-stock alert routed", ScenarioKind.HAPPY_PATH, happy_path),
            HarnessScenario("routing channel unavailable", ScenarioKind.FAILURE_PATH, failure_path),
            HarnessScenario(
                "repeated breaches suppressed", ScenarioKind.DATA_QUALITY_EDGE_CASE, data_quality_edge_case
            ),
        ]
    )
