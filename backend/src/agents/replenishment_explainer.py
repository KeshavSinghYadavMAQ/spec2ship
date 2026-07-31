"""MAF/Copilot SDK rationale-explanation agent wrapper (T054, US3, FR-005).

Explanation only, never the reorder decision itself (Constitution II/V). Wraps the
deterministic factor list produced by `engine.py` into operator-facing narration.
"""

from __future__ import annotations

from typing import Any

from src.agents.base import DeterministicFallbackExplainer, ExplanationAgent, try_load_maf_agent

_INSTRUCTIONS = (
    "You explain retail replenishment reorder recommendations to store and inventory "
    "managers in 1-2 concise sentences, referencing the specific stock, demand, and "
    "policy factors provided. Never invent factors that are not in the input."
)

_FALLBACK_TEMPLATE = (
    "Reorder {recommended_quantity} units by {recommended_by_date}: current stock "
    "({current_stock}) is at or below the reorder point ({reorder_point}), with lead "
    "time {lead_time_days} days and safety stock {safety_stock} units."
)


class _MafReplenishmentExplainer(ExplanationAgent):
    """Wraps a live MAF `ChatAgent` instance; falls back to deterministic narration if
    the runtime call fails so an agent-layer error never blocks the API response."""

    def __init__(self, maf_agent: Any) -> None:
        self._maf_agent = maf_agent
        self._fallback = DeterministicFallbackExplainer(_FALLBACK_TEMPLATE)

    def explain(self, factors: dict[str, Any]) -> str:
        try:
            # Real MAF integration point: translate `factors` into a ChatAgent.run() call.
            return str(self._maf_agent.run(str(factors)))
        except Exception:
            return self._fallback.explain(factors)


class ReplenishmentExplainerAgent:
    def __init__(self, agent: ExplanationAgent | None = None) -> None:
        if agent is not None:
            self._agent = agent
        else:
            maf_agent = try_load_maf_agent(
                name="replenishment-explainer", instructions=_INSTRUCTIONS
            )
            self._agent = (
                _MafReplenishmentExplainer(maf_agent)
                if maf_agent is not None
                else DeterministicFallbackExplainer(_FALLBACK_TEMPLATE)
            )

    def explain(self, factors: dict[str, Any]) -> str:
        return self._agent.explain(factors)
