"""Contract test: GET /v1/transfers/suggestions and
POST /v1/transfers/suggestions/{id}/status (T066, US5, FR-008, FR-009, FR-020)."""

from __future__ import annotations

from src.domain.admin.audit import AuditLogWriter
from src.domain.transfer_balance.models import FeasibilityStatus, TransferSuggestionRepository


def test_list_transfer_suggestions_empty(client):
    response = client.get("/v1/transfers/suggestions")
    assert response.status_code == 200
    assert response.json() == []


def test_update_transfer_status(client, db_session):
    repo = TransferSuggestionRepository(db_session)
    suggestion = repo.create(
        sku_id="SKU-1",
        source_location_id="STORE-1",
        destination_location_id="STORE-2",
        suggested_quantity=10,
        feasibility_status=FeasibilityStatus.FEASIBLE,
        feasibility_reason="Surplus available at source without breaching source minimum",
        priority_rank=1,
        factors={},
    )
    db_session.commit()

    response = client.post(
        f"/v1/transfers/suggestions/{suggestion.id}/status",
        json={"status": "accepted"},
        headers={"X-User-Id": "operator-2", "X-User-Role": "regional_manager"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_update_transfer_status_requires_authentication(client, db_session):
    repo = TransferSuggestionRepository(db_session)
    suggestion = repo.create(
        sku_id="SKU-1B",
        source_location_id="STORE-1",
        destination_location_id="STORE-2",
        suggested_quantity=10,
        feasibility_status=FeasibilityStatus.FEASIBLE,
        feasibility_reason="Surplus available at source without breaching source minimum",
        priority_rank=1,
        factors={},
    )
    db_session.commit()

    response = client.post(
        f"/v1/transfers/suggestions/{suggestion.id}/status", json={"status": "accepted"}
    )
    assert response.status_code == 401


def test_update_transfer_status_not_found(client):
    response = client.post(
        "/v1/transfers/suggestions/does-not-exist/status",
        json={"status": "accepted"},
        headers={"X-User-Id": "operator-2", "X-User-Role": "regional_manager"},
    )
    assert response.status_code == 404


def test_update_transfer_status_writes_audit_trail_entry(client, db_session):
    repo = TransferSuggestionRepository(db_session)
    suggestion = repo.create(
        sku_id="SKU-AUDIT",
        source_location_id="STORE-1",
        destination_location_id="STORE-2",
        suggested_quantity=10,
        feasibility_status=FeasibilityStatus.FEASIBLE,
        feasibility_reason="Surplus available at source without breaching source minimum",
        priority_rank=1,
        factors={},
    )
    db_session.commit()

    response = client.post(
        f"/v1/transfers/suggestions/{suggestion.id}/status",
        json={"status": "accepted"},
        headers={"X-User-Id": "operator-2", "X-User-Role": "regional_manager"},
    )
    assert response.status_code == 200

    entries = AuditLogWriter(db_session).list_entries(
        entity_type="transfer_suggestion", entity_id=suggestion.id
    )
    assert len(entries) == 1
    assert entries[0].actor_user_id == "operator-2"
    assert entries[0].after["status"] == "accepted"
