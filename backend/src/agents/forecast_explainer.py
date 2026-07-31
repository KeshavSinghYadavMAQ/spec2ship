"""MAF/Copilot SDK forecast-narration agent wrapper (T106, US4, per research.md).

Explanation only — never alters the trend/seasonality/promotion projection computed by
`engine.py` (Constitution II/V).
"""

from __future__ import annotations

from typing import Any

from src.agents.base import DeterministicFallbackExplainer, ExplanationAgent, try_load_maf_agent

_INSTRUCTIONS = (
    "You explain demand forecasts to inventory planners in 1-2 concise sentences, "
    "referencing the trend, seasonality, and promotion factors provided. Call out when "
    "the forecast is based on insufficient history. Never invent factors not in the input."
)

_FALLBACK_TEMPLATE = (
    "Forecast of {forecast_quantity:.0f} units for {sku_id} at {location_id}: trend "
    "factor {trend_factor:.2f}, seasonality factor {seasonality_factor:.2f}, promotion "
    "factor {promotion_factor:.2f}, based on {history_points_used} historical points."
)


class _MafForecastExplainer(ExplanationAgent):
    def __init__(self, maf_agent: Any) -> None:
        self._maf_agent = maf_agent
        self._fallback = DeterministicFallbackExplainer(_FALLBACK_TEMPLATE)

    def explain(self, factors: dict[str, Any]) -> str:
        try:
            return str(self._maf_agent.run(str(factors)))
        except Exception:
            return self._fallback.explain(factors)


class ForecastExplainerAgent:
    def __init__(self, agent: ExplanationAgent | None = None) -> None:
        if agent is not None:
            self._agent = agent
        else:
            maf_agent = try_load_maf_agent(name="forecast-explainer", instructions=_INSTRUCTIONS)
            self._agent = (
                _MafForecastExplainer(maf_agent)
                if maf_agent is not None
                else DeterministicFallbackExplainer(_FALLBACK_TEMPLATE)
            )

    def explain(self, factors: dict[str, Any]) -> str:
        return self._agent.explain(factors)
