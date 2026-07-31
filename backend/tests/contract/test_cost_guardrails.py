"""Contract test: GET /v1/admin/cost-guardrails (T104, SC-008)."""

from __future__ import annotations


def test_get_cost_guardrails_shape(client):
    response = client.get("/v1/admin/cost-guardrails")
    assert response.status_code == 200
    body = response.json()
    assert body["ingested_event_count"] >= 0
    assert body["monthly_cost_ceiling_usd"] == 15_000.0
    assert body["per_event_cost_assumption_usd"] == 0.00005
    assert body["estimated_ingestion_cost_usd"] == round(
        body["ingested_event_count"] * body["per_event_cost_assumption_usd"], 4
    )
    assert body["within_ceiling"] is True


def test_cost_guardrails_reflects_ingested_events(client):
    before = client.get("/v1/admin/cost-guardrails").json()["ingested_event_count"]

    payload = {
        "source_system": "pos-1",
        "event_type": "stock_update",
        "sku_id": "SKU-1",
        "location_id": "STORE-1",
        "shelf_delta": 1,
    }
    client.post("/v1/inventory/events", json=payload)

    after = client.get("/v1/admin/cost-guardrails").json()["ingested_event_count"]
    assert after == before + 1
