"""Imbalance detection + feasibility-constrained transfer engine (T070, US5, FR-008,
FR-009, FR-020).

Reads `StorePriorityProfile` (Foundational stub from T022, refined by US8's full scoring
service in T084) to rank destination stores. Never proposes a transfer that would breach
the source location's own minimum threshold (feasibility constraint).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.inventory.models import InventoryPosition
from src.domain.transfer_balance.models import (
    FeasibilityStatus,
    TransferSuggestion,
    TransferSuggestionRepository,
)


@dataclass
class TransferCandidate:
    should_transfer: bool
    suggested_quantity: int
    feasibility_status: FeasibilityStatus
    feasibility_reason: str
    factors: dict[str, Any]


def evaluate_transfer_pair(
    *,
    source_position: InventoryPosition,
    source_policy: ProductLocationPolicy,
    destination_position: InventoryPosition,
    destination_policy: ProductLocationPolicy,
) -> TransferCandidate:
    source_stock = source_position.reconciled_total
    destination_stock = destination_position.reconciled_total

    source_surplus = max(0, source_stock - source_policy.max_qty)
    destination_deficit = max(0, destination_policy.reorder_point - destination_stock)

    factors = {
        "source_stock": source_stock,
        "source_max_qty": source_policy.max_qty,
        "source_min_qty": source_policy.min_qty,
        "source_surplus": source_surplus,
        "destination_stock": destination_stock,
        "destination_reorder_point": destination_policy.reorder_point,
        "destination_deficit": destination_deficit,
    }

    if source_surplus <= 0 or destination_deficit <= 0:
        return TransferCandidate(
            should_transfer=False,
            suggested_quantity=0,
            feasibility_status=FeasibilityStatus.INFEASIBLE,
            feasibility_reason="No surplus at the source location or no deficit at the destination",
            factors=factors,
        )

    max_transferable_without_breaching_source_min = max(0, source_stock - source_policy.min_qty)
    suggested_quantity = min(
        source_surplus, destination_deficit, max_transferable_without_breaching_source_min
    )
    factors["max_transferable_without_breaching_source_min"] = (
        max_transferable_without_breaching_source_min
    )

    if suggested_quantity <= 0:
        return TransferCandidate(
            should_transfer=False,
            suggested_quantity=0,
            feasibility_status=FeasibilityStatus.INFEASIBLE,
            feasibility_reason="Transfer would breach the source location's own minimum threshold",
            factors=factors,
        )

    return TransferCandidate(
        should_transfer=True,
        suggested_quantity=suggested_quantity,
        feasibility_status=FeasibilityStatus.FEASIBLE,
        feasibility_reason="Surplus available at source without breaching source minimum",
        factors=factors,
    )


class TransferBalanceEngine:
    def __init__(self, repo: TransferSuggestionRepository) -> None:
        self._repo = repo

    def generate_suggestion(
        self,
        *,
        source_position: InventoryPosition,
        source_policy: ProductLocationPolicy,
        destination_position: InventoryPosition,
        destination_policy: ProductLocationPolicy,
        priority_rank: int = 0,
    ) -> TransferSuggestion | None:
        candidate = evaluate_transfer_pair(
            source_position=source_position,
            source_policy=source_policy,
            destination_position=destination_position,
            destination_policy=destination_policy,
        )
        if not candidate.should_transfer:
            return None

        return self._repo.create(
            sku_id=source_position.sku_id,
            source_location_id=source_position.location_id,
            destination_location_id=destination_position.location_id,
            suggested_quantity=candidate.suggested_quantity,
            feasibility_status=candidate.feasibility_status,
            feasibility_reason=candidate.feasibility_reason,
            priority_rank=priority_rank,
            factors=candidate.factors,
        )
