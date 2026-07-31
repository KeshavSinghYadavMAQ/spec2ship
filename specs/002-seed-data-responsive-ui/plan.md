# Implementation Plan: Realistic Store Demo Data & Colorful Responsive Theming

**Branch**: `002-seed-data-responsive-ui` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-seed-data-responsive-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver an admin-triggered, idempotent sample-data seeding capability that populates the existing V1 platform (inventory, alerting, replenishment, forecasting, transfer-balance, analytics, admin domains) with realistic, pilot-scale, fictitious retail data (US1), plus a matching clear/reset action, and refresh the existing React frontend with a consistent, colorful, modern Fluent UI v9 design system that stays fully responsive (US3) and preserves dark/light theme parity and WCAG AA contrast (US2, US4) across every existing feature screen. No new services or infrastructure are introduced: seeding reuses existing domain services and a new lightweight seed-record ledger for traceable removal, and theming extends the existing `AppThemeProvider` with a custom Fluent UI brand ramp instead of introducing a second styling system.

## Technical Context

**Language/Version**: Python 3.12 (backend seeding capability, reusing existing domain services), TypeScript 5.x / React 18 (frontend design system)

**Primary Dependencies**: Backend reuses the existing stack (FastAPI, SQLAlchemy 2.0, Pydantic v2) and existing domain services (`inventory`, `alerting`, `replenishment`, `forecasting`, `transfer_balance`, `analytics`) as the only write path for seeded data; no new backend dependency is added — realistic identifiers are generated from curated static reference pools (region/city codes, product categories) combined with a fixed-seed `random.Random`, avoiding a third-party fake-data library. Frontend reuses the existing `@fluentui/react-components` v9 dependency, adding a custom `BrandVariants` palette via Fluent's `createLightTheme`/`createDarkTheme` theme generator — no new frontend dependency.

**Storage**: Same Azure SQL Database (`mssql+pyodbc`) / SQLite dev fallback as spec 001; adds one new lightweight table, `sample_data_seed_records` (a seed-record ledger: `entity_type`, `entity_id`, `seed_batch_id`, `created_at`), owned by a new `sample_data` domain module — existing domain tables are untouched.

**Testing**: pytest + pytest-asyncio + httpx for seeding contract/integration tests and idempotency/resumability harness scenarios under `backend/tests/harness/sample_data`; Vitest + React Testing Library for theme-token unit tests; Playwright + `@axe-core/playwright` (already a frontend dependency) for responsive-breakpoint and WCAG AA contrast harness scenarios across all in-scope screens.

**Target Platform**: Azure Container Apps (backend), Azure Static Web Apps (frontend) — unchanged from spec 001.

**Project Type**: web application (frontend + backend), extending the existing Option 2 structure from spec 001; no new top-level project.

**Performance Goals**: Full pilot-scale seeding run (1,000+ stores, 100,000+ SKUs) completes in under 30 minutes (SC-001, SC-006); all in-scope screens remain responsive with no unhandled slowdowns at pilot-scale data volumes (SC-008).

**Constraints**: Seeding/clear actions gated by both `admin` role (existing RBAC, FR-004) and a non-production environment check (extends existing `Settings.environment`, defaulting to allow only `local`/`dev`/`test`/`staging`); seeding MUST be idempotent and resumable after partial failure with no automatic rollback (FR-003); per-store assortment MUST stay realistic rather than a full store-by-SKU cross product to keep record volume operationally reasonable (FR-005); all colorful UI elements MUST meet WCAG AA contrast in both themes (FR-008, SC-004) and remain distinguishable to colorblind users via non-color cues (FR-010).

