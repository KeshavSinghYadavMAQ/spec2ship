# Retail Forecasting Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This skill defines a
delivery checklist; forecast calculation stays deterministic and the runtime agent only narrates it.

## Purpose
Define demand forecasting behavior for SKU-store planning with seasonality and event sensitivity.

## Capability Scope
- Capability: Demand forecasting for SKU-store planning with seasonality and event sensitivity
- Spec alignment: see the orchestrator's Capability Ownership Map and the active spec (`specs/001-retail-replenishment-v1/spec.md`) for current user story and requirement IDs

## Use This Skill When
- Scoping forecast capabilities for v1
- Defining inputs and horizons
- Defining quality metrics and validation rules

## Constitution Alignment
- II: Forecast generation implemented in Python; MAF/Copilot SDK used for any agent-driven forecast narration
- III: Harness scenarios required for demand shocks and sparse-data edge cases
- V: Forecast quality indicators must be observable over time

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

Deliverables MUST include executable harness file paths, commands, and results for happy-path,
failure-path, and data-quality scenarios, plus contract-test paths and results for every exposed
contract. Responses MUST include authorization checks, audit events, cost/Azure Well-Architected
evidence, open risks, and the standard handoff recommendation to `retail.orchestrator`.

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
