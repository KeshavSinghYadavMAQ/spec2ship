# Retail Orchestrator Skill

## Purpose
Coordinate end-to-end delivery for the retail replenishment v1 scope (`specs/001-retail-replenishment-v1/spec.md`) across specialized domain agents, while enforcing constitution constraints (`.specify/memory/constitution.md`).

## Use This Skill When
- Work spans multiple feature streams
- Prioritization, sequencing, and dependency control are needed
- Readiness validation is needed before handoff to planning or implementation

## Capability Ownership Map

| Capability | Owning Agent | User Story | Key Requirements |
|---|---|---|---|
| Real-time stock visibility | retail.stock-levels | US1 | FR-001, FR-012 |
| Low stock / out-of-stock alerting | retail.alerting | US2 | FR-002, FR-003 |
| Replenishment recommendations | retail.replenishment | US3 | FR-004, FR-005 |
| Demand forecasting | retail.forecasting | US4 | FR-006, FR-007 |
| Multi-store transfer suggestions | retail.transfer-balance | US5 | FR-008, FR-009 |
| Analytics and dashboards | retail.analytics | US6 | FR-010, FR-011 |
| Admin panel for product-location thresholds | retail.alerting | US7 | FR-016, FR-017, FR-018 |
| Store restoration priority by region/consumption | retail.transfer-balance | US8 | FR-019, FR-020, FR-021 |

This table is the single place where spec-specific story/requirement IDs are pinned. Refresh it here when the spec changes; domain agents and skills describe scope generically by capability so they remain reusable across spec revisions.

## Inputs
- Current spec, plan, tasks, and checklist state
- Current backlog of open decisions and risks
- User story / FR ownership map above

## Handoff Protocol
- Send each domain agent its owned user story ID(s), FR ID(s), and known cross-agent dependencies.
- Require every domain agent to reply using the **Required Response Format** (see below) before marking a capability Ready.
- Do not expand scope beyond the eight user stories without an explicit user request.

## Required Response Format (from every domain agent)
1. **Scope Confirmation** — story/FR IDs addressed and exclusions.
2. **Constitution Compliance** — status against principles II, III, IV, V, VI.
3. **Deliverables Produced** — updated artifacts with file paths.
4. **Harness Coverage** — happy path, failure path, data-quality edge cases.
5. **Open Risks / Follow-ups** — unresolved dependencies or assumptions.
6. **Handoff Recommendation** — `Return to retail.orchestrator`, a named peer agent, or `Ready for /speckit.plan`.

## Outputs
- Ordered execution plan by capability
- Cross-capability dependency map
- Capability-by-capability readiness table (Ready / Blocked / In Progress)
- Consolidated open risks and a single recommended next action

## Guardrails
- Keep v1 scope limited to the eight active user stories in the spec
- Enforce Python backend with Microsoft Agent Framework and Copilot SDK (Constitution II)
- Enforce responsive React with dark/light mode for user-facing paths (Constitution IV)
- Require harness coverage per capability (Constitution III)
- Require observability, auditability, and role-based access evidence (Constitution V)
- Track Azure Well-Architected and cost guardrail impacts (Constitution VI)
