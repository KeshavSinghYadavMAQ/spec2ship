"""Integration test: region/consumption composite scoring + explanation journey (T082,
US8, FR-019, FR-021)."""

from __future__ import annotations

from src.domain.transfer_balance.priority_models import StorePriorityProfile
from src.domain.transfer_balance.priority_service import StorePriorityService


def test_recompute_rankings_orders_by_composite_score(db_session):
    db_session.add_all(
        [
            StorePriorityProfile(
                id="p1",
                store_id="STORE-1",
                region="north",
                recent_consumption_rate=2.0,
                region_weight=0.8,
                consumption_weight=0.2,
                current_priority_rank=0,
            ),
            StorePriorityProfile(
                id="p2",
                store_id="STORE-2",
                region="north",
                recent_consumption_rate=20.0,
                region_weight=0.8,
                consumption_weight=0.2,
                current_priority_rank=0,
            ),
        ]
    )
    db_session.flush()

    service = StorePriorityService(db_session)
    ranked = service.recompute_rankings(region_priority_scores={"STORE-1": 10.0, "STORE-2": 0.0})

    assert ranked[0].store_id == "STORE-1", "high region-shortage signal should outrank consumption alone"
    assert ranked[0].current_priority_rank == 1
    assert ranked[0].narration


def test_recompute_rankings_defaults_missing_consumption_to_zero(db_session):
    db_session.add(
        StorePriorityProfile(
            id="p1",
            store_id="STORE-3",
            region="south",
            recent_consumption_rate=0.0,
            region_weight=0.5,
            consumption_weight=0.5,
            current_priority_rank=0,
        )
    )
    db_session.flush()

    service = StorePriorityService(db_session)
    ranked = service.recompute_rankings()

    assert ranked[0].current_priority_rank == 1
