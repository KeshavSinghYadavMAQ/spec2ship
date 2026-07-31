"""Harness scenario for User Story 5 (T068): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition
from src.domain.transfer_balance.engine import TransferBalanceEngine
from src.domain.transfer_balance.models import FeasibilityStatus, TransferSuggestionRepository

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def _position(location_id: str, shelf: int) -> InventoryPosition:
    return InventoryPosition(
        id=str(uuid.uuid4()),
        sku_id="SKU-T1",
        location_id=location_id,
        shelf_quantity=shelf,
        backroom_quantity=0,
        freshness_at=datetime.now(UTC),
    )


def _policy(location_id: str, **overrides) -> ProductLocationPolicy:
    defaults = dict(
        id=str(uuid.uuid4()),
        sku_id="SKU-T1",
        location_id=location_id,
        low_stock_threshold=10,
        out_of_stock_threshold=0,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
    )
    defaults.update(overrides)
    return ProductLocationPolicy(**defaults)


def test_transfer_harness_scenarios(db_session):
    repo = TransferSuggestionRepository(db_session)
    engine = TransferBalanceEngine(repo)

    def happy_path() -> None:
        suggestion = engine.generate_suggestion(
            source_position=_position("STORE-T1", shelf=80),
            source_policy=_policy("STORE-T1"),
            destination_position=_position("STORE-T2", shelf=5),
            destination_policy=_policy("STORE-T2"),
        )
        assert suggestion is not None
        assert suggestion.feasibility_status == FeasibilityStatus.FEASIBLE.value

    def failure_path() -> None:
        # Destination already above its reorder point: no transfer should be suggested.
        suggestion = engine.generate_suggestion(
            source_position=_position("STORE-T1", shelf=80),
            source_policy=_policy("STORE-T1"),
            destination_position=_position("STORE-T2", shelf=30),
            destination_policy=_policy("STORE-T2"),
        )
        assert suggestion is None

    def data_quality_edge_case() -> None:
        # A tiny source min_qty gap must not allow a transfer that breaches the
        # source's own minimum threshold, even though a large surplus/deficit exists.
        suggestion = engine.generate_suggestion(
            source_position=_position("STORE-T1", shelf=11),
            source_policy=_policy("STORE-T1", max_qty=10, min_qty=10),
            destination_position=_position("STORE-T2", shelf=0),
            destination_policy=_policy("STORE-T2", reorder_point=50),
        )
        assert suggestion is not None
        assert suggestion.suggested_quantity == 1, "must not breach source min_qty of 10"

    run_scenarios(
        [
            HarnessScenario(
                "feasible surplus-to-deficit transfer", ScenarioKind.HAPPY_PATH, happy_path
            ),
            HarnessScenario(
                "no deficit at destination", ScenarioKind.FAILURE_PATH, failure_path
            ),
            HarnessScenario(
                "source minimum threshold respected",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
