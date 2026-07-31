"""Contract test: GET /v1/alerts and POST /v1/alerts/{alertId}/transition (T039, US2,
FR-002, FR-003)."""

from __future__ import annotations

from src.domain.alerting.models import Severity, StockAlertRepository


def test_list_alerts_empty(client):
    response = client.get("/v1/alerts")
    assert response.status_code == 200
    assert response.json() == []


def test_transition_alert_success(client, db_session):
    repo = StockAlertRepository(db_session)
    alert = repo.create(
        sku_id="SKU-1", location_id="STORE-1", severity=Severity.LOW_STOCK, routing_channel="email"
    )
    db_session.commit()

    response = client.post(f"/v1/alerts/{alert.id}/transition", json={"status": "Acknowledged"})
    assert response.status_code == 200
    assert response.json()["status"] == "Acknowledged"


def test_transition_alert_invalid_returns_409(client, db_session):
    repo = StockAlertRepository(db_session)
    alert = repo.create(
        sku_id="SKU-2", location_id="STORE-1", severity=Severity.OUT_OF_STOCK, routing_channel="sms"
    )
    db_session.commit()

    # Open -> Resolved is not a valid direct transition.
    response = client.post(f"/v1/alerts/{alert.id}/transition", json={"status": "Resolved"})
    assert response.status_code == 409
