# Implementation Plan: Authentication, Row-Level Security & Modern Theme Redesign

**Branch**: `003-auth-rls-theme-redesign` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-auth-rls-theme-redesign/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a real authentication boundary for the retail platform by replacing header-based identity impersonation with server-validated HttpOnly secure-cookie sessions (US1), enforce row-level security across all domain APIs using authoritative per-request role/scope resolution (US2), and refresh every existing React screen with the specified visual system (light and dark palettes, typography, navigation, tables, badges, KPI summary cards, and icons) while preserving accessibility and responsiveness (US3-US6). The implementation extends existing backend and frontend modules without adding new infrastructure services.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x + React 18 (frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2, existing Redis cache client (for short-lived auth/rate-limit state), existing `@fluentui/react-components` + `@fluentui/react-icons` stack, TanStack Query, Playwright + axe-core, Vitest

**Storage**: Existing SQL database (Azure SQL / SQLite dev fallback) with new auth/session tables; optional short-lived cache keys for failed-login windows and lockouts

**Testing**: `pytest` + `pytest-asyncio` + `httpx` for unit/integration/contract/harness tests, Vitest + RTL for frontend logic/token tests, Playwright + axe-core for end-to-end responsive/theme/accessibility validation

**Target Platform**: Azure Container Apps (backend) and Azure Static Web Apps (frontend)

**Project Type**: Web application (existing split frontend + backend monorepo)

**Performance Goals**: Login-to-dashboard under 10s (SC-003); authenticated requests incur no visible regression over current baseline; all redesigned screens remain responsive at current pilot-scale data volumes with no unhandled slowdowns

**Constraints**: Auth sessions must be HttpOnly secure cookies; account lockout policy fixed at 5 failed attempts in rolling 15 minutes causing 30-minute lockout; RLS record lookups return 404 and list endpoints return filtered 200; role/scope must reflect changes by next request; WCAG 2.2 AA in both themes; no client-controlled identity headers on protected endpoints

**Scale/Scope**: 6 user stories, 30 functional requirements; all existing domains affected by auth/RLS middleware and all existing frontend feature screens affected by theme/layout refresh

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Outcome-Driven Retail Value: US1-US2 protect data trust boundaries and prevent cross-store data leakage; US3-US6 improve scanability and operator speed with measurable UX outcomes (SC-005-SC-008).
- [x] Python Agent Backend Standard: Backend changes remain Python-first with explicit domain/service boundaries; existing MAF/Copilot SDK usage is preserved and untouched.
- [x] Harness-First Validation: Plan defines harness and contract tests for login/logout, lockout policy, session invalidation, RLS list filtering, RLS record-level 404 behavior, and full UI theme/responsive/accessibility checks before implementation completion.
- [x] Production React Experience: Plan includes responsive React redesign across all in-scope screens with dark/light parity and icon+label navigation.
- [x] Operational Trustworthiness: Plan includes audit logs for login/logout/auth failures and out-of-scope access denials, plus generic error messaging and secure-by-default session handling.
- [x] Azure Well-Architected and Cost Efficiency: No new managed services required; reuses existing database/cache/app hosting; limits operational cost by in-place extension of current architecture.

**Post-Design Re-check (after Phase 1)**: Re-validated against `research.md`, `data-model.md`, `contracts/auth-rls-ui.yaml`, and `quickstart.md`; all gates remain satisfied with no constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-auth-rls-theme-redesign/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── auth-rls-ui.yaml
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── routers/
│   │   │   └── auth.py                          # NEW login/logout/session endpoints
│   │   ├── dependencies/
│   │   │   └── auth_session.py                  # NEW current-session resolver
│   │   └── main.py                              # MODIFIED protected-route wiring and CORS/session config
│   ├── domain/
│   │   ├── auth/
│   │   │   ├── models.py                        # NEW user-account/session/auth-attempt entities
│   │   │   ├── service.py                       # NEW login/logout/session validation + lockout policy
│   │   │   └── password_policy.py               # NEW password strength + compromised-password checks
│   │   ├── admin/
│   │   │   └── rbac.py                          # MODIFIED to consume authenticated identity context
│   │   ├── inventory/ ... forecasting/... etc   # MODIFIED query-level RLS scoping hooks
│   │   └── security/
│   │       └── scope_service.py                 # NEW per-request role/scope resolution
│   ├── schemas/
│   │   └── auth.py                              # NEW request/response schemas
│   └── infrastructure/
│       └── migrations/versions/                 # NEW migration for auth/session tables
└── tests/
    ├── unit/auth/                               # NEW
    ├── integration/auth/                        # NEW
    ├── contract/                                # NEW auth + RLS contract tests
    └── harness/auth_rls/                        # NEW cross-domain RLS + lockout harness

frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx                              # MODIFIED authenticated shell + nav redesign
│   │   └── routes.tsx                           # MODIFIED protected route wiring
│   ├── components/
│   │   ├── AuthGuard.tsx                        # NEW session gate wrapper
│   │   ├── NavItem.tsx                          # NEW icon+pill nav item
│   │   ├── KpiCard.tsx                          # NEW summary card component
│   │   └── StatusBadge.tsx                      # MODIFIED for redesigned bordered-pill badge styling
│   ├── features/
│   │   ├── auth/LoginPage.tsx                   # NEW responsive login UI
│   │   └── */                                   # MODIFIED all existing feature surfaces for tokens/KPIs/table style
│   ├── services/authClient.ts                   # NEW login/logout/session API client
│   └── theme/
│       ├── tokens.ts                            # MODIFIED with requested light/dark palette and spacing scale
│       └── AppThemeProvider.tsx                 # MODIFIED typography + theme token application
└── tests/
    ├── integration/auth/                        # NEW login/logout/guard tests
    ├── theme/                                   # MODIFIED token consistency checks
    └── e2e/responsive/                          # MODIFIED/NEW full redesign parity and accessibility specs
```

**Structure Decision**: Keep the existing frontend/backend split and add focused auth and security modules rather than spreading auth logic across domain routers. RLS enforcement is centralized via per-request scope resolution and repository/query filters in each domain, while frontend redesign remains token-driven inside the existing Fluent-based theming system.

## Complexity Tracking

*No constitution violations identified. This section is intentionally empty.*
