"""Contract test: GET/POST /v1/admin/product-location-policies (T074, US7, FR-016,
FR-017, FR-018)."""

from __future__ import annotations

from src.domain.alerting.policy_models import ProductLocationPolicy

_ADMIN_HEADERS = {"X-User-Id": "admin-1", "X-User-Role": "admin"}
_VALID_BODY = {
    "sku_id": "SKU-1",
    "location_id": "STORE-1",
    "low_stock_threshold": 10,
    "out_of_stock_threshold": 2,
    "reorder_point": 20,
    "min_qty": 10,
    "max_qty": 50,
    "safety_stock": 5,
}


def test_list_policies_empty(client):
    response = client.get("/v1/admin/product-location-policies")
    assert response.status_code == 200
    assert response.json() == []


def test_upsert_policy_requires_admin_role(client):
    response = client.post("/v1/admin/product-location-policies", json=_VALID_BODY)
    assert response.status_code == 401  # no X-User-Id/X-User-Role headers supplied


def test_upsert_policy_rejects_non_admin_role(client):
    response = client.post(
        "/v1/admin/product-location-policies",
        json=_VALID_BODY,
        headers={"X-User-Id": "sm-1", "X-User-Role": "store_manager"},
    )
    assert response.status_code == 403


def test_upsert_policy_success(client):
    response = client.post(
        "/v1/admin/product-location-policies", json=_VALID_BODY, headers=_ADMIN_HEADERS
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sku_id"] == "SKU-1"
    assert body["updated_by"] == "admin-1"


def test_upsert_policy_validation_error_returns_422(client):
    invalid_body = {**_VALID_BODY, "out_of_stock_threshold": 999}
    response = client.post(
        "/v1/admin/product-location-policies", json=invalid_body, headers=_ADMIN_HEADERS
    )
    assert response.status_code == 422


def test_upsert_policy_locked_returns_409(client, db_session):
    existing = ProductLocationPolicy(
        id="existing-1",
        sku_id="SKU-2",
        location_id="STORE-1",
        low_stock_threshold=10,
        out_of_stock_threshold=0,
        reorder_point=20,
        min_qty=10,
        max_qty=50,
        safety_stock=5,
        edit_lock_held=True,
    )
    db_session.add(existing)
    db_session.commit()

    response = client.post(
        "/v1/admin/product-location-policies",
        json={**_VALID_BODY, "sku_id": "SKU-2"},
        headers=_ADMIN_HEADERS,
    )
    assert response.status_code == 409
