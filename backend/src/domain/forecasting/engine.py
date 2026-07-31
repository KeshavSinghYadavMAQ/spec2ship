"""Trend/seasonality/promotion-aware forecasting engine with error indicators (T062,
US4, FR-006, FR-007).

Deterministic projection math lives here; `ForecastExplainerAgent` (T106) only narrates
the factors this engine computes (Constitution II/V).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from src.agents.forecast_explainer import ForecastExplainerAgent
from src.domain.forecasting.models import (
    DemandForecast,
    DemandForecastRepository,
    ForecastErrorIndicator,
)

MIN_HISTORY_POINTS = 3
_TREND_CLAMP_MIN = 0.5
_TREND_CLAMP_MAX = 2.0
_CV_HIGH_THRESHOLD = 0.5
_CV_MEDIUM_THRESHOLD = 0.2


@dataclass
class ForecastProjection:
    forecast_quantity: float
    trend_factor: float
    error_indicator: ForecastErrorIndicator
    history_points_used: int
    factors: dict[str, Any]


def _coefficient_of_variation(history: list[float]) -> float:
    if not history:
        return 0.0
    mean = sum(history) / len(history)
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in history) / len(history)
    return float((variance**0.5) / mean)


def compute_forecast_projection(
    history: list[float],
    *,
    seasonality_factor: float = 1.0,
    promotion_factor: float = 1.0,
) -> ForecastProjection:
    """Insufficient history (< MIN_HISTORY_POINTS) never raises — it returns a
    best-effort projection flagged `insufficient_history` so callers can surface the
    data-quality warning rather than failing the request (failure-path edge case)."""
    history_points_used = len(history)

    if history_points_used < MIN_HISTORY_POINTS:
        base_average = sum(history) / history_points_used if history_points_used else 0.0
        forecast_quantity = max(0.0, base_average * seasonality_factor * promotion_factor)
        factors = {
            "history": history,
            "base_average": base_average,
            "trend_factor": 1.0,
            "seasonality_factor": seasonality_factor,
            "promotion_factor": promotion_factor,
        }
        return ForecastProjection(
            forecast_quantity=forecast_quantity,
            trend_factor=1.0,
            error_indicator=ForecastErrorIndicator.INSUFFICIENT_HISTORY,
            history_points_used=history_points_used,
            factors=factors,
        )

    recent_window = history[-3:]
    base_average = sum(recent_window) / len(recent_window)
    trend_factor = 1.0
    if history[0] > 0:
        trend_factor = max(_TREND_CLAMP_MIN, min(_TREND_CLAMP_MAX, history[-1] / history[0]))

    forecast_quantity = max(
        0.0, base_average * trend_factor * seasonality_factor * promotion_factor
    )

    coefficient_of_variation = _coefficient_of_variation(history)
    if coefficient_of_variation > _CV_HIGH_THRESHOLD:
        error_indicator = ForecastErrorIndicator.HIGH
    elif coefficient_of_variation > _CV_MEDIUM_THRESHOLD:
        error_indicator = ForecastErrorIndicator.MEDIUM
    else:
        error_indicator = ForecastErrorIndicator.LOW

    factors = {
        "history": history,
        "base_average": base_average,
        "trend_factor": trend_factor,
        "seasonality_factor": seasonality_factor,
        "promotion_factor": promotion_factor,
        "coefficient_of_variation": coefficient_of_variation,
    }
    return ForecastProjection(
        forecast_quantity=forecast_quantity,
        trend_factor=trend_factor,
        error_indicator=error_indicator,
        history_points_used=history_points_used,
        factors=factors,
    )


class ForecastingEngine:
    def __init__(
        self, repo: DemandForecastRepository, explainer: ForecastExplainerAgent | None = None
    ) -> None:
        self._repo = repo
        self._explainer = explainer or ForecastExplainerAgent()

    def generate_forecast(
        self,
        *,
        sku_id: str,
        location_id: str,
        history: list[float],
        period_start: date,
        period_end: date,
        seasonality_factor: float = 1.0,
        promotion_factor: float = 1.0,
    ) -> DemandForecast:
        projection = compute_forecast_projection(
            history, seasonality_factor=seasonality_factor, promotion_factor=promotion_factor
        )
        narration = self._explainer.explain(
            {
                **projection.factors,
                "forecast_quantity": projection.forecast_quantity,
                "sku_id": sku_id,
                "location_id": location_id,
                "history_points_used": projection.history_points_used,
            }
        )
        return self._repo.create(
            sku_id=sku_id,
            location_id=location_id,
            period_start=period_start,
            period_end=period_end,
            forecast_quantity=projection.forecast_quantity,
            trend_factor=projection.trend_factor,
            seasonality_factor=seasonality_factor,
            promotion_factor=promotion_factor,
            history_points_used=projection.history_points_used,
            error_indicator=projection.error_indicator,
            factors=projection.factors,
            narration=narration,
        )
