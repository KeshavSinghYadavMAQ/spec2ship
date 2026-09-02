# Retail Forecasting Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point is
guidance only and must not calculate forecast values.

## Purpose
Define demand forecasting behavior for SKU-store planning with seasonality and event sensitivity.

## Use This Skill When
- Scoping forecast capabilities for v1
- Defining inputs and horizons
- Defining quality metrics and validation rules

## Checklist
- Confirm historical demand input requirements
- Confirm seasonality and event adjustment support
- Confirm forecast confidence and error metrics
- Confirm forecast-to-recommendation dependency expectations

## Outputs
- Forecasting requirement refinements
- Forecast KPI definitions
- Harness scenarios for demand shocks and sparse data

## Governance Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.forecasting` agent. Deliverables
MUST include executable harness and contract-test paths, commands, and results, plus authorization,
audit, cost, and Azure Well-Architected evidence before handoff to `retail.orchestrator`.
