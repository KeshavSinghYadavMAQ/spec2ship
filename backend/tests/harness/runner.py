"""Harness scenario runner (T007, Constitution III non-negotiable).

Each domain's harness module (e.g. `test_inventory_harness.py`) registers happy-path,
failure-path, and data-quality-edge-case scenarios via `HarnessScenario`. This runner
exists so CI can invoke `pytest tests/harness` as a single gate distinct from
unit/contract/integration suites, per the required backend test layout.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class ScenarioKind(StrEnum):
    HAPPY_PATH = "happy_path"
    FAILURE_PATH = "failure_path"
    DATA_QUALITY_EDGE_CASE = "data_quality_edge_case"


@dataclass
class HarnessScenario:
    name: str
    kind: ScenarioKind
    run: Callable[[], None]

    def execute(self) -> None:
        self.run()


def run_scenarios(scenarios: list[HarnessScenario]) -> None:
    """Execute all scenarios, raising on the first failure with scenario context attached."""
    for scenario in scenarios:
        try:
            scenario.execute()
        except AssertionError as exc:
            raise AssertionError(f"[{scenario.kind}] {scenario.name}: {exc}") from exc
