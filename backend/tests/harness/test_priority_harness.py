"""Harness scenario for User Story 8 (T083): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

from src.domain.transfer_balance.priority_models import StorePriorityProfile
from src.domain.transfer_balance.priority_service import StorePriorityService

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def test_store_priority_harness_scenarios(db_session):
    service = StorePriorityService(db_session)

    def happy_path() -> None:
        db_session.add_all(
            [
                StorePriorityProfile(
                    id="hp1",
                    store_id="STORE-HP1",
                    region="north",
                    recent_consumption_rate=15.0,
                    region_weight=0.5,
                    consumption_weight=0.5,
                    current_priority_rank=0,
                ),
                StorePriorityProfile(
                    id="hp2",
                    store_id="STORE-HP2",
                    region="north",
                    recent_consumption_rate=2.0,
                    region_weight=0.5,
                    consumption_weight=0.5,
                    current_priority_rank=0,
                ),
            ]
        )
        db_session.flush()
        ranked = service.recompute_rankings(region="north")
        assert ranked[0].store_id == "STORE-HP1"
        assert ranked[0].narration

    def failure_path() -> None:
        # Recomputing over an empty result set (unknown region) must not raise.
        ranked = service.recompute_rankings(region="unknown-region")
        assert ranked == []

    def data_quality_edge_case() -> None:
        # Conflicting signals: store with tiny consumption but a large regional
        # shortage score should still win when region_weight dominates.
        db_session.add_all(
            [
                StorePriorityProfile(
                    id="dq1",
                    store_id="STORE-DQ1",
                    region="south",
                    recent_consumption_rate=1.0,
                    region_weight=0.9,
                    consumption_weight=0.1,
                    current_priority_rank=0,
                ),
                StorePriorityProfile(
                    id="dq2",
                    store_id="STORE-DQ2",
                    region="south",
                    recent_consumption_rate=100.0,
                    region_weight=0.9,
                    consumption_weight=0.1,
                    current_priority_rank=0,
                ),
            ]
        )
        db_session.flush()
        ranked = service.recompute_rankings(
            region="south",
            region_priority_scores={"STORE-DQ1": 50.0, "STORE-DQ2": 0.0},
        )
        assert ranked[0].store_id == "STORE-DQ1"

    run_scenarios(
        [
            HarnessScenario(
                "consumption-driven ranking with narration", ScenarioKind.HAPPY_PATH, happy_path
            ),
            HarnessScenario(
                "empty region produces empty ranking", ScenarioKind.FAILURE_PATH, failure_path
            ),
            HarnessScenario(
                "region shortage signal outweighs raw consumption",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
