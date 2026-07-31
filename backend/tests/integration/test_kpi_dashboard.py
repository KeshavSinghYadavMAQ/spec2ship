"""Integration test: KPI aggregation across inventory/alerts/recommendations/forecasts
(T089, US6, FR-010, FR-011)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from src.domain.analytics.service import KPIAggregationService
from src.domain.forecasting.models import DemandForecast, ForecastErrorIndicator
from src.domain.replenishment.models import ReplenishmentRecommendation
from src.domain.transfer_balance.priority_models import StorePriorityProfile


def test_compute_aggregates_recommendation_outcomes_and_forecast_quality(db_session):
    db_session.add(
        StorePriorityProfile(
            id="p1",
            store_id="STORE-1",
            region="north",
            recent_consumption_rate=5.0,
            region_weight=0.5,
            consumption_weight=0.5,
        )
    )
    db_session.add(
        ReplenishmentRecommendation(
            id=str(uuid.uuid4()),
            sku_id="SKU-1",
            location_id="STORE-1",
            recommended_quantity=10,
            recommended_by_date=date.today(),
            policy_snapshot={},
            rationale={"narration": "x", "factors": {}},
            status="accepted",
            created_at=datetime.now(UTC),
        )
    )
    db_session.add(
        DemandForecast(
            id=str(uuid.uuid4()),
            sku_id="SKU-1",
            location_id="STORE-1",
            period_start=date.today(),
            period_end=date.today(),
            forecast_quantity=10.0,
            trend_factor=1.0,
            seasonality_factor=1.0,
            promotion_factor=1.0,
            history_points_used=5,
            error_indicator=ForecastErrorIndicator.LOW.value,
            factors={},
            created_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    service = KPIAggregationService(db_session)
    kpi = service.compute(region="north")

    assert kpi.recommendation_outcomes == {"accepted": 1}
    assert kpi.forecast_quality == {"low": 1}


def test_compute_scopes_by_store_id_directly(db_session):
    service = KPIAggregationService(db_session)
    kpi = service.compute(store_id="STORE-does-not-exist")

    assert kpi.total_positions == 0
    assert kpi.fill_rate == 1.0
    assert kpi.recommendation_outcomes == {}
