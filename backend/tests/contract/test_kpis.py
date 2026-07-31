"""Contract test: GET /v1/analytics/kpis (T088, US6, FR-010, FR-011)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.alerting.models import AlertStatus, StockAlert
from src.domain.inventory.models import InventoryPosition
from src.domain.transfer_balance.priority_models import StorePriorityProfile


def test_kpis_empty_dataset_returns_full_fill_rate(client):
    response = client.get("/v1/analytics/kpis")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["fill_rate"] == 1.0
    assert body[0]["total_positions"] == 0


def test_kpis_reflects_open_alerts_and_region_filter(client, db_session):
    db_session.add(
        StorePriorityProfile(
            id="p1",
            store_id="STORE-1",
            region="north",
            recent_consumption_rate=5.0,
            region_weight=0.5,
            consumption_weight=0.5,
        )
    )
    db_session.add(
        InventoryPosition(
            id=str(uuid.uuid4()),
            sku_id="SKU-1",
            location_id="STORE-1",
            shelf_quantity=1,
            backroom_quantity=0,
            freshness_at=datetime.now(UTC),
        )
    )
    db_session.add(
        StockAlert(
            id=str(uuid.uuid4()),
            sku_id="SKU-1",
            location_id="STORE-1",
            severity="low_stock",
            status=AlertStatus.OPEN.value,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    response = client.get("/v1/analytics/kpis", params={"region": "north"})
    assert response.status_code == 200
    body = response.json()[0]
    assert body["total_positions"] == 1
    assert body["open_alert_count"] == 1
    assert body["fill_rate"] == 0.0
