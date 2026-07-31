# Retail Replenishment Skill

## Purpose
Define explainable replenishment recommendations using policy-driven inventory controls.

## Capability Scope
- Capability: Explainable replenishment recommendations using policy-driven inventory controls
- Spec alignment: see the orchestrator's Capability Ownership Map and the active spec (`specs/001-retail-replenishment-v1/spec.md`) for current user story and requirement IDs

## Use This Skill When
- Designing reorder decision logic
- Refining recommendation rationale content
- Modeling policy overrides and acceptance actions

## Constitution Alignment
- II: Recommendation logic implemented in Python; explanations generated via MAF/Copilot SDK reasoning where applicable
- III: Harness scenarios required for policy and lead-time variations
- V: Recommendation acceptance/override actions must be auditable

## Checklist
- Confirm min-max and reorder point behavior
- Confirm safety stock and lead-time inputs
- Confirm explanation fields for user trust
- Confirm acceptance/override audit behavior

## Outputs
- Recommendation requirements
- Rationale schema
- Harness scenarios for policy and demand shifts

## Handoff & Response Expectations
When this skill is used to produce a deliverable, the response MUST follow the agent's Required Response Format: Scope Confirmation, Constitution Compliance, Deliverables Produced, Harness Coverage, Open Risks/Follow-ups, and a Handoff Recommendation back to `retail.orchestrator`.
