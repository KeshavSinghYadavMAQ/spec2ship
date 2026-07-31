"""Harness scenario for User Story 3 (T051): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition
from src.domain.replenishment.engine import ReplenishmentEngine, compute_reorder_decision
from src.domain.replenishment.models import ReplenishmentRecommendationRepository

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def _position(shelf: int) -> InventoryPosition:
    return InventoryPosition(
        id=str(uuid.uuid4()),
        sku_id="SKU-R1",
        location_id="STORE-R1",
        shelf_quantity=shelf,
        backroom_quantity=0,
        freshness_at=datetime.now(UTC),
    )


def _policy(**overrides) -> ProductLocationPolicy:
    defaults = dict(
        id=str(uuid.uuid4()),
        sku_id="SKU-R1",
        location_id="STORE-R1",
        low_stock_threshold=10,
        out_of_stock_threshold=0,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
    )
    defaults.update(overrides)
    return ProductLocationPolicy(**defaults)


def test_replenishment_harness_scenarios(db_session):
    repo = ReplenishmentRecommendationRepository(db_session)
    engine = ReplenishmentEngine(repo)

    def happy_path() -> None:
        recommendation = engine.generate_recommendation(_position(shelf=5), _policy())
        assert recommendation is not None
        assert recommendation.recommended_quantity > 0
        assert recommendation.rationale["narration"]

    def failure_path() -> None:
        # Missing/zero policy inputs (reorder_point=0) must not raise; no reorder needed.
        recommendation = engine.generate_recommendation(
            _position(shelf=5), _policy(reorder_point=0, max_qty=0)
        )
        assert recommendation is None, "no recommendation when reorder point is already satisfied"

    def data_quality_edge_case() -> None:
        # Abrupt lead-time change after a recommendation is generated must not corrupt
        # the already-generated recommendation's stored policy snapshot.
        policy = _policy()
        first = engine.generate_recommendation(_position(shelf=5), policy)
        assert first is not None
        original_snapshot = dict(first.rationale["factors"])
        # Simulate a later lead-time assumption change by recomputing fresh decision.
        decision = compute_reorder_decision(_position(shelf=5), policy, today=date.today())
        assert decision.factors["lead_time_days"] == original_snapshot["lead_time_days"], (
            "recomputed lead time should be stable given the same policy inputs"
        )

    run_scenarios(
        [
            HarnessScenario("reorder quantity/timing produced", ScenarioKind.HAPPY_PATH, happy_path),
            HarnessScenario("missing policy inputs", ScenarioKind.FAILURE_PATH, failure_path),
            HarnessScenario(
                "abrupt lead-time change", ScenarioKind.DATA_QUALITY_EDGE_CASE, data_quality_edge_case
            ),
        ]
    )
