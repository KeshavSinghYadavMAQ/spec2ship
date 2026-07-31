"""Alert routing/notification dispatch (T045, US2, FR-003).

Resolves a delivery channel for a new alert and dispatches a notification. Channel
resolution is a simple severity-based mapping for v1; production would extend this to
per-role/per-location channel configuration. Dispatch failures are logged and surfaced
via the `dispatch_failed` flag rather than raising, so alert creation itself never fails
because a notification channel is temporarily unavailable (harness failure-path case).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.alerting.models import Severity
from src.infrastructure.observability import get_logger, metrics

logger = get_logger(__name__)

_SEVERITY_CHANNELS = {
    Severity.LOW_STOCK: "email",
    Severity.OUT_OF_STOCK: "sms",
}


@dataclass
class RoutingResult:
    channel: str
    dispatched: bool


def resolve_channel(severity: Severity) -> str:
    return _SEVERITY_CHANNELS.get(severity, "email")


def dispatch_notification(
    *, sku_id: str, location_id: str, severity: Severity, channel: str
) -> RoutingResult:
    try:
        # Placeholder for a real notification integration (email/SMS/webhook provider).
        # Kept intentionally simple; failures here must not block alert persistence.
        logger.info(
            "Alert dispatched",
            extra={
                "context": {
                    "sku_id": sku_id,
                    "location_id": location_id,
                    "severity": severity.value,
                    "channel": channel,
                }
            },
        )
        metrics.increment("alert.dispatched")
        return RoutingResult(channel=channel, dispatched=True)
    except Exception:
        logger.exception("Alert dispatch failed", extra={"context": {"channel": channel}})
        metrics.increment("alert.dispatch_failed")
        return RoutingResult(channel=channel, dispatched=False)
