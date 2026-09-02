# Retail Transfer Balance Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This skill defines a
delivery checklist; feasibility and ranking remain deterministic service responsibilities.

## Purpose
Define multi-store balancing and transfer suggestions to reduce shortages and excess stock, and define store restoration priority by region and consumption.

## Capability Scope
- Capability: Multi-store inventory balancing and transfer suggestions, plus store restoration priority by region and consumption
- Spec alignment: see the orchestrator's Capability Ownership Map and the active spec (`specs/001-retail-replenishment-v1/spec.md`) for current user stories and requirement IDs

## Use This Skill When
- Designing transfer recommendation logic
- Defining feasibility constraints
- Validating expected business impact
- Designing store restoration priority scoring by region and consumption

## Constitution Alignment
- II: Transfer and priority ranking logic implemented in Python, agent-explainable where reasoning is involved
- III: Harness scenarios required for regional imbalance and conflicting priority-signal cases
- V: Priority factors and transfer decisions must be explainable and auditable

## Checklist
- Confirm source/destination eligibility
- Confirm feasibility constraints (availability, lead time, policy)
- Confirm transfer ranking and tie-break logic
- Confirm transfer tracking status expectations
- Confirm store priority weighting factors (region, consumption) and explainability requirements

## Outputs
- Transfer recommendation requirements
- Feasibility assumptions
- Harness scenarios for regional imbalance patterns
- Store priority requirement refinements and priority factor explanation schema

## Governance Gate

Deliverables MUST include executable harness file paths, commands, and results for happy-path,
failure-path, and data-quality scenarios, plus contract-test paths and results for every exposed
contract. Responses MUST include authorization checks, audit events for priority and transfer
decisions, cost/Azure Well-Architected evidence, open risks, and the standard handoff recommendation
to `retail.orchestrator`.

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
