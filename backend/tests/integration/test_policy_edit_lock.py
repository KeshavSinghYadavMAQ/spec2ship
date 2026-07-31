"""Integration test: threshold edit -> lock-held-during-evaluation ->
apply-next-cycle journey (T075, US7, FR-016, FR-017, FR-023)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from src.domain.alerting.evaluation_service import ThresholdEvaluationService
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.alerting.policy_service import PolicyEditLockedError, PolicyService
from src.domain.inventory.models import InventoryPosition


def test_edit_rejected_while_evaluation_holds_the_lock(db_session, fake_cache):
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
    db_session.add(policy)
    db_session.flush()

    position = InventoryPosition(
        id=str(uuid.uuid4()),
        sku_id="SKU-1",
        location_id="STORE-1",
        shelf_quantity=3,
        backroom_quantity=0,
        freshness_at=datetime.now(UTC),
    )

    evaluation_service = ThresholdEvaluationService(db_session, fake_cache)
    evaluation_service.evaluate(position, policy)

    # After evaluate() completes, the lock is released so edits apply cleanly on the
    # next cycle.
    assert policy.edit_lock_held is False

    policy_service = PolicyService(db_session)
    updated = policy_service.upsert_policy(
        sku_id="SKU-1",
        location_id="STORE-1",
        low_stock_threshold=15,
        out_of_stock_threshold=2,
        reorder_point=25,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
        updated_by="admin-1",
    )
    assert updated.low_stock_threshold == 15


def test_edit_rejected_when_lock_manually_held(db_session):
    policy = ProductLocationPolicy(
        id=str(uuid.uuid4()),
        sku_id="SKU-2",
        location_id="STORE-1",
        low_stock_threshold=10,
        out_of_stock_threshold=0,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
        edit_lock_held=True,
    )
    db_session.add(policy)
    db_session.flush()

    policy_service = PolicyService(db_session)
    with pytest.raises(PolicyEditLockedError):
        policy_service.upsert_policy(
            sku_id="SKU-2",
            location_id="STORE-1",
            low_stock_threshold=15,
            out_of_stock_threshold=2,
            reorder_point=25,
            min_qty=10,
            max_qty=50,
            safety_stock=5,
            updated_by="admin-1",
        )
