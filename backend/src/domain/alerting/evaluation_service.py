"""Threshold evaluation service (T043, US2, FR-002).

Reads `ProductLocationPolicy` + `InventoryPosition` to decide whether a low-stock or
out-of-stock alert should be raised, applying suppression (FR-003) before persisting a
new `StockAlert`.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.alerting.models import Severity, StockAlert, StockAlertRepository
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.alerting.routing import dispatch_notification, resolve_channel
from src.domain.alerting.suppression import mark_suppressed, should_suppress
from src.domain.inventory.models import InventoryPosition
from src.infrastructure.cache import CacheClient


def _determine_severity(position: InventoryPosition, policy: ProductLocationPolicy) -> Severity | None:
    if position.reconciled_total <= policy.out_of_stock_threshold:
        return Severity.OUT_OF_STOCK
    if position.reconciled_total <= policy.low_stock_threshold:
        return Severity.LOW_STOCK
    return None


class ThresholdEvaluationService:
    def __init__(self, session: Session, cache: CacheClient) -> None:
        self._session = session
        self._cache = cache
        self._alerts = StockAlertRepository(session)

    def evaluate(
        self, position: InventoryPosition, policy: ProductLocationPolicy
    ) -> StockAlert | None:
        severity = _determine_severity(position, policy)
        if severity is None:
            return None

        if should_suppress(
            self._cache, sku_id=position.sku_id, location_id=position.location_id, severity=severity.value
        ):
            return None

        existing = self._alerts.find_active_for_sku_location(position.sku_id, position.location_id)
        if existing is not None and existing.severity == severity.value:
            return None

        channel = resolve_channel(severity)
        alert = self._alerts.create(
            sku_id=position.sku_id,
            location_id=position.location_id,
            severity=severity,
            routing_channel=channel,
        )
        dispatch_notification(
            sku_id=position.sku_id, location_id=position.location_id, severity=severity, channel=channel
        )
        mark_suppressed(
            self._cache, sku_id=position.sku_id, location_id=position.location_id, severity=severity.value
        )
        return alert
