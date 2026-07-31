<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan at
`specs/003-auth-rls-theme-redesign/plan.md` (see also `research.md`, `data-model.md`,
`contracts/`, and `quickstart.md` in the same directory).
<!-- SPECKIT END -->

# Copilot Instructions

## Solution Context

This repository defines a production-grade retail inventory replenishment platform.

Primary solution constraints:

- Backend MUST be implemented in Python.
- Agent workflows MUST use Microsoft Agent Framework (MAF) and Copilot SDK.
- Frontend MUST be implemented in React.
- User-facing experiences MUST be responsive and support both dark and light mode.
- Work MUST align with `.specify/memory/constitution.md` and the active feature spec.

## Backend Guidance

- Prefer clear domain-driven service boundaries for inventory, alerting, replenishment, forecasting, transfer balancing, analytics, and admin configuration.
- Keep business logic out of transport layers. API handlers, routes, and controllers should orchestrate, validate, and delegate to domain services.
- Model agent interactions explicitly. Separate agent prompts, tools, orchestration logic, and business policy evaluation into distinct modules.
- Make Copilot SDK and MAF usage explainable and testable. Agent outputs should be structured, validated, and auditable.
- Prefer typed Python code, explicit schemas, and validation at system boundaries.
- Use deterministic policy logic where required and use agent reasoning to enrich explanations, summarization, prioritization, and operator assistance.
- Build for observability from the start: structured logs, traces, metrics, and audit events are required for recommendation and alert workflows.
- Avoid mixing infrastructure concerns with domain logic. Configuration, storage, queueing, and integration adapters should remain isolated from decision policies.

## Python Best Practices

- Use modern Python patterns with clear package boundaries and descriptive names.
- Prefer small modules and focused classes/functions over large multi-purpose files.
- Use type hints throughout production code.
- Validate external inputs and normalize upstream inventory, sales, and returns data before domain processing.
- Raise explicit domain errors instead of silent fallbacks where correctness matters.
- Keep side effects at the edges. Pure calculation and ranking logic should be easy to unit test.
- Write harnesses and tests for recommendation logic, threshold behavior, prioritization, and failure handling.

## MAF and Copilot SDK Guidance

- Use MAF and Copilot SDK for orchestration, reasoning loops, tool invocation, and explainable decision support.
- Keep prompts versionable and domain-specific.
- Prefer structured agent outputs over free-form text when outputs feed system decisions.
- Always preserve explanation payloads for recommendation and prioritization results.
- Define tool contracts clearly so agent steps can be tested independently.
- Do not let the agent bypass core business safeguards such as thresholds, policy rules, or authorization checks.

## Frontend Guidance

- Use React for all user-facing experiences.
- Prioritize operational usability: fast scanning, clear status hierarchy, safe actions, and minimal ambiguity.
- Design for desktop-first operational workflows while keeping layouts responsive for tablets and mobile web.
- Support both dark and light themes consistently across dashboards, detail screens, and admin workflows.
- Keep components composable and domain-oriented. Separate page composition, view state, and data-fetching concerns.
- Prefer accessible UI patterns and keyboard-friendly workflows for high-frequency operational tasks.
- Ensure charts, tables, alerts, and recommendation panels remain readable in constrained layouts.

## React Best Practices

- Prefer functional components and modern React patterns.
- Keep data fetching and transformation separate from presentational components where possible.
- Avoid over-centralized monolith components; split by domain feature.
- Use explicit loading, empty, error, and stale-data states for operational screens.
- Treat dashboards, alert worklists, admin forms, and recommendation review panels as separate feature surfaces.
- Avoid unnecessary client-side complexity when a simpler server-driven approach works.

## Project Structure

Follow a clear split between frontend, backend, specs, and agent customization assets.

Expected structure for implementation work:

```text
backend/
├── src/
│   ├── agents/
│   ├── api/
│   ├── domain/
│   │   ├── inventory/
│   │   ├── alerting/
│   │   ├── replenishment/
│   │   ├── forecasting/
│   │   ├── transfer_balance/
│   │   ├── analytics/
│   │   └── admin/
│   ├── integrations/
│   ├── schemas/
│   └── infrastructure/
└── tests/
	├── unit/
	├── integration/
	├── contract/
	└── harness/

frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── features/
│   │   ├── inventory/
│   │   ├── alerting/
│   │   ├── replenishment/
│   │   ├── forecasting/
│   │   ├── transfer-balance/
│   │   ├── analytics/
│   │   └── admin/
│   ├── services/
│   ├── hooks/
│   ├── theme/
│   └── utils/
└── tests/

specs/
.github/
.specify/
```

Project structure rules:

- Keep backend and frontend feature boundaries aligned by domain.
- Place recommendation, ranking, threshold, and forecasting logic in backend domain modules, not UI code.
- Place agent definitions and skills under `.github/agents/` and `.github/skills/`.
- Keep feature specs, plans, tasks, and checklists under `specs/`.
- Keep implementation tests close to the correct execution layer: unit, integration, contract, and harness.

## Delivery Expectations

- Start from the active spec and current constitution.
- Preserve V1 scope discipline unless the user explicitly expands scope.
- When adding new operational capabilities, align user stories, requirements, entities, assumptions, and success criteria as needed.
- Prefer minimal, production-ready changes over speculative scaffolding.
- Keep documentation in sync when architecture, agent flow, or delivery workflow changes.
