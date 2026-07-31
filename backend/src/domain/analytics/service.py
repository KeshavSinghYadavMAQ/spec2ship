"""`KPIView` model and aggregation service (T091, US6, FR-010, FR-011).

KPIs are computed on read from existing operational data (no separate KPI table) so
values always reflect current inventory/alert/recommendation/forecast state:

- `fill_rate`: share of SKU/location positions with no open (non-resolved) stock alert.
- `average_alert_age_hours`: how long currently-open alerts have persisted (staleness).
- `recommendation_outcomes`: replenishment recommendation counts by decision status.
- `forecast_quality`: demand forecast counts by error indicator.

`region` filters resolve to a set of `store_id`s via `StorePriorityProfile` (the only
place region↔store mapping is modeled in v1). `category` is accepted for API/contract
compatibility but is a no-op in v1 since no product-category master data is modeled yet.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.domain.alerting.models import AlertStatus, StockAlert
from src.domain.forecasting.models import DemandForecast
from src.domain.inventory.models import InventoryPosition
from src.domain.replenishment.models import ReplenishmentRecommendation
from src.domain.transfer_balance.priority_models import StorePriorityProfile


class KPIView(BaseModel):
    region: str | None
    store_id: str | None
    category: str | None
    date_from: date | None
    date_to: date | None
    total_positions: int
    fill_rate: float
    open_alert_count: int
    average_alert_age_hours: float
    recommendation_outcomes: dict[str, int]
    forecast_quality: dict[str, int]


class KPIAggregationService:
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _age_hours(now: datetime, created_at: datetime) -> float:
        """SQLite drops tzinfo on round-trip, so `created_at` may come back naive even
        though it was always stored as UTC; normalize before subtracting."""
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return (now - created_at).total_seconds() / 3600


    def _resolve_store_ids(self, *, region: str | None, store_id: str | None) -> list[str] | None:
        if store_id:
            return [store_id]
        if region:
            rows = (
                self._session.query(StorePriorityProfile.store_id).filter_by(region=region).all()
            )
            return [row[0] for row in rows]
        return None

    def compute(
        self,
        *,
        region: str | None = None,
        store_id: str | None = None,
        category: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> KPIView:
        store_ids = self._resolve_store_ids(region=region, store_id=store_id)

        position_query = self._session.query(InventoryPosition)
        if store_ids is not None:
            position_query = position_query.filter(InventoryPosition.location_id.in_(store_ids))
        positions = position_query.all()
        total_positions = len(positions)

        alert_query = self._session.query(StockAlert).filter(
            StockAlert.status != AlertStatus.RESOLVED.value
        )
        if store_ids is not None:
            alert_query = alert_query.filter(StockAlert.location_id.in_(store_ids))
        open_alerts = alert_query.all()
        open_alert_count = len(open_alerts)

        skus_with_open_alerts = {(a.sku_id, a.location_id) for a in open_alerts}
        positions_healthy = sum(
            1 for p in positions if (p.sku_id, p.location_id) not in skus_with_open_alerts
        )
        fill_rate = positions_healthy / total_positions if total_positions else 1.0

        now = datetime.now(UTC)
        average_alert_age_hours = (
            sum(self._age_hours(now, a.created_at) for a in open_alerts) / len(open_alerts)
            if open_alerts
            else 0.0
        )

        recommendation_query = self._session.query(ReplenishmentRecommendation)
        if store_ids is not None:
            recommendation_query = recommendation_query.filter(
                ReplenishmentRecommendation.location_id.in_(store_ids)
            )
        recommendation_outcomes: dict[str, int] = {}
        for recommendation in recommendation_query.all():
            recommendation_outcomes[recommendation.status] = (
                recommendation_outcomes.get(recommendation.status, 0) + 1
            )

        forecast_query = self._session.query(DemandForecast)
        if store_ids is not None:
            forecast_query = forecast_query.filter(DemandForecast.location_id.in_(store_ids))
        forecast_quality: dict[str, int] = {}
        for forecast in forecast_query.all():
            forecast_quality[forecast.error_indicator] = (
                forecast_quality.get(forecast.error_indicator, 0) + 1
            )

        return KPIView(
            region=region,
            store_id=store_id,
            category=category,
            date_from=date_from,
            date_to=date_to,
            total_positions=total_positions,
            fill_rate=fill_rate,
            open_alert_count=open_alert_count,
            average_alert_age_hours=average_alert_age_hours,
            recommendation_outcomes=recommendation_outcomes,
            forecast_quality=forecast_quality,
        )
