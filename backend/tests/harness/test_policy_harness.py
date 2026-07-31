"""Harness scenario for User Story 7 (T076): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

import uuid

import pytest
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.alerting.policy_service import (
    PolicyEditLockedError,
    PolicyService,
    PolicyValidationError,
)

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def test_policy_harness_scenarios(db_session):
    service = PolicyService(db_session)

    def happy_path() -> None:
        policy = service.upsert_policy(
            sku_id="SKU-P1",
            location_id="STORE-P1",
            low_stock_threshold=10,
            out_of_stock_threshold=2,
            reorder_point=20,
            min_qty=10,
            max_qty=50,
            safety_stock=5,
            updated_by="admin-1",
        )
        assert policy.low_stock_threshold == 10
        assert policy.change_history and policy.change_history[-1]["updated_by"] == "admin-1"

    def failure_path() -> None:
        # out_of_stock_threshold above low_stock_threshold is invalid and must be
        # rejected rather than silently accepted.
        with pytest.raises(PolicyValidationError):
            service.upsert_policy(
                sku_id="SKU-P2",
                location_id="STORE-P1",
                low_stock_threshold=10,
                out_of_stock_threshold=20,
                reorder_point=20,
                min_qty=10,
                max_qty=50,
                safety_stock=5,
                updated_by="admin-1",
            )

    def data_quality_edge_case() -> None:
        # Editing a policy while its edit lock is held (simulating an in-flight
        # evaluation) must be rejected with a lock error, not silently overwritten.
        locked = ProductLocationPolicy(
            id=str(uuid.uuid4()),
            sku_id="SKU-P3",
            location_id="STORE-P1",
            low_stock_threshold=10,
            out_of_stock_threshold=0,
            reorder_point=20,
            min_qty=10,
            max_qty=50,
            safety_stock=5,
            edit_lock_held=True,
        )
        db_session.add(locked)
        db_session.flush()
        with pytest.raises(PolicyEditLockedError):
            service.upsert_policy(
                sku_id="SKU-P3",
                location_id="STORE-P1",
                low_stock_threshold=15,
                out_of_stock_threshold=2,
                reorder_point=25,
                min_qty=10,
                max_qty=50,
                safety_stock=5,
                updated_by="admin-1",
            )

    run_scenarios(
        [
            HarnessScenario(
                "threshold saved with audit trail", ScenarioKind.HAPPY_PATH, happy_path
            ),
            HarnessScenario(
                "invalid threshold values rejected", ScenarioKind.FAILURE_PATH, failure_path
            ),
            HarnessScenario(
                "edit during in-flight evaluation rejected",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
