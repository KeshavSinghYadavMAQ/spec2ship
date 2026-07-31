"""Cost-guardrail tracking hooks (T027, SC-008, Constitution VI).

Tracks estimated per-event ingestion cost against the $0.00005/event assumption and
exposes a snapshot against the $15,000/month pilot infrastructure ceiling (both figures
from research.md's "Cost guardrails" decision). This is an estimation aid for the
analytics/admin dashboard (T104), not a substitute for real Azure Cost Management data.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from src.infrastructure.config import get_settings


@dataclass
class CostSnapshot:
    ingested_event_count: int
    estimated_ingestion_cost_usd: float
    monthly_cost_ceiling_usd: float
    per_event_cost_assumption_usd: float

    @property
    def within_ceiling(self) -> bool:
        return self.estimated_ingestion_cost_usd <= self.monthly_cost_ceiling_usd


class CostGuardrailTracker:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ingested_event_count = 0

    def record_ingested_event(self, count: int = 1) -> None:
        with self._lock:
            self._ingested_event_count += count

    def get_cost_snapshot(self) -> CostSnapshot:
        settings = get_settings()
        with self._lock:
            count = self._ingested_event_count
        return CostSnapshot(
            ingested_event_count=count,
            estimated_ingestion_cost_usd=round(count * settings.cost_per_ingested_event_usd, 4),
            monthly_cost_ceiling_usd=settings.cost_ceiling_monthly_usd,
            per_event_cost_assumption_usd=settings.cost_per_ingested_event_usd,
        )


cost_guardrails = CostGuardrailTracker()
