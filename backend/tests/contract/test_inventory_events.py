"""Contract test: POST /v1/inventory/events, incl. 429 rate-limit response (T029, US1,
FR-012, FR-022, FR-024)."""

from __future__ import annotations

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
