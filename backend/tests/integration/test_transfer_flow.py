"""Integration test: imbalance detection + feasibility-constrained suggestion journey
(T067, US5, FR-008, FR-009, FR-020)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition
from src.domain.transfer_balance.engine import TransferBalanceEngine
from src.domain.transfer_balance.models import FeasibilityStatus, TransferSuggestionRepository


def _position(location_id: str, shelf: int) -> InventoryPosition:
    return InventoryPosition(
        id=str(uuid.uuid4()),
        sku_id="SKU-1",
        location_id=location_id,
        shelf_quantity=shelf,
        backroom_quantity=0,
        freshness_at=datetime.now(UTC),
    )


def _policy(location_id: str, **overrides) -> ProductLocationPolicy:
    defaults = dict(
        id=str(uuid.uuid4()),
        sku_id="SKU-1",
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


def test_generates_feasible_suggestion_from_surplus_to_deficit(db_session):
    repo = TransferSuggestionRepository(db_session)
    engine = TransferBalanceEngine(repo)

    suggestion = engine.generate_suggestion(
        source_position=_position("STORE-1", shelf=80),
        source_policy=_policy("STORE-1"),
        destination_position=_position("STORE-2", shelf=5),
        destination_policy=_policy("STORE-2"),
        priority_rank=2,
    )

    assert suggestion is not None
    assert suggestion.feasibility_status == FeasibilityStatus.FEASIBLE.value
    assert suggestion.suggested_quantity > 0
    assert suggestion.priority_rank == 2


def test_no_suggestion_when_source_has_no_surplus(db_session):
    repo = TransferSuggestionRepository(db_session)
    engine = TransferBalanceEngine(repo)

    suggestion = engine.generate_suggestion(
        source_position=_position("STORE-1", shelf=20),
        source_policy=_policy("STORE-1"),
        destination_position=_position("STORE-2", shelf=5),
        destination_policy=_policy("STORE-2"),
    )

    assert suggestion is None
