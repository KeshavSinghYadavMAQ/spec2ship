"""Contract test for `DELETE /v1/admin/sample-data` (T015, US1, FR-011).

Verifies the admin-role gate and that a clear run removes previously seeded records.
"""

from __future__ import annotations

_ADMIN_HEADERS = {"X-User-Id": "admin-1", "X-User-Role": "admin"}
_NON_ADMIN_HEADERS = {"X-User-Id": "sm-1", "X-User-Role": "store_manager"}


def test_clear_rejects_non_admin(client):
    response = client.delete("/v1/admin/sample-data", headers=_NON_ADMIN_HEADERS)
    assert response.status_code == 403


def test_clear_removes_seeded_data(client):
    seed_response = client.post(
        "/v1/admin/sample-data/seed",
        headers=_ADMIN_HEADERS,
        params={"store_count": 2, "catalog_size": 6, "assortment_size": 3},
    )
    assert seed_response.status_code == 202
    seeded_counts = seed_response.json()["counts_by_entity_type"]
    assert sum(seeded_counts.values()) > 0

    clear_response = client.delete("/v1/admin/sample-data", headers=_ADMIN_HEADERS)
    assert clear_response.status_code == 200
    removed_counts = clear_response.json()["removed_counts_by_entity_type"]
    assert removed_counts == seeded_counts

    status_response = client.get("/v1/admin/sample-data/status", headers=_ADMIN_HEADERS)
    assert status_response.status_code == 404
