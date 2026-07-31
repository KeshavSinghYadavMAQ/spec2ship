"""RLS contract tests for inventory list filtering and record-level 404 (T033, US2)."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.admin.rbac import UserRoleAssignment
from src.domain.inventory.models import InventoryPosition


def _seed_role(db_session) -> None:
    db_session.add(
        UserRoleAssignment(
            id="ura-1",
            user_id="mgr-a",
            role="store_manager",
            location_scope={"location_ids": ["STORE-A"]},
        )
    )


def _seed_positions(db_session) -> tuple[str, str]:
    now = datetime.now(UTC)
    a = InventoryPosition(
        id="pos-a",
        sku_id="SKU-1",
        location_id="STORE-A",
        shelf_quantity=5,
        backroom_quantity=2,
        last_event_id=None,
        freshness_at=now,
        data_freshness_warning=False,
    )
    b = InventoryPosition(
        id="pos-b",
        sku_id="SKU-2",
        location_id="STORE-B",
        shelf_quantity=6,
        backroom_quantity=1,
        last_event_id=None,
        freshness_at=now,
        data_freshness_warning=False,
    )
    db_session.add_all([a, b])
    db_session.flush()
    return a.id, b.id


def test_inventory_list_is_filtered_to_scope(client, db_session):
    _seed_role(db_session)
    _seed_positions(db_session)

    response = client.get(
        "/v1/inventory/positions",
        headers={"X-User-Id": "mgr-a", "X-User-Role": "store_manager"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["location_id"] == "STORE-A"


def test_inventory_record_out_of_scope_returns_404(client, db_session):
    _seed_role(db_session)
    _, out_of_scope_id = _seed_positions(db_session)

    response = client.get(
        f"/v1/inventory/positions/{out_of_scope_id}",
        headers={"X-User-Id": "mgr-a", "X-User-Role": "store_manager"},
    )

    assert response.status_code == 404
