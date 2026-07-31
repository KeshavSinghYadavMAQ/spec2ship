"""Reorder-point/min-max/lead-time/safety-stock recommendation engine (T053, US3, FR-004).

Deterministic reorder math lives here; `ReplenishmentExplainerAgent` (T054) only narrates
the factors this engine computes, never alters the quantity/timing decision
(Constitution II/V).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from src.agents.replenishment_explainer import ReplenishmentExplainerAgent
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition
from src.domain.replenishment.models import (
    ReplenishmentRecommendation,
    ReplenishmentRecommendationRepository,
)


@dataclass
class ReorderDecision:
    should_reorder: bool
    recommended_quantity: int
    recommended_by_date: date
    factors: dict[str, Any]


def _lead_time_days(policy: ProductLocationPolicy) -> int:
    # v1 uses a fixed lead-time assumption per policy; a future iteration could source
    # this from a supplier/lead-time table. Kept explicit so callers/tests can see it.
    return 7


def compute_reorder_decision(
    position: InventoryPosition, policy: ProductLocationPolicy, *, today: date | None = None
) -> ReorderDecision:
    today = today or date.today()
    lead_time_days = _lead_time_days(policy)
    current_stock = position.reconciled_total

    if current_stock > policy.reorder_point:
        return ReorderDecision(
            should_reorder=False,
            recommended_quantity=0,
            recommended_by_date=today,
            factors={"current_stock": current_stock, "reorder_point": policy.reorder_point},
        )

    recommended_quantity = max(0, policy.max_qty - current_stock + policy.safety_stock)
    factors = {
        "current_stock": current_stock,
        "reorder_point": policy.reorder_point,
        "min_qty": policy.min_qty,
        "max_qty": policy.max_qty,
        "safety_stock": policy.safety_stock,
        "lead_time_days": lead_time_days,
        "recommended_quantity": recommended_quantity,
        "recommended_by_date": (today + timedelta(days=lead_time_days)).isoformat(),
    }
    return ReorderDecision(
        should_reorder=recommended_quantity > 0,
        recommended_quantity=recommended_quantity,
        recommended_by_date=today + timedelta(days=lead_time_days),
        factors=factors,
    )


class ReplenishmentEngine:
    def __init__(
        self,
        repo: ReplenishmentRecommendationRepository,
        explainer: ReplenishmentExplainerAgent | None = None,
    ) -> None:
        self._repo = repo
        self._explainer = explainer or ReplenishmentExplainerAgent()

    def generate_recommendation(
        self, position: InventoryPosition, policy: ProductLocationPolicy
    ) -> ReplenishmentRecommendation | None:
        decision = compute_reorder_decision(position, policy)
        if not decision.should_reorder:
            return None

        narration = self._explainer.explain(decision.factors)
        rationale = {"factors": decision.factors, "narration": narration}

        return self._repo.create(
            sku_id=position.sku_id,
            location_id=position.location_id,
            recommended_quantity=decision.recommended_quantity,
            recommended_by_date=decision.recommended_by_date,
            policy_snapshot={
                "reorder_point": policy.reorder_point,
                "min_qty": policy.min_qty,
                "max_qty": policy.max_qty,
                "safety_stock": policy.safety_stock,
            },
            rationale=rationale,
        )
