"""Harness scenario for User Story 4 (T060): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

from datetime import date

from src.domain.forecasting.engine import ForecastingEngine
from src.domain.forecasting.models import DemandForecastRepository, ForecastErrorIndicator

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def test_forecasting_harness_scenarios(db_session):
    repo = DemandForecastRepository(db_session)
    engine = ForecastingEngine(repo)

    def happy_path() -> None:
        forecast = engine.generate_forecast(
            sku_id="SKU-F1",
            location_id="STORE-F1",
            history=[20.0, 22.0, 24.0, 26.0, 28.0],
            period_start=date(2025, 2, 1),
            period_end=date(2025, 2, 7),
        )
        assert forecast.forecast_quantity > 0
        assert forecast.error_indicator != ForecastErrorIndicator.INSUFFICIENT_HISTORY.value
        assert forecast.narration

    def failure_path() -> None:
        # Fewer than MIN_HISTORY_POINTS data points must not raise; it must flag
        # insufficient_history instead of failing the whole request.
        forecast = engine.generate_forecast(
            sku_id="SKU-F2",
            location_id="STORE-F1",
            history=[15.0],
            period_start=date(2025, 2, 1),
            period_end=date(2025, 2, 7),
        )
        assert forecast.error_indicator == ForecastErrorIndicator.INSUFFICIENT_HISTORY.value
        assert forecast.forecast_quantity >= 0

    def data_quality_edge_case() -> None:
        # Highly volatile history should be flagged high error/low confidence rather
        # than silently producing an overconfident point estimate.
        forecast = engine.generate_forecast(
            sku_id="SKU-F3",
            location_id="STORE-F1",
            history=[5.0, 50.0, 2.0, 60.0, 1.0],
            period_start=date(2025, 2, 1),
            period_end=date(2025, 2, 7),
        )
        assert forecast.error_indicator == ForecastErrorIndicator.HIGH.value

    run_scenarios(
        [
            HarnessScenario(
                "trend-adjusted forecast produced", ScenarioKind.HAPPY_PATH, happy_path
            ),
            HarnessScenario(
                "insufficient history flagged, not rejected", ScenarioKind.FAILURE_PATH, failure_path
            ),
            HarnessScenario(
                "volatile history flagged high error",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
