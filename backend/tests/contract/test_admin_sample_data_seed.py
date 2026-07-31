"""Contract tests for `POST /v1/admin/sample-data/seed` (T013, US1, FR-004, FR-011).

Verifies the admin-role + non-production-environment gate (403 for both violations) and
the happy-path 202 response shape.
"""

from __future__ import annotations

from src.infrastructure.config import get_settings

_ADMIN_HEADERS = {"X-User-Id": "admin-1", "X-User-Role": "admin"}
_NON_ADMIN_HEADERS = {"X-User-Id": "sm-1", "X-User-Role": "store_manager"}


def _override_environment(environment: str) -> None:
    from src.api.main import app

    base = get_settings()
    app.dependency_overrides[get_settings] = lambda: base.model_copy(
        update={"environment": environment}
    )


def _clear_environment_override() -> None:
    from src.api.main import app

    app.dependency_overrides.pop(get_settings, None)


def test_seed_rejects_non_admin(client):
    response = client.post("/v1/admin/sample-data/seed", headers=_NON_ADMIN_HEADERS)
    assert response.status_code == 403


def test_seed_rejects_production_environment(client):
    _override_environment("production")
    try:
        response = client.post("/v1/admin/sample-data/seed", headers=_ADMIN_HEADERS)
        assert response.status_code == 403
    finally:
        _clear_environment_override()


def test_seed_returns_run_summary(client):
    response = client.post(
        "/v1/admin/sample-data/seed",
        headers=_ADMIN_HEADERS,
        params={"store_count": 2, "catalog_size": 6, "assortment_size": 3},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] in {"in_progress", "completed", "partially_completed"}
    assert "seed_batch_id" in body
    assert isinstance(body["counts_by_entity_type"], dict)
    assert "started_at" in body
