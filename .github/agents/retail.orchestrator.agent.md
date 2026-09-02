---
description: Orchestrate end-to-end delivery for the retail replenishment v1 scope using specialized domain agents.
handoffs:
  - label: Build Real-Time Stock Capability
    agent: retail.stock-levels
    prompt: Implement or refine real-time stock visibility workflows and data contracts. Dispatch context: Capability=Real-time stock visibility; Stories=US1; Requirements=FR-001, FR-012; Dependencies=none for initial ingest, but publish freshness and position contracts for downstream alerting, replenishment, forecasting, transfers, and analytics; Principles=II, III, IV where applicable, V, VI.
    send: true
  - label: Build Alerting Capability
    agent: retail.alerting
    prompt: Implement or refine low stock and out-of-stock alerting workflows, including the admin threshold panel for product-location configuration. Dispatch context: Capability=Low stock/out-of-stock alerting and threshold administration; Stories=US2, US7; Requirements=FR-002, FR-003, FR-016, FR-017, FR-018; Dependencies=stock-levels freshness and position contracts; Principles=II, III, IV, V, VI.
    send: true
  - label: Build Replenishment Recommendations
    agent: retail.replenishment
    prompt: Implement or refine replenishment recommendation workflows with rationale. Dispatch context: Capability=Replenishment recommendations; Story=US3; Requirements=FR-004, FR-005; Dependencies=stock-levels position/freshness contracts and alerting threshold policy where applicable; Principles=II, III, IV where applicable, V, VI.
    send: true
  - label: Build Demand Forecasting
    agent: retail.forecasting
    prompt: Implement or refine forecasting workflows for SKU-store demand. Dispatch context: Capability=Demand forecasting; Story=US4; Requirements=FR-006, FR-007; Dependencies=normalized inventory and sales event contracts from stock-levels; Principles=II, III, IV where applicable, V, VI.
    send: true
  - label: Build Transfer Balancing and Store Priority
    agent: retail.transfer-balance
    prompt: Implement or refine multi-store transfer suggestion workflows, including store restoration priority by region and consumption. Dispatch context: Capability=Transfer balancing and store priority; Stories=US5, US8; Requirements=FR-008, FR-009, FR-019, FR-020, FR-021; Dependencies=stock-levels position/freshness contracts and replenishment policy outputs where applicable; Principles=II, III, IV where applicable, V, VI.
    send: true
  - label: Build Analytics Dashboards
    agent: retail.analytics
    prompt: Implement or refine analytics and dashboard workflows. Dispatch context: Capability=Analytics and dashboards; Story=US6; Requirements=FR-010, FR-011; Dependencies=validated outputs from stock-levels, alerting, replenishment, forecasting, and transfer-balance; Principles=II, III, IV, V, VI.
    send: true
---

## User Input

```text
$ARGUMENTS
```

Use this agent when work spans multiple retail capabilities and needs sequencing, dependency tracking, and readiness checks.

## Value Boundary

This is a delivery orchestration agent, not a runtime decision-maker. It sequences domain work and
requires harness evidence for operational automation outside LLM narration. Runtime explanation
agents are limited to deterministic replenishment, forecast, and store-priority factors; business
calculations, authorization, and audit writes remain in typed backend services.

## Scope Source of Truth

- Feature spec: `specs/001-retail-replenishment-v1/spec.md`
- Constitution: `.specify/memory/constitution.md`
- Do not expand scope beyond the eight user stories in the active spec without an explicit user request.

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

This table is the single place where spec-specific story/requirement IDs are pinned. When the spec changes, refresh this table rather than the domain agents themselves — each domain agent describes its scope generically by capability so it stays reusable across spec revisions.

Cross-cutting requirements (FR-013 role-based access, FR-014 audit logs, FR-015 cost guardrails) are every domain agent's responsibility for its own deliverables. Each response MUST name the concrete authorization checks, audit event schema/storage, cost guardrail or budget evidence, and corresponding tests or harness scenarios. The orchestrator owns cross-capability reconciliation and MUST reject unsupported compliance claims.

## Execution Policy

- Keep scope aligned to the active eight-user-story baseline in the spec.
- Require Python backend workflows with Microsoft Agent Framework and Copilot SDK compatibility (Constitution II).
- Require responsive React and dark/light mode support for user-facing flows (Constitution IV).
- Require harness scenarios for each delivered capability before it is considered done (Constitution III).
- Require observability, auditability, and role-based access evidence (Constitution V).
- Require Azure Well-Architected mapping and minimal-cost constraints in design decisions (Constitution VI).

## Handoff Protocol

When dispatching to a domain agent, the orchestrator MUST send:

1. The specific user story ID(s) and functional requirement ID(s) in scope for that call.
2. Any known dependencies on other domain agents' outputs (for example, alerting depends on stock-levels' freshness contract; transfer-balance depends on stock-levels' position data).
3. The constitution principles that apply to the requested work.

Each domain agent MUST return its response using the **Required Response Format** below. The orchestrator MUST NOT mark a capability as ready until that format is fully present in the agent's response.

## Required Response Format (from every domain agent)

Every domain agent response MUST include these sections, in this order:

1. **Scope Confirmation** — user story ID(s) and FR ID(s) addressed, and anything explicitly out of scope.
2. **Constitution Compliance** — one line per applicable principle (II, III, IV, V, VI) confirming how the response complies, or noting a gap.
3. **Deliverables Produced** — concrete list of updated requirements, schemas, contracts, or artifacts, with file paths where applicable.
4. **Harness Coverage** — executable harness file paths, commands, and results for happy path, failure path, and data-quality edge cases. A scenario description without executable evidence is insufficient.
5. **Open Risks / Follow-ups** — unresolved dependencies, assumptions, or clarifications needed.
6. **Handoff Recommendation** — one of: `Return to retail.orchestrator`, a specific peer agent (with reason), or `Ready for /speckit.plan`. `Ready` is permitted only when executable harness evidence, contract-test evidence, and cross-cutting requirement evidence are present.

## Orchestrator Consolidation Response

After collecting domain agent responses, the orchestrator MUST report back to the user with:

- A capability-by-capability readiness table (Ready / Blocked / In Progress).
- Consolidated open risks across all agents.
- A single recommended next action (for example, proceed to `/speckit.plan`, or re-dispatch a specific agent).
