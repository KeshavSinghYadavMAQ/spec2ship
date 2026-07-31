"""Harness scenario: scope changes apply on next request (T035, US2)."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.admin.rbac import UserRoleAssignment
from src.domain.inventory.models import InventoryPosition

_HEADERS = {"X-User-Id": "mgr-a", "X-User-Role": "store_manager"}


def test_scope_change_reflects_on_next_request(client, db_session):
    db_session.add(
        UserRoleAssignment(
            id="ura-refresh",
            user_id="mgr-a",
            role="store_manager",
            location_scope={"location_ids": ["STORE-A"]},
        )
    )
    now = datetime.now(UTC)
    db_session.add_all(
        [
            InventoryPosition(
                id="inv-a",
                sku_id="SKU-1",
                location_id="STORE-A",
                shelf_quantity=4,
                backroom_quantity=0,
                last_event_id=None,
                freshness_at=now,
                data_freshness_warning=False,
            ),
            InventoryPosition(
                id="inv-b",
                sku_id="SKU-2",
                location_id="STORE-B",
                shelf_quantity=7,
                backroom_quantity=1,
                last_event_id=None,
                freshness_at=now,
                data_freshness_warning=False,
            ),
        ]
    )
    db_session.flush()

    first = client.get("/v1/inventory/positions", headers=_HEADERS)
    assert first.status_code == 200
    assert {row["location_id"] for row in first.json()} == {"STORE-A"}

    assignment = db_session.query(UserRoleAssignment).filter_by(id="ura-refresh").one()
    assignment.location_scope = {"location_ids": ["STORE-B"]}
    db_session.flush()

    second = client.get("/v1/inventory/positions", headers=_HEADERS)
    assert second.status_code == 200
    assert {row["location_id"] for row in second.json()} == {"STORE-B"}
