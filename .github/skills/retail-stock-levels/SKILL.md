# Retail Stock Levels Skill

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

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
