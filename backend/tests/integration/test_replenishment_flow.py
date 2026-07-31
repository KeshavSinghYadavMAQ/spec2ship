"""Integration test: recommendation generation + explanation journey (T050, US3, FR-004,
FR-005)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition
from src.domain.replenishment.engine import ReplenishmentEngine
from src.domain.replenishment.models import ReplenishmentRecommendationRepository


def test_recommendation_includes_explanation_and_updates_on_policy_change(db_session):
    position = InventoryPosition(
        id=str(uuid.uuid4()),
        sku_id="SKU-1",
        location_id="STORE-1",
        shelf_quantity=5,
        backroom_quantity=0,
        freshness_at=datetime.now(UTC),
    )
    policy = ProductLocationPolicy(
        id=str(uuid.uuid4()),
        sku_id="SKU-1",
        location_id="STORE-1",
        low_stock_threshold=10,
        out_of_stock_threshold=0,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
    )
    repo = ReplenishmentRecommendationRepository(db_session)
    engine = ReplenishmentEngine(repo)

    recommendation = engine.generate_recommendation(position, policy)
    assert recommendation is not None
    assert recommendation.recommended_quantity > 0
    assert recommendation.rationale["narration"], "explanation must not be empty"
    assert "factors" in recommendation.rationale

    # Policy change (higher max_qty) should be reflected in a regenerated recommendation.
    policy.max_qty = 80
    updated = engine.generate_recommendation(position, policy)
    assert updated.recommended_quantity > recommendation.recommended_quantity
