# Retail Analytics Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point is
guidance only and must not calculate KPI values.

## Purpose
Define dashboard and KPI behavior for daily inventory and replenishment operations.

## Use This Skill When
- Scoping dashboard widgets
- Defining KPI formulas and drill-down behavior
- Validating visibility for operational exceptions

## Checklist
- Confirm core KPI set for v1
- Confirm exception widgets and thresholds
- Confirm filter dimensions (region, store, SKU, time)
- Confirm report outputs and cadence expectations

## Outputs
- Dashboard requirement refinements
- KPI dictionary
- Harness scenarios for KPI correctness and trend validation

## Governance Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.analytics` agent. Deliverables
MUST include executable harness and contract-test paths, commands, and results, plus authorization,
audit, cost, and Azure Well-Architected evidence before handoff to `retail.orchestrator`.
