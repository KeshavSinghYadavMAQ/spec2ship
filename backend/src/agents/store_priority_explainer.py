"""MAF/Copilot SDK priority-factor explanation agent wrapper (T107, US8, per
research.md).

Explanation only — never alters the region/consumption composite score computed by
`priority_service.py` (Constitution II/V).
"""

from __future__ import annotations

from typing import Any

from src.agents.base import DeterministicFallbackExplainer, ExplanationAgent, try_load_maf_agent

_INSTRUCTIONS = (
    "You explain store restoration priority rankings to regional planners in 1-2 "
    "concise sentences, referencing the region score, consumption rate, and their "
    "weights. Never invent factors not in the input."
)

_FALLBACK_TEMPLATE = (
    "Priority rank {current_priority_rank} for {store_id} (region {region}): region "
    "score {region_score:.2f} (weight {region_weight:.2f}), consumption rate "
    "{consumption_rate:.2f} (weight {consumption_weight:.2f}), composite score "
    "{composite_score:.2f}."
)


class _MafStorePriorityExplainer(ExplanationAgent):
    def __init__(self, maf_agent: Any) -> None:
        self._maf_agent = maf_agent
        self._fallback = DeterministicFallbackExplainer(_FALLBACK_TEMPLATE)

    def explain(self, factors: dict[str, Any]) -> str:
        try:
            return str(self._maf_agent.run(str(factors)))
        except Exception:
            return self._fallback.explain(factors)


class StorePriorityExplainerAgent:
    def __init__(self, agent: ExplanationAgent | None = None) -> None:
        if agent is not None:
            self._agent = agent
        else:
            maf_agent = try_load_maf_agent(
                name="store-priority-explainer", instructions=_INSTRUCTIONS
            )
            self._agent = (
                _MafStorePriorityExplainer(maf_agent)
                if maf_agent is not None
                else DeterministicFallbackExplainer(_FALLBACK_TEMPLATE)
            )

    def explain(self, factors: dict[str, Any]) -> str:
        return self._agent.explain(factors)
