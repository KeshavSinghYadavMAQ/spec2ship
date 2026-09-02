# Retail Analytics Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This skill defines a
delivery checklist; KPI calculation stays deterministic and harnesses automate validation workflows.

## Purpose
Define dashboard and KPI behavior for daily inventory and replenishment operations.

## Capability Scope
- Capability: Dashboard and KPI behavior for daily inventory and replenishment operations
- Spec alignment: see the orchestrator's Capability Ownership Map and the active spec (`specs/001-retail-replenishment-v1/spec.md`) for current user story and requirement IDs

## Use This Skill When
- Scoping dashboard widgets
- Defining KPI formulas and drill-down behavior
- Validating visibility for operational exceptions

## Constitution Alignment
- II: KPI computation implemented in Python service layer
- III: Harness scenarios required for KPI correctness and drill-down workflows
- IV: Dashboards must be responsive and support dark/light mode
- V: KPI sources must be observable and traceable to underlying events

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

Deliverables MUST include executable harness file paths, commands, and results for happy-path,
failure-path, and data-quality scenarios, plus contract-test paths and results for every exposed
contract. Responses MUST include authorization checks, audit events, cost/Azure Well-Architected
evidence, open risks, and the standard handoff recommendation to `retail.orchestrator`.

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
