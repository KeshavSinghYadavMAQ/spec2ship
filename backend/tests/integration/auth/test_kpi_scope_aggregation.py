"""US5 KPI aggregation scope integration tests."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.admin.rbac import UserRoleAssignment
from src.domain.alerting.models import StockAlert
from src.domain.inventory.models import InventoryPosition


def test_kpis_are_filtered_by_user_scope(client, db_session):
    db_session.add(
        UserRoleAssignment(
            id="ura-kpi",
            user_id="mgr-a",
            role="store_manager",
            location_scope={"location_ids": ["STORE-A"]},
        )
    )
    now = datetime.now(UTC)
    db_session.add_all(
        [
            InventoryPosition(
                id="kpi-pos-a",
                sku_id="SKU-1",
                location_id="STORE-A",
                shelf_quantity=5,
                backroom_quantity=2,
                last_event_id=None,
                freshness_at=now,
                data_freshness_warning=False,
            ),
            InventoryPosition(
                id="kpi-pos-b",
                sku_id="SKU-2",
                location_id="STORE-B",
                shelf_quantity=5,
                backroom_quantity=2,
                last_event_id=None,
                freshness_at=now,
                data_freshness_warning=False,
            ),
            StockAlert(
                id="kpi-alert-a",
                sku_id="SKU-2",
                location_id="STORE-B",
                severity="out_of_stock",
                status="Open",
                owner_user_id=None,
                routing_channel=None,
                suppressed_until=None,
                created_at=now,
                updated_at=now,
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        "/v1/analytics/kpis",
        headers={"X-User-Id": "mgr-a", "X-User-Role": "store_manager"},
    )

    assert response.status_code == 200
    body = response.json()[0]
    assert body["total_positions"] == 1
    assert body["open_alert_count"] == 0
