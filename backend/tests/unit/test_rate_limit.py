"""Unit tests for `RateLimitMiddleware` (T099, FR-024).

Overrides the requests-per-window setting to a small value so the 429 boundary can be
exercised deterministically without waiting out a real window.
"""

from __future__ import annotations

# Importing the app at module (collection) time ensures every domain model is registered on
# `Base.metadata` before the `db_session` fixture's `create_all()` runs, matching the ordering
# the full suite gets "for free" from other test modules importing routers during collection.
import src.api.main  # noqa: F401
from src.infrastructure.config import get_settings


def test_ingestion_requests_within_window_succeed(client, monkeypatch):
    monkeypatch.setenv("APP_RATE_LIMIT_REQUESTS_PER_WINDOW", "2")
    get_settings.cache_clear()
    try:
        payload = {
            "source_system": "pos-1",
            "event_type": "stock_update",
            "sku_id": "SKU-1",
            "location_id": "STORE-1",
            "shelf_delta": 1,
        }
        headers = {"X-Source-System": "pos-1"}

        first = client.post("/v1/inventory/events", json=payload, headers=headers)
        second = client.post("/v1/inventory/events", json=payload, headers=headers)
        assert first.status_code == 202
        assert second.status_code == 202
    finally:
        get_settings.cache_clear()


def test_ingestion_over_limit_returns_429_with_retry_after(client, monkeypatch):
    monkeypatch.setenv("APP_RATE_LIMIT_REQUESTS_PER_WINDOW", "1")
    get_settings.cache_clear()
    try:
        payload = {
            "source_system": "pos-2",
            "event_type": "stock_update",
            "sku_id": "SKU-1",
            "location_id": "STORE-1",
            "shelf_delta": 1,
        }
        headers = {"X-Source-System": "pos-2"}

        first = client.post("/v1/inventory/events", json=payload, headers=headers)
        second = client.post("/v1/inventory/events", json=payload, headers=headers)

        assert first.status_code == 202
        assert second.status_code == 429
        assert "Retry-After" in second.headers
        assert second.json()["title"] == "Too Many Requests"
    finally:
        get_settings.cache_clear()


def test_rate_limit_is_scoped_per_source_system(client, monkeypatch):
    monkeypatch.setenv("APP_RATE_LIMIT_REQUESTS_PER_WINDOW", "1")
    get_settings.cache_clear()
    try:
        headers_a = {"X-Source-System": "pos-a"}
        headers_b = {"X-Source-System": "pos-b"}
        payload = {
            "source_system": "pos-a",
            "event_type": "stock_update",
            "sku_id": "SKU-1",
            "location_id": "STORE-1",
            "shelf_delta": 1,
        }

        a_first = client.post("/v1/inventory/events", json=payload, headers=headers_a)
        b_first = client.post(
            "/v1/inventory/events", json={**payload, "source_system": "pos-b"}, headers=headers_b
        )

        assert a_first.status_code == 202
        assert b_first.status_code == 202, "a different source system must have its own budget"
    finally:
        get_settings.cache_clear()
