# Implementation Plan: Retail Replenishment V1 Foundation

**Branch**: `001-retail-replenishment-v1` (pinned via `.specify/feature.json`; git branch: `Main`) | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-retail-replenishment-v1/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver the V1 retail replenishment platform: real-time stock visibility (US1), low/out-of-stock alerting (US2), explainable replenishment recommendations (US3), demand forecasting (US4), multi-store transfer balancing (US5), operational analytics dashboards (US6), an admin panel for product-location thresholds (US7), and region/consumption-based store restoration priority (US8). The backend is a Python service layer orchestrated with Microsoft Agent Framework and the Copilot SDK for explainable reasoning (rationale generation, prioritization narration), backed by durable relational storage and a message-queue-based ingestion pipeline that satisfies the queue-and-replay resilience requirement (FR-022) at enterprise scale (1,000+ stores, 100,000+ SKUs, per Clarifications). The frontend is a responsive React application with first-class dark/light theming, delivered as a single-language (English) v1 experience with externalized UI text for future localization. See [architecture.md](./architecture.md) for the system context and component diagram.

## Technical Context

**Language/Version**: Python 3.12 (backend, agents), TypeScript 5.x (frontend)

**Primary Dependencies**: FastAPI (async API layer), Microsoft Agent Framework, Copilot SDK, Pydantic v2 (schemas/validation), SQLAlchemy 2.0 (ORM, `mssql+pyodbc` dialect for Azure SQL Database); React 18 + Vite + TypeScript, `@fluentui/react-components` (Fluent UI v9 for built-in dark/light theming and accessibility), TanStack Query (server-state data fetching)

**Storage**: Azure SQL Database (vCore, general purpose tier) for domain data: inventory positions, alerts, recommendations, forecasts, transfers, policies, priority profiles, audit log; Azure Cache for Redis (dedup/suppression windows, evaluation locks for FR-023); Azure Service Bus (inbound event queue and replay for FR-022)

**Testing**: pytest + pytest-asyncio + httpx (backend unit/contract/integration), harness scenario runner under `backend/tests/harness` (Constitution III), Vitest + React Testing Library (frontend), Playwright (critical-path UI flows)

**Target Platform**: Azure Container Apps (Linux containers) for backend services; Azure Static Web Apps for the React frontend

**Project Type**: web application (frontend + backend, per Option 2 structure below)

**Performance Goals**: Stock position visibility within 60s for 95% of updates (SC-001); alert notification within 2 minutes for 90% of breaches (SC-003); dashboard triage workflows completed in under 2 minutes for 90% of sessions (SC-007); 99.9% monthly platform uptime (SC-009)

**Constraints**: Enterprise-scale volume (1,000+ stores, 100,000+ SKUs per Clarifications) driving throughput/storage sizing; single-language (English) v1 UI with externalized text; queue-and-replay resilience for upstream source outages (FR-022); threshold-edit lock during in-flight evaluations (FR-023); per-source-system ingestion rate limiting with retryable 429 responses (FR-024); monthly pilot operating cost ceiling of $15,000/month and a $0.00005-per-ingested-event budget assumption (SC-008, Constitution VI)

**Scale/Scope**: 8 user stories (3 P1, 4 P2, 1 P3), 24 functional requirements, 10 key entities, RBAC across 5 roles, enterprise-scale data volume (1,000+ stores, 100,000+ SKUs)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Outcome-Driven Retail Value: Every user story (US1-US8) maps to explicit business value and measurable outcomes (SC-001 to SC-008).
- [x] Python Agent Backend Standard: Technical approach uses a Python 3.12 backend with Microsoft Agent Framework and Copilot SDK for explainable reasoning (replenishment rationale, prioritization narration).
- [x] Harness-First Validation: Harness scenarios (happy path, failure path, data-quality edge cases) are planned per domain under `backend/tests/harness` before implementation.
- [x] Production React Experience: React 18 + Fluent UI v9 delivers responsive, dark/light-themed, accessible (WCAG 2.2 AA) UI for alerts, recommendations, approvals, and dashboards.
- [x] Operational Trustworthiness: Structured logging/metrics/traces, RBAC (FR-013), auditable logs (FR-014, FR-018), per-source ingestion rate limiting (FR-024), and a 99.9% monthly uptime target (SC-009) are planned across all domains.
- [x] Azure Well-Architected and Cost Efficiency: Azure Container Apps + managed Azure SQL Database/Redis/Service Bus with autoscaling boundaries, single-region reliability design meeting SC-009, and environment tiering; cost guardrails tracked per SC-008 ($15,000/month pilot ceiling, $0.00005/event ingestion assumption) and FR-015.

**Post-Design Re-check (after Phase 1)**: All six gates re-validated against `research.md`, `data-model.md`, and
`contracts/openapi.yaml`. No new violations introduced; no entries required in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-retail-replenishment-v1/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── architecture.md      # System architecture diagram and component notes
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/               # MAF/Copilot SDK agent prompts, tools, orchestration
│   ├── api/                  # FastAPI routers: inventory, alerting, replenishment, forecasting, transfer_balance, analytics, admin
│   ├── domain/
│   │   ├── inventory/        # US1 - stock position, reconciliation
│   │   ├── alerting/         # US2, US7 - thresholds, alerts, admin threshold panel logic
│   │   ├── replenishment/    # US3 - reorder policy, recommendations, rationale
│   │   ├── forecasting/      # US4 - demand forecasts, quality indicators
│   │   ├── transfer_balance/ # US5, US8 - transfer suggestions, store priority
│   │   ├── analytics/        # US6 - KPI aggregation
│   │   └── admin/            # RBAC, audit trail, configuration
│   ├── integrations/         # Inbound event adapters, queue/replay (FR-022)
│   ├── schemas/               # Pydantic request/response/domain schemas
│   └── infrastructure/       # DB, cache, service bus, observability wiring
└── tests/
	├── unit/
	├── integration/
	├── contract/
	└── harness/

frontend/
├── src/
│   ├── app/                  # Routing, theme provider, layout shell
│   ├── components/           # Shared, domain-agnostic UI primitives
│   ├── features/
│   │   ├── inventory/
│   │   ├── alerting/
│   │   ├── replenishment/
│   │   ├── forecasting/
│   │   ├── transfer-balance/
│   │   ├── analytics/
│   │   └── admin/
│   ├── services/              # API clients (TanStack Query)
│   ├── hooks/
│   ├── theme/                 # Dark/light theme tokens
│   └── utils/
└── tests/
```

**Structure Decision**: Option 2 (web application: frontend + backend), matching the mandated project structure in `.github/copilot-instructions.md`. Backend domain modules map 1:1 to the retail domain agents (`retail.stock-levels`, `retail.alerting`, `retail.replenishment`, `retail.forecasting`, `retail.transfer-balance`, `retail.analytics`) with the admin panel (US7) folded into `alerting`/`admin`, and store priority (US8) folded into `transfer_balance`, consistent with the orchestrator's Capability Ownership Map.

## Complexity Tracking

*No constitution violations identified. This section is intentionally empty.*
