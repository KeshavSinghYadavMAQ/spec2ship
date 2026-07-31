"""Contract test: POST /v1/inventory/events, incl. 429 rate-limit response (T029, US1,
FR-012, FR-022, FR-024)."""

from __future__ import annotations

import uuid

from src.domain.alerting.policy_models import ProductLocationPolicy
from src.infrastructure.config import get_settings


def test_ingest_event_accepted(client):
    response = client.post(
        "/v1/inventory/events",
        json={
            "source_system": "pos-1",
            "event_type": "sale",
            "sku_id": "SKU-2",
            "location_id": "STORE-1",
            "shelf_delta": 3,
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert body["processing_state"] == "applied"


def test_ingest_event_validation_error(client):
    response = client.post(
        "/v1/inventory/events",
        json={
            "source_system": "pos-1",
            "event_type": "not-a-real-type",
            "sku_id": "SKU-2",
            "location_id": "STORE-1",
        },
    )
    assert response.status_code == 422
    assert response.json()["title"] == "Validation Error"


def test_ingest_event_rate_limited(client):
    get_settings.cache_clear()
    settings = get_settings()
    limit = settings.rate_limit_requests_per_window

    last_response = None
    for _ in range(limit + 1):
        last_response = client.post(
            "/v1/inventory/events",
            headers={"X-Source-System": "pos-flood"},
            json={
                "source_system": "pos-flood",
                "event_type": "stock_update",
                "sku_id": "SKU-3",
                "location_id": "STORE-1",
                "shelf_delta": 1,
            },
        )

    assert last_response is not None
    assert last_response.status_code == 429
    assert "Retry-After" in last_response.headers
    assert last_response.json()["status"] == 429


def test_ingest_event_breaching_policy_raises_alert(client, db_session):
    """Regression test (US2, FR-002): ingesting an event that breaches an active
    ProductLocationPolicy's threshold must raise a StockAlert via the live API, not just
    when the evaluator is called directly in isolation."""
    policy = ProductLocationPolicy(
        id=str(uuid.uuid4()),
        sku_id="SKU-ALERT",
        location_id="STORE-ALERT",
        low_stock_threshold=10,
        out_of_stock_threshold=0,
        reorder_point=15,
        min_qty=5,
        max_qty=50,
        safety_stock=5,
        is_active=True,
    )
    db_session.add(policy)
    db_session.flush()

    response = client.post(
        "/v1/inventory/events",
        json={
            "source_system": "pos-1",
            "event_type": "stock_update",
            "sku_id": "SKU-ALERT",
            "location_id": "STORE-ALERT",
            "shelf_delta": 5,
        },
    )
    assert response.status_code == 202

    alerts_response = client.get("/v1/alerts")
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()
    assert any(
        a["sku_id"] == "SKU-ALERT" and a["location_id"] == "STORE-ALERT" and a["status"] == "Open"
        for a in alerts
    )
