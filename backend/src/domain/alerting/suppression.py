"""Alert deduplication/suppression using Redis TTL windows (T044, US2, FR-003).

Prevents duplicate notifications for repeated breaches of the same SKU-location within
a configurable suppression window (spec.md edge case: "Promotion-driven demand spike
causes simultaneous low stock events across many stores" and Acceptance Scenario 3).
"""

from __future__ import annotations

from src.infrastructure.cache import CacheClient
from src.infrastructure.config import get_settings


def _suppression_key(sku_id: str, location_id: str, severity: str) -> str:
    return f"alert-suppression:{sku_id}:{location_id}:{severity}"


def should_suppress(cache: CacheClient, *, sku_id: str, location_id: str, severity: str) -> bool:
    """Returns True if an alert for this SKU-location-severity was already raised within
    the suppression window (i.e. this breach should NOT create a new alert)."""
    key = _suppression_key(sku_id, location_id, severity)
    return cache.get(key) is not None


def mark_suppressed(
    cache: CacheClient, *, sku_id: str, location_id: str, severity: str, window_seconds: int | None = None
) -> None:
    settings = get_settings()
    key = _suppression_key(sku_id, location_id, severity)
    cache.set(key, "1", ex=window_seconds or settings.alert_suppression_window_seconds)
