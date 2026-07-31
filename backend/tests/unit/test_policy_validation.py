"""Unit tests for `PolicyService`/`_validate` threshold edge logic (T099, US7, FR-016,
FR-017)."""

from __future__ import annotations

import pytest
from src.domain.alerting.policy_service import PolicyService, PolicyValidationError


@pytest.mark.parametrize(
    "overrides",
    [
        {"low_stock_threshold": -1},
        {"out_of_stock_threshold": -1},
        {"reorder_point": -1},
        {"min_qty": -1},
        {"max_qty": -1},
        {"safety_stock": -1},
    ],
)
def test_negative_values_are_rejected(db_session, overrides):
    service = PolicyService(db_session)
    base = dict(
        sku_id="SKU-U1",
        location_id="STORE-U1",
        low_stock_threshold=10,
        out_of_stock_threshold=2,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
        updated_by="admin-1",
    )
    base.update(overrides)
    with pytest.raises(PolicyValidationError):
        service.upsert_policy(**base)


def test_out_of_stock_threshold_equal_to_low_stock_threshold_is_allowed(db_session):
    service = PolicyService(db_session)
    policy = service.upsert_policy(
        sku_id="SKU-U2",
        location_id="STORE-U1",
        low_stock_threshold=10,
        out_of_stock_threshold=10,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
        updated_by="admin-1",
    )
    assert policy.out_of_stock_threshold == 10


def test_min_qty_equal_to_max_qty_is_allowed(db_session):
    service = PolicyService(db_session)
    policy = service.upsert_policy(
        sku_id="SKU-U3",
        location_id="STORE-U1",
        low_stock_threshold=10,
        out_of_stock_threshold=2,
        reorder_point=20,
        min_qty=20,
        max_qty=20,
        safety_stock=5,
        updated_by="admin-1",
    )
    assert policy.min_qty == policy.max_qty == 20


def test_multiple_validation_errors_are_all_reported(db_session):
    service = PolicyService(db_session)
    with pytest.raises(PolicyValidationError) as excinfo:
        service.upsert_policy(
            sku_id="SKU-U4",
            location_id="STORE-U1",
            low_stock_threshold=10,
            out_of_stock_threshold=20,
            reorder_point=20,
            min_qty=50,
            max_qty=10,
            safety_stock=5,
            updated_by="admin-1",
        )
    assert len(excinfo.value.errors) == 2
