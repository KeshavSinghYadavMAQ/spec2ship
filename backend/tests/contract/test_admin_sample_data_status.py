"""Contract test for `GET /v1/admin/sample-data/status` (T014, US1).

Verifies the 404 "never seeded" case and the 200 shape after a seeding run.
"""

from __future__ import annotations

_ADMIN_HEADERS = {"X-User-Id": "admin-1", "X-User-Role": "admin"}


def test_status_404_when_never_seeded(client):
    response = client.get("/v1/admin/sample-data/status", headers=_ADMIN_HEADERS)
    assert response.status_code == 404


def test_status_after_seeding_returns_summary(client):
    seed_response = client.post(
        "/v1/admin/sample-data/seed",
        headers=_ADMIN_HEADERS,
        params={"store_count": 2, "catalog_size": 6, "assortment_size": 3},
    )
    assert seed_response.status_code == 202

    status_response = client.get("/v1/admin/sample-data/status", headers=_ADMIN_HEADERS)
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["seed_batch_id"] == seed_response.json()["seed_batch_id"]
    assert isinstance(body["counts_by_entity_type"], dict)
    assert len(body["counts_by_entity_type"]) > 0
