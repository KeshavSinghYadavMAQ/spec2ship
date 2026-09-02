# Retail Stock Levels Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This skill defines a
delivery checklist; stock arithmetic and replay are deterministic harness concerns.

## Purpose
Define and validate near real-time inventory visibility across shelf, backroom, store, and warehouse stock states.

## Capability Scope
- Capability: Real-time stock visibility across shelf, backroom, store, and warehouse contexts
- Spec alignment: see the orchestrator's Capability Ownership Map and the active spec (`specs/001-retail-replenishment-v1/spec.md`) for current user story and requirement IDs

## Use This Skill When
- Updating stock visibility requirements
- Designing inventory ingest and reconciliation behavior
- Defining freshness and lag targets

## Constitution Alignment
- II: Backend logic implemented in Python using MAF/Copilot SDK conventions where agent reasoning is involved
- III: Harness scenarios required for ingest edge cases before merge
- V: Freshness and reconciliation events must be observable and auditable

## Checklist
- Confirm SKU-location inventory model
- Confirm shelf vs backroom tracking rules
- Confirm event deduplication and ordering behavior
- Confirm freshness SLA and monitoring signals

## Outputs
- Updated acceptance scenarios
- Data contract assumptions
- Harness scenarios for data-quality edge cases

## Governance Gate

Deliverables MUST include executable harness file paths, commands, and results for happy-path,
failure-path, and data-quality scenarios, plus contract-test paths and results for every exposed
contract. Responses MUST include authorization checks, audit events, cost/Azure Well-Architected
evidence, open risks, and the standard handoff recommendation to `retail.orchestrator`.

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
