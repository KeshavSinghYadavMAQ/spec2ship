# Retail Alerting Skill

## Purpose
Define low stock and out-of-stock alerting that is actionable, deduplicated, and role-routed, and define the admin panel for product-location threshold management.

## Capability Scope
- Capability: Low stock and out-of-stock alerting, plus the admin panel for product-location threshold management
- Spec alignment: see the orchestrator's Capability Ownership Map and the active spec (`specs/001-retail-replenishment-v1/spec.md`) for current user stories and requirement IDs

## Use This Skill When
- Designing threshold policy behavior
- Defining urgency and escalation logic
- Mapping channels to role responsibilities
- Designing the admin panel for product-location threshold configuration

## Constitution Alignment
- II: Alert evaluation and threshold configuration logic implemented in Python, agent-explainable where reasoning is involved
- III: Harness scenarios required for burst events and invalid threshold submissions
- IV: Admin panel UI must be responsive and support dark/light mode
- V: Threshold configuration changes must be auditable

## Checklist
- Confirm threshold hierarchy (global, category, SKU, location)
- Confirm deduplication and suppression windows
- Confirm urgency tiers and escalation rules
- Confirm notification routing and delivery assumptions
- Confirm admin panel validation rules and audit trail for threshold changes

## Outputs
- Alert policy definitions
- Alert acceptance scenarios
- Harness scenarios for burst and repeated breaches
- Admin panel requirement refinements and audit trail expectations

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
