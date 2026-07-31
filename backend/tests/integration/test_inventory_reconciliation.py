"""Integration test: shelf/backroom reconciliation journey (T030, US1, FR-001)."""

from __future__ import annotations


def test_shelf_and_backroom_reconcile_to_total(client):
    client.post(
        "/v1/inventory/events",
        json={
            "source_system": "wms-1",
            "event_type": "stock_update",
            "sku_id": "SKU-10",
            "location_id": "STORE-9",
            "shelf_delta": 20,
            "backroom_delta": 30,
        },
    )

    response = client.get("/v1/inventory/positions", params={"sku_id": "SKU-10", "location_id": "STORE-9"})
    position = response.json()[0]
    assert position["shelf_quantity"] == 20
    assert position["backroom_quantity"] == 30
    assert position["reconciled_total"] == 50


def test_returns_increase_stock_without_duplicate_counting(client):
    client.post(
        "/v1/inventory/events",
        json={
            "source_system": "pos-1",
            "event_type": "sale",
            "sku_id": "SKU-11",
            "location_id": "STORE-1",
            "shelf_delta": 5,
        },
    )
    client.post(
        "/v1/inventory/events",
        json={
            "source_system": "pos-1",
            "event_type": "return",
            "sku_id": "SKU-11",
            "location_id": "STORE-1",
            "shelf_delta": 2,
        },
    )

    response = client.get("/v1/inventory/positions", params={"sku_id": "SKU-11"})
    position = response.json()[0]
    # Started at 0, -5 from sale clamped to 0, +2 from return -> 2
    assert position["shelf_quantity"] == 2
