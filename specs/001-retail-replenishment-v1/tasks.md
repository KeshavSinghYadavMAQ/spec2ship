# Tasks: Retail Replenishment V1 Foundation

**Input**: Design documents from `/specs/001-retail-replenishment-v1/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests and Harness**: Test and harness tasks are REQUIRED. Every user story includes contract/integration tests and a harness scenario (happy path, failure path, data-quality edge case per Constitution III) before implementation is considered complete.

**Organization**: Tasks are grouped by user story (US1–US8, per [spec.md](./spec.md)) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- File paths follow the Option 2 (web app) structure defined in [plan.md](./plan.md#project-structure)

## Path Conventions

- Backend: `backend/src/{agents,api,domain/{inventory,alerting,replenishment,forecasting,transfer_balance,analytics,admin},integrations,schemas,infrastructure}`, `backend/tests/{unit,integration,contract,harness}`
- Frontend: `frontend/src/{app,components,features/{inventory,alerting,replenishment,forecasting,transfer-balance,analytics,admin},services,hooks,theme,utils}`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure per [plan.md](./plan.md): `backend/src/{agents,api,domain/{inventory,alerting,replenishment,forecasting,transfer_balance,analytics,admin},integrations,schemas,infrastructure}`, `backend/tests/{unit,integration,contract,harness}`
- [X] T002 Create frontend project structure per [plan.md](./plan.md): `frontend/src/{app,components,features/{inventory,alerting,replenishment,forecasting,transfer-balance,analytics,admin},services,hooks,theme,utils}`, `frontend/tests/`
- [X] T003 [P] Initialize backend Python 3.12 project (`backend/pyproject.toml`) with FastAPI, Microsoft Agent Framework, Copilot SDK, Pydantic v2, SQLAlchemy 2.0 (`mssql+pyodbc`), pytest, pytest-asyncio, httpx
- [X] T004 [P] Initialize frontend Vite + React 18 + TypeScript project (`frontend/package.json`) with `@fluentui/react-components`, `@tanstack/react-query`
- [X] T005 [P] Configure backend linting/formatting/type-checking (ruff, black, mypy) in `backend/pyproject.toml`
- [X] T006 [P] Configure frontend ESLint/Prettier/TypeScript strict config in `frontend/.eslintrc.cjs`, `frontend/tsconfig.json`
- [X] T007 Establish harness scaffolding (scenario runner + CI wiring) in `backend/tests/harness/runner.py`
- [X] T008 [P] Configure Vitest and Playwright test runners in `frontend/tests/`

**Checkpoint**: Tooling and scaffolding ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Setup Azure SQL Database connection/session management in `backend/src/infrastructure/db.py` (async-bridge engine per [research.md](./research.md))
- [X] T010 Setup Alembic migrations framework in `backend/src/infrastructure/migrations/`
- [X] T011 [P] Implement Redis client wrapper in `backend/src/infrastructure/cache.py` (suppression windows FR-003, evaluation locks FR-023, rate-limit token buckets FR-024)
- [X] T012 [P] Implement Azure Service Bus client wrapper in `backend/src/infrastructure/queue.py` (inbound event queue/replay FR-022)
- [X] T013 [P] Define `ProblemDetail` error schema in `backend/src/schemas/errors.py`
- [X] T014 [P] Implement `UserRoleAssignment` model and RBAC authorization dependency in `backend/src/domain/admin/rbac.py` (FR-013, 5 roles)
- [X] T015 Implement per-source-system rate-limiting middleware in `backend/src/api/middleware/rate_limit.py` (FR-024: 429 + `Retry-After`, token bucket via Redis)
- [X] T016 [P] Setup FastAPI app, `/v1` versioned router mounting, and exception handlers (map to `ProblemDetail`) in `backend/src/api/main.py`
- [X] T017 [P] Configure structured logging, metrics, and tracing baseline in `backend/src/infrastructure/observability.py`
- [X] T018 [P] Configure environment/config management (Pydantic Settings) in `backend/src/infrastructure/config.py`
- [X] T019 Implement `IntegrationEvent` model and queue-and-replay processing service in `backend/src/domain/inventory/integration_event.py` (FR-022; queued → processing → applied, or dead_lettered → replayed → applied)
- [X] T020 Implement `InventoryPosition` model and repository in `backend/src/domain/inventory/models.py` (shared read dependency for US2–US8)
- [X] T021 Implement `ProductLocationPolicy` model with `edit_lock_held` field in `backend/src/domain/alerting/policy_models.py` (FR-016, FR-023; shared read dependency for US2/US3)
- [X] T022 Implement `StorePriorityProfile` model in `backend/src/domain/transfer_balance/priority_models.py` (FR-019; shared read dependency for US5)
- [X] T023 [P] Implement audit log writer service in `backend/src/domain/admin/audit.py` (FR-014, FR-018)
- [X] T024 [P] Setup React app shell, routing, and Fluent UI theme provider with dark/light toggle in `frontend/src/app/App.tsx` and `frontend/src/theme/`
- [X] T025 [P] Configure TanStack Query client and base API service in `frontend/src/services/apiClient.ts`
- [X] T026 [P] Add responsive layout and dark/light theme snapshot tests in `frontend/tests/theme.test.tsx`
- [X] T027 [P] Implement cost-guardrail tracking hooks (SC-008, Constitution VI) in `backend/src/infrastructure/cost_guardrails.py`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - View Real-Time Stock Position (Priority: P1) 🎯 MVP

**Goal**: Store/inventory managers can see current stock by store, warehouse, shelf, and backroom.

**Independent Test**: Ingest stock and sales events for multiple SKUs and verify visible stock state matches expected quantities by location and stock type.

### Tests and Harness for User Story 1 (REQUIRED) ⚠️

- [X] T028 [P] [US1] Contract test `GET /v1/inventory/positions` in `backend/tests/contract/test_inventory_positions.py`
- [X] T029 [P] [US1] Contract test `POST /v1/inventory/events` (incl. 429 rate-limit response) in `backend/tests/contract/test_inventory_events.py`
- [X] T030 [P] [US1] Integration test for shelf/backroom reconciliation journey in `backend/tests/integration/test_inventory_reconciliation.py`
- [X] T031 [US1] Harness scenario — happy path (stock update visible within freshness target), failure path (malformed event), data-quality edge case (duplicate/out-of-order events) in `backend/tests/harness/test_inventory_harness.py`

### Implementation for User Story 1

- [X] T032 [US1] Implement inventory reconciliation service (shelf+backroom totals, dedupe/out-of-order handling) in `backend/src/domain/inventory/service.py` (FR-001)
- [X] T033 [US1] Implement `GET /v1/inventory/positions` endpoint in `backend/src/api/routers/inventory.py`
- [X] T034 [US1] Implement `POST /v1/inventory/events` endpoint wired to Service Bus queue + rate-limit middleware in `backend/src/api/routers/inventory.py` (FR-012, FR-024); also invokes `ThresholdEvaluationService` for the affected sku/location after ingest so a breach raises a `StockAlert` synchronously (FR-002, fixed post-implementation review 2026-08-01 — previously only exercised by tests, not wired into the router)
- [X] T035 [US1] Implement replay/reconciliation worker with data-freshness warning flag in `backend/src/domain/inventory/replay_worker.py` (FR-022)
- [X] T036 [P] [US1] Build inventory position table/detail view (shelf/backroom/reconciled total, freshness indicator) in `frontend/src/features/inventory/InventoryPositionView.tsx`
- [X] T037 [US1] Wire inventory feature to API via TanStack Query hooks in `frontend/src/features/inventory/hooks/useInventoryPositions.ts`
- [X] T038 [US1] Add loading/empty/error/stale-data states to the inventory view

**Checkpoint**: User Story 1 fully functional and independently testable.

---

## Phase 4: User Story 2 - Act on Low and Out-of-Stock Alerts (Priority: P1)

**Goal**: Operations users receive low-stock/out-of-stock alerts quickly and can act on them through their lifecycle.

**Independent Test**: Configure thresholds and verify alert generation, urgency, deduplication, and channel routing using synthetic inventory changes.

### Tests and Harness for User Story 2 (REQUIRED) ⚠️

- [X] T039 [P] [US2] Contract test `GET /v1/alerts` and `POST /v1/alerts/{alertId}/transition` in `backend/tests/contract/test_alerts.py`
- [X] T040 [P] [US2] Integration test for threshold breach → alert → routing → suppression journey in `backend/tests/integration/test_alert_lifecycle.py`
- [X] T041 [US2] Harness scenario — happy path (low-stock alert routed), failure path (routing channel unavailable), data-quality edge case (repeated breaches suppressed) in `backend/tests/harness/test_alerting_harness.py`

### Implementation for User Story 2

- [X] T042 [US2] Implement `StockAlert` model with 5-state lifecycle (Open, Acknowledged, Escalated, Snoozed, Resolved) in `backend/src/domain/alerting/models.py`
- [X] T043 [US2] Implement threshold evaluation service reading `ProductLocationPolicy` + `InventoryPosition` in `backend/src/domain/alerting/evaluation_service.py` (FR-002)
- [X] T044 [US2] Implement alert deduplication/suppression using Redis TTL windows in `backend/src/domain/alerting/suppression.py` (FR-003)
- [X] T045 [US2] Implement alert routing/notification dispatch in `backend/src/domain/alerting/routing.py` (FR-003)
- [X] T046 [US2] Implement `GET /v1/alerts` and `POST /v1/alerts/{alertId}/transition` endpoints in `backend/src/api/routers/alerts.py`
- [X] T047 [P] [US2] Build alert worklist view (status/severity filters, lifecycle transitions) in `frontend/src/features/alerting/AlertWorklist.tsx`
- [X] T048 [US2] Wire alerting feature to API via TanStack Query hooks in `frontend/src/features/alerting/hooks/useAlerts.ts`

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Use Automated Replenishment Recommendations (Priority: P1)

**Goal**: Inventory managers receive explainable reorder recommendations.

**Independent Test**: Supply stock, demand, lead-time, and policy inputs, then verify recommendation quantity, timing, and rationale.

### Tests and Harness for User Story 3 (REQUIRED) ⚠️

- [X] T049 [P] [US3] Contract test `GET /v1/replenishment/recommendations` and `POST /v1/replenishment/recommendations/{id}/decision` in `backend/tests/contract/test_replenishment.py`
- [X] T050 [P] [US3] Integration test recommendation generation + explanation journey in `backend/tests/integration/test_replenishment_flow.py`
- [X] T051 [US3] Harness scenario — happy path (reorder quantity/timing produced), failure path (missing policy inputs), data-quality edge case (abrupt lead-time change) in `backend/tests/harness/test_replenishment_harness.py`

### Implementation for User Story 3

- [X] T052 [US3] Implement `ReplenishmentRecommendation` model in `backend/src/domain/replenishment/models.py`
- [X] T053 [US3] Implement reorder-point/min-max/lead-time/safety-stock recommendation engine in `backend/src/domain/replenishment/engine.py` (FR-004)
- [X] T054 [US3] Implement MAF/Copilot SDK rationale-explanation agent wrapper (explanation only, not the decision) in `backend/src/agents/replenishment_explainer.py` (FR-005)
- [X] T055 [US3] Implement `GET /v1/replenishment/recommendations` and decision endpoints in `backend/src/api/routers/replenishment.py`
- [X] T056 [P] [US3] Build recommendation review panel with rationale display and accept/override/dismiss actions in `frontend/src/features/replenishment/RecommendationPanel.tsx`
- [X] T057 [US3] Wire replenishment feature to API via TanStack Query hooks in `frontend/src/features/replenishment/hooks/useRecommendations.ts`
- [X] T105 [US3] Capture operator actionability rating on the recommendation decision endpoint/UI (extend `POST /v1/replenishment/recommendations/{id}/decision` schema + `RecommendationPanel.tsx`) to measure SC-004 in `backend/src/api/routers/replenishment.py` and `frontend/src/features/replenishment/RecommendationPanel.tsx`

**Checkpoint**: All P1 stories (US1–US3) independently functional — MVP.

---

## Phase 6: User Story 4 - Forecast Demand by Store and SKU (Priority: P2)

**Goal**: Planners review demand forecasts using trend, seasonal, and promotion context.

**Independent Test**: Submit historical demand with seasonal/promotion attributes and verify forecast outputs and error indicators by SKU and store.

### Tests and Harness for User Story 4 (REQUIRED) ⚠️

- [X] T058 [P] [US4] Contract test `GET /v1/forecasts` in `backend/tests/contract/test_forecasts.py`
- [X] T059 [P] [US4] Integration test forecast generation with seasonal/promotion adjustment in `backend/tests/integration/test_forecasting_flow.py`
- [X] T060 [US4] Harness scenario — happy path (store/SKU projections), failure path (insufficient history), data-quality edge case (promotion-driven demand spike) in `backend/tests/harness/test_forecasting_harness.py`

### Implementation for User Story 4

- [X] T061 [US4] Implement `DemandForecast` model in `backend/src/domain/forecasting/models.py`
- [X] T062 [US4] Implement trend/seasonality/promotion-aware forecasting engine and error indicators in `backend/src/domain/forecasting/engine.py` (FR-006, FR-007)
- [X] T063 [US4] Implement `GET /v1/forecasts` endpoint in `backend/src/api/routers/forecasting.py`
- [X] T106 [US4] Implement MAF/Copilot SDK forecast-narration agent wrapper (explanation only, not the projection logic) in `backend/src/agents/forecast_explainer.py` (per research.md Agent orchestration decision)
- [X] T064 [P] [US4] Build forecast review view with quality/error indicators in `frontend/src/features/forecasting/ForecastView.tsx`
- [X] T065 [US4] Wire forecasting feature to API via TanStack Query hooks in `frontend/src/features/forecasting/hooks/useForecasts.ts`

**Checkpoint**: US1–US4 functional.

---

## Phase 7: User Story 5 - Balance Inventory via Transfer Suggestions (Priority: P2)

**Goal**: Regional planners receive transfer suggestions between stores/warehouses.

**Independent Test**: Simulate regional overstock and shortage patterns, then verify transfer suggestions and feasibility constraints.

### Tests and Harness for User Story 5 (REQUIRED) ⚠️

- [X] T066 [P] [US5] Contract test `GET /v1/transfers/suggestions` and status-update endpoint in `backend/tests/contract/test_transfers.py`
- [X] T067 [P] [US5] Integration test overstock/shortage balancing journey in `backend/tests/integration/test_transfer_flow.py`
- [X] T068 [US5] Harness scenario — happy path (transfer recommendation generated), failure path (infeasible transfer excluded), data-quality edge case (conflicting store priority signals) in `backend/tests/harness/test_transfer_harness.py`

### Implementation for User Story 5

- [X] T069 [US5] Implement `TransferSuggestion` model in `backend/src/domain/transfer_balance/models.py`
- [X] T070 [US5] Implement imbalance detection + feasibility-constrained transfer engine reading `StorePriorityProfile` in `backend/src/domain/transfer_balance/engine.py` (FR-008, FR-009, FR-020; uses the Foundational stub ranking from T022 until US8's full scoring service — T084 — is available)
- [X] T071 [US5] Implement `GET /v1/transfers/suggestions` and status-update endpoints in `backend/src/api/routers/transfers.py`
- [X] T072 [P] [US5] Build transfer suggestion list with feasibility/priority display and status actions in `frontend/src/features/transfer-balance/TransferSuggestions.tsx`
- [X] T073 [US5] Wire transfer-balance feature to API via TanStack Query hooks in `frontend/src/features/transfer-balance/hooks/useTransfers.ts`

**Checkpoint**: US1–US5 functional.

---

## Phase 8: User Story 7 - Manage Product Location Thresholds in an Admin Panel (Priority: P2)

**Goal**: Admin users manage product-location alert/replenishment thresholds.

**Independent Test**: Create and update product-location threshold settings, then verify the saved values are visible and influence downstream alert and recommendation behavior.

### Tests and Harness for User Story 7 (REQUIRED) ⚠️

- [X] T074 [P] [US7] Contract test `GET`/`POST /v1/admin/product-location-policies` (incl. 409 edit-lock, 422 validation) in `backend/tests/contract/test_policies.py`
- [X] T075 [P] [US7] Integration test threshold edit → lock-during-evaluation → apply-next-cycle journey in `backend/tests/integration/test_policy_edit_lock.py`
- [X] T076 [US7] Harness scenario — happy path (threshold saved and applied), failure path (invalid/incomplete values rejected), data-quality edge case (edit attempted during in-flight evaluation) in `backend/tests/harness/test_policy_harness.py`

### Implementation for User Story 7

- [X] T077 [US7] Implement threshold validation rules and edit-lock enforcement service in `backend/src/domain/alerting/policy_service.py` (FR-016, FR-017, FR-023)
- [X] T078 [US7] Implement `GET`/`POST /v1/admin/product-location-policies` endpoints with audit logging in `backend/src/api/routers/admin_policies.py` (FR-018)
- [X] T079 [P] [US7] Build admin threshold management panel with validation feedback and lock-state indicator in `frontend/src/features/admin/ProductLocationPolicyAdmin.tsx`
- [X] T080 [US7] Wire admin policy feature to API via TanStack Query hooks in `frontend/src/features/admin/hooks/usePolicies.ts`

**Checkpoint**: US1–US5, US7 functional.

---

## Phase 9: User Story 8 - Prioritize Stores for Item Restoration by Region and Consumption (Priority: P2)

**Goal**: Regional planners prioritize stores for restoration based on region and consumption patterns.

**Independent Test**: Provide multiple stores with different regions, consumption rates, and shortage conditions, then verify the resulting priority order used by restoration and transfer decisions.

### Tests and Harness for User Story 8 (REQUIRED) ⚠️

- [X] T081 [P] [US8] Contract test `GET /v1/store-priority/profiles` and `POST /v1/store-priority/rules` in `backend/tests/contract/test_store_priority.py`
- [X] T082 [P] [US8] Integration test region/consumption-based ranking journey in `backend/tests/integration/test_priority_ranking.py`
- [X] T083 [US8] Harness scenario — happy path (stores ranked by configured factors), failure path (missing consumption data), data-quality edge case (conflicting region/consumption signals) in `backend/tests/harness/test_priority_harness.py`

### Implementation for User Story 8

- [X] T084 [US8] Implement region-based and consumption-based priority scoring service in `backend/src/domain/transfer_balance/priority_service.py` (FR-019, FR-021)
- [X] T085 [US8] Implement `GET /v1/store-priority/profiles` and `POST /v1/store-priority/rules` endpoints in `backend/src/api/routers/store_priority.py` (FR-020)
- [X] T107 [US8] Implement MAF/Copilot SDK priority-factor explanation agent wrapper (explanation only, not the scoring decision) in `backend/src/agents/store_priority_explainer.py` (per research.md Agent orchestration decision)
- [X] T086 [P] [US8] Build store priority review view with contributing-factor breakdown in `frontend/src/features/transfer-balance/StorePriorityView.tsx`
- [X] T087 [US8] Wire store-priority feature to API via TanStack Query hooks in `frontend/src/features/transfer-balance/hooks/useStorePriority.ts`

**Checkpoint**: US1–US5, US7–US8 functional.

---

## Phase 10: User Story 6 - Operate with Analytics and Dashboards (Priority: P3)

**Goal**: Regional managers track inventory and replenishment KPIs through dashboards.

**Independent Test**: Load representative data and verify KPI widgets, filtering behavior, and trend summaries across operational views.

### Tests and Harness for User Story 6 (REQUIRED) ⚠️

- [X] T088 [P] [US6] Contract test `GET /v1/analytics/kpis` in `backend/tests/contract/test_kpis.py`
- [X] T089 [P] [US6] Integration test dashboard filter/aggregation journey in `backend/tests/integration/test_kpi_dashboard.py`
- [X] T090 [US6] Harness scenario — happy path (KPI widgets load), failure path (missing data window), data-quality edge case (partial aggregation) in `backend/tests/harness/test_analytics_harness.py`

### Implementation for User Story 6

- [X] T091 [US6] Implement `KPIView` model and aggregation service (fill-rate, aging, forecast/replenishment outcomes) in `backend/src/domain/analytics/service.py` (FR-010, FR-011)
- [X] T092 [US6] Implement `GET /v1/analytics/kpis` endpoint with region/store/category/time filters in `backend/src/api/routers/analytics.py`
- [X] T093 [P] [US6] Build KPI dashboard with high-risk item widgets and trend/exception summaries in `frontend/src/features/analytics/Dashboard.tsx`
- [X] T094 [US6] Wire analytics feature to API via TanStack Query hooks in `frontend/src/features/analytics/hooks/useKpis.ts`

**Checkpoint**: All 8 user stories independently functional.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T095 [P] Implement `GET /v1/admin/audit-log` endpoint in `backend/src/api/routers/admin_audit.py` (FR-014, FR-018)
- [X] T096 [P] Documentation updates cross-linking `docs/` to `specs/001-retail-replenishment-v1/`
- [X] T097 Code cleanup and refactoring pass across domain modules
- [X] T098 Performance validation against SC-001 (60s visibility), SC-003 (2-minute alerting), SC-007 (2-minute triage) targets
- [X] T099 [P] Additional backend unit tests for policy/threshold/rate-limit edge logic in `backend/tests/unit/`
- [X] T100 [P] Validate dashboard/admin/alert-worklist responsiveness and dark/light mode behavior (Playwright) in `frontend/tests/e2e/theme.spec.ts`
- [X] T101 [P] Validate structured logs/metrics/traces and RBAC/audit coverage across all domains
- [X] T102 Security hardening pass (RBAC enforcement, input validation, rate-limit abuse testing — OWASP Top 10 review)
- [X] T103 Run [quickstart.md](./quickstart.md) validation end-to-end
- [X] T104 Validate SC-009 (99.9% uptime design, zone-redundancy configuration) and SC-008 (cost guardrail dashboard against the $15,000/month ceiling and $0.00005/event assumption)
- [X] T108 [P] Run a WCAG 2.2 AA accessibility audit (automated axe-core scan in CI + manual review) across alerts, recommendations, approvals, and dashboards in `frontend/tests/e2e/accessibility.spec.ts` (Constitution IV)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phases 3–10)**: All depend on Foundational completion
  - P1 stories (US1, US2, US3) form the MVP and should be completed first
  - P2 stories (US4, US5, US7, US8) can proceed in parallel once Foundational is done
  - P3 story (US6) depends on data produced by US1–US5/US7/US8 for meaningful KPIs, but its own implementation is independently testable with representative seed data
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories — foundational read dependency for US2–US8
- **US2 (P1)**: Reads `ProductLocationPolicy` (Foundational) and `InventoryPosition` (US1) — independently testable with seeded data
- **US3 (P1)**: Reads `ProductLocationPolicy` (Foundational) and `InventoryPosition` (US1) — independently testable with seeded data
- **US4 (P2)**: Independently testable with seeded historical demand data
- **US5 (P2)**: Reads `StorePriorityProfile` (Foundational, refined by US8) — independently testable with seeded imbalance data
- **US7 (P2)**: Owns `ProductLocationPolicy` CRUD/admin surface consumed by US2/US3
- **US8 (P2)**: Owns `StorePriorityProfile` scoring/admin surface consumed by US5
- **US6 (P3)**: Reads aggregated data from US1–US5/US7/US8 for dashboards — independently testable with seeded data

### Within Each User Story

- Contract tests, integration tests, and harness scenarios MUST be written and FAIL before implementation
- Models before services; services before endpoints; backend endpoints before frontend wiring
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational completes, P1 stories (US1–US3) should be prioritized; P2 stories (US4, US5, US7, US8) can then run in parallel across team members
- All tests for a user story marked [P] can run in parallel
- Backend and frontend implementation tasks within a story marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1, Phase 4: US2, Phase 5: US3
4. **STOP and VALIDATE**: Run harness scenarios and quickstart.md for US1–US3 independently
5. Deploy/demo if ready (MVP)

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → US2 → US3 → Test independently after each → Deploy/Demo (MVP!)
3. US4, US5, US7, US8 (P2) → Test independently → Deploy/Demo
4. US6 (P3) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 → US2 (both P1, sequential due to shared inventory read dependency)
   - Developer B: US3 (P1, parallel to A once US1 models exist)
   - Developer C: US7 → US8 (owns policy/priority admin surfaces feeding US2/US3/US5)
   - Developer D: US4, US5 (P2)
3. US6 (P3) picked up once P1/P2 stories have produced data to visualize

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Every user story is independently completable and testable per its Independent Test criterion in [spec.md](./spec.md)
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence
