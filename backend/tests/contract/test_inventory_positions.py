"""Contract test: GET /v1/inventory/positions (T028, US1, FR-001)."""

from __future__ import annotations


def test_list_positions_empty(client):
    response = client.get("/v1/inventory/positions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_positions_after_event(client):
    client.post(
        "/v1/inventory/events",
        json={
            "source_system": "pos-1",
            "event_type": "stock_update",
            "sku_id": "SKU-1",
            "location_id": "STORE-1",
            "shelf_delta": 10,
            "backroom_delta": 5,
        },
    )

    response = client.get("/v1/inventory/positions", params={"sku_id": "SKU-1"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["sku_id"] == "SKU-1"
    assert body[0]["shelf_quantity"] == 10
    assert body[0]["backroom_quantity"] == 5
    assert body[0]["reconciled_total"] == 15