**Scale/Scope**: 4 user stories (2 P1, 2 P2), 11 functional requirements, 2 key entities (Sample Data Set, Design Tokens), 2 new admin API endpoints (seed, clear) plus 1 status endpoint, extending the existing RBAC and audit model from spec 001.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Outcome-Driven Retail Value: US1-US4 map to explicit value (faster demos/onboarding/UAT via realistic data, higher operator trust via consistent modern UI) and measurable outcomes (SC-001 to SC-008).
- [x] Python Agent Backend Standard: Seeding is implemented as a Python service in a new `sample_data` domain module that calls existing domain services (no direct storage writes); no agent reasoning is required for this deterministic capability, consistent with the constitution's allowance for deterministic policy logic where correctness matters.
- [x] Harness-First Validation: Harness scenarios planned for seeding idempotency/resumability (happy path, interrupted-seeding recovery, non-production-gate failure path) and for responsive/theme-parity/contrast checks (Playwright + axe-core) before implementation.
- [x] Production React Experience: Plan extends the existing responsive, dark/light-themed React 18 + Fluent UI v9 frontend with a custom brand palette validated for WCAG 2.2 AA contrast across all in-scope screens.
- [x] Operational Trustworthiness: Seeding/clear actions are RBAC-gated (admin + non-production), and logged/audited via the existing admin audit trail (FR-004, FR-011); the seed-record ledger provides traceability for what was removed.
- [x] Azure Well-Architected and Cost Efficiency: No new infrastructure; one new small table adds negligible storage cost; seeding volume is bounded to pilot-scale figures already budgeted in spec 001's cost guardrails.

**Post-Design Re-check (after Phase 1)**: All six gates re-validated against `research.md`, `data-model.md`, and `contracts/sample-data.yaml`. No new violations introduced; no entries required in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/002-seed-data-responsive-ui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── domain/
│   │   ├── sample_data/       # NEW - seeding/clear orchestration, seed-record ledger (US1, FR-001-005, FR-011)
│   │   ├── inventory/         # existing - reused as a write path for seeded inventory positions
│   │   ├── alerting/          # existing - reused for seeded policies/alerts
│   │   ├── replenishment/     # existing - reused for seeded recommendations
│   │   ├── forecasting/       # existing - reused for seeded forecasts
│   │   ├── transfer_balance/  # existing - reused for seeded transfers/priority profiles
│   │   ├── analytics/         # existing - unaffected, consumes seeded data
│   │   └── admin/             # existing - RBAC (require_role(ADMIN)) and audit trail, reused as-is
│   └── api/
│       └── routers/
│           └── admin_sample_data.py  # NEW - POST /v1/admin/sample-data/seed, DELETE /v1/admin/sample-data, GET /v1/admin/sample-data/status
└── tests/
	├── unit/sample_data/          # NEW
	├── integration/sample_data/   # NEW
	├── contract/                  # NEW sample-data contract tests added alongside existing
	└── harness/sample_data/       # NEW - idempotency, resumability, non-prod-gate scenarios

frontend/
├── src/
│   ├── theme/
│   │   ├── AppThemeProvider.tsx   # MODIFIED - consumes new custom brand theme instead of webLightTheme/webDarkTheme
│   │   ├── tokens.ts              # NEW - BrandVariants palette + semantic status/severity tokens (FR-006, FR-010)
│   │   └── ThemeModeContext.ts    # existing - unchanged
│   └── features/                  # existing feature folders (inventory, alerting, replenishment,
│                                   # forecasting, transfer-balance, analytics, admin) - styling updated
│                                   # in place to consume new tokens; no new feature folders added
└── tests/
	├── theme/                     # NEW - token/contrast unit tests
	└── e2e/responsive/            # NEW - Playwright + axe-core breakpoint and contrast harness
```

**Structure Decision**: Extends spec 001's Option 2 (web application) structure without introducing new top-level projects. A new `backend/src/domain/sample_data/` module owns seeding/clear orchestration and the seed-record ledger, kept isolated from other domains per the constitution's guidance to separate infrastructure/lifecycle concerns from core domain logic; it calls existing domain services rather than writing to storage directly. On the frontend, the visual refresh is delivered as an in-place extension of the existing `theme/` module (new `tokens.ts`) consumed by all existing `features/*` folders — no new feature surface is introduced since this is a cross-cutting design-system change, not a new capability.

## Complexity Tracking

*No constitution violations identified. This section is intentionally empty.*
