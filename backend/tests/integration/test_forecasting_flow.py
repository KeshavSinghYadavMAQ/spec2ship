"""Integration test: forecast generation + explanation journey (T059, US4, FR-006,
FR-007)."""

from __future__ import annotations

from datetime import date

from src.domain.forecasting.engine import ForecastingEngine
from src.domain.forecasting.models import DemandForecastRepository, ForecastErrorIndicator


def test_forecast_generation_includes_trend_and_narration(db_session):
    repo = DemandForecastRepository(db_session)
    engine = ForecastingEngine(repo)

    forecast = engine.generate_forecast(
        sku_id="SKU-1",
        location_id="STORE-1",
        history=[10.0, 12.0, 14.0, 16.0, 20.0],
        period_start=date(2025, 1, 1),
        period_end=date(2025, 1, 7),
    )

    assert forecast.forecast_quantity > 0
    assert forecast.trend_factor > 1.0, "rising history should yield an upward trend factor"
    assert forecast.narration, "explanation must not be empty"
    assert forecast.error_indicator in {
        ForecastErrorIndicator.LOW.value,
        ForecastErrorIndicator.MEDIUM.value,
        ForecastErrorIndicator.HIGH.value,
    }


def test_forecast_with_promotion_and_seasonality_factors(db_session):
    repo = DemandForecastRepository(db_session)
    engine = ForecastingEngine(repo)

    baseline = engine.generate_forecast(
        sku_id="SKU-2",
        location_id="STORE-1",
        history=[10.0, 10.0, 10.0, 10.0],
        period_start=date(2025, 1, 1),
        period_end=date(2025, 1, 7),
    )
    boosted = engine.generate_forecast(
        sku_id="SKU-2",
        location_id="STORE-1",
        history=[10.0, 10.0, 10.0, 10.0],
        period_start=date(2025, 1, 8),
        period_end=date(2025, 1, 14),
        seasonality_factor=1.2,
        promotion_factor=1.5,
    )

    assert boosted.forecast_quantity > baseline.forecast_quantity
