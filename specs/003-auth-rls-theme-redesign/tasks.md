# Tasks: Authentication, Row-Level Security & Modern Theme Redesign

**Input**: Design documents from `/specs/003-auth-rls-theme-redesign/`

**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/auth-rls-ui.yaml`, `quickstart.md`

**Tests and Harness**: Test and harness tasks are required. Every user story includes contract/integration/harness or e2e validation before completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature scaffolding and shared verification baselines.

- [X] T001 Create auth domain package scaffolding in `backend/src/domain/auth/__init__.py`
- [X] T002 Create auth API router scaffolding in `backend/src/api/routers/auth.py`
- [X] T003 [P] Create auth schema scaffolding in `backend/src/schemas/auth.py`
- [X] T004 [P] Create frontend auth feature scaffolding in `frontend/src/features/auth/LoginPage.tsx`
- [X] T005 [P] Create backend auth harness package in `backend/tests/harness/auth_rls/__init__.py`
- [X] T006 [P] Create frontend auth integration test package in `frontend/tests/integration/auth/test_login_guard.test.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before any user story implementation.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T007 Create authentication persistence migration for `user_accounts` and `auth_sessions` in `backend/src/infrastructure/migrations/versions/0004_auth_sessions_and_accounts.py`
- [X] T008 [P] Implement backend auth entities (`UserAccount`, `AuthSession`) in `backend/src/domain/auth/models.py`
- [X] T009 [P] Implement password policy and compromised-password check primitives in `backend/src/domain/auth/password_policy.py`
- [X] T010 Implement session and lockout business rules in `backend/src/domain/auth/service.py`
- [X] T011 [P] Implement authenticated-session dependency resolver in `backend/src/api/dependencies/auth_session.py`
- [X] T012 Update RBAC identity source to authenticated session context in `backend/src/domain/admin/rbac.py`
- [X] T013 Wire auth router and session middleware/CORS cookie settings in `backend/src/api/main.py`
- [X] T014 [P] Implement authoritative per-request scope resolution service in `backend/src/domain/security/scope_service.py`
- [X] T015 [P] Add structured auth/RLS audit event helpers in `backend/src/domain/admin/audit.py`
- [X] T016 [P] Add frontend auth API client methods (login/logout/session) in `frontend/src/services/authClient.ts`
- [X] T017 [P] Add frontend auth guard shell component in `frontend/src/components/AuthGuard.tsx`
- [X] T018 Configure protected route composition for authenticated shell in `frontend/src/app/App.tsx`
- [X] T019 Add baseline contract harness registration for auth/RLS suite in `backend/tests/contract/test_auth_contract_smoke.py`
- [X] T020 Add baseline e2e smoke for redirected unauthenticated route access in `frontend/tests/e2e/responsive/test_auth_redirect_smoke.spec.ts`

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Secure Login and Logout (Priority: P1) MVP

**Goal**: Deliver real login/logout with secure HttpOnly cookie sessions and lockout handling.

**Independent Test**: Logged-out user is redirected to login; valid login opens app; logout invalidates session; lockout is enforced after repeated failures.

### Tests and Harness for User Story 1

- [X] T021 [P] [US1] Add auth endpoint contract tests for `/auth/login`, `/auth/logout`, `/auth/session` in `backend/tests/contract/test_auth_endpoints.py`
- [X] T022 [P] [US1] Add auth service unit tests (password policy, lockout window, session issuance) in `backend/tests/unit/auth/test_auth_service.py`
- [X] T023 [US1] Add login/logout/session lifecycle harness scenario in `backend/tests/harness/auth_rls/test_auth_lifecycle_harness.py`
- [X] T024 [P] [US1] Add frontend login route guard integration tests in `frontend/tests/integration/auth/test_login_guard.test.tsx`
- [X] T025 [US1] Add frontend e2e login/logout journey test in `frontend/tests/e2e/responsive/test_auth_login_logout.spec.ts`

### Implementation for User Story 1

- [X] T026 [US1] Implement login endpoint request validation and generic failure responses in `backend/src/api/routers/auth.py`
- [X] T027 [US1] Implement logout endpoint and session revocation behavior in `backend/src/api/routers/auth.py`
- [X] T028 [US1] Implement session status endpoint in `backend/src/api/routers/auth.py`
- [X] T029 [US1] Implement account lockout counter updates and unlock timing in `backend/src/domain/auth/service.py`
- [X] T030 [US1] Implement login UI form, error states, and submit flow in `frontend/src/features/auth/LoginPage.tsx`
- [X] T031 [US1] Integrate auth state bootstrap and logout action in app shell in `frontend/src/app/App.tsx`
- [X] T032 [US1] Add auth audit logging calls for success/failure/logout/session-invalid in `backend/src/domain/auth/service.py`

**Checkpoint**: User Story 1 complete and independently testable.

---

## Phase 4: User Story 2 - Row-Level Security Across Domain Data (Priority: P1)

**Goal**: Enforce server-side RLS for all in-scope domains with list filtering and record-level 404 semantics.

**Independent Test**: Scoped user sees only in-scope rows; out-of-scope record fetches return 404; scope changes take effect on next request.

### Tests and Harness for User Story 2

- [X] T033 [P] [US2] Add RLS contract tests for list filtering and record-level 404 behavior in `backend/tests/contract/test_rls_inventory_contract.py`
- [X] T034 [P] [US2] Add cross-domain RLS integration tests (alerts/replenishment/forecast/transfers/priority) in `backend/tests/integration/auth/test_rls_cross_domain.py`
- [X] T035 [US2] Add RLS scope-change-next-request harness scenario in `backend/tests/harness/auth_rls/test_rls_scope_refresh_harness.py`
- [X] T036 [P] [US2] Add frontend scoped-data rendering integration tests for role/scope personas in `frontend/tests/integration/auth/test_scope_filtered_views.test.tsx`

### Implementation for User Story 2

- [X] T037 [US2] Implement scope lookup and cache invalidation policy in `backend/src/domain/security/scope_service.py`
- [X] T038 [US2] Apply RLS filtering to inventory query paths in `backend/src/domain/inventory/models.py`
- [X] T039 [US2] Apply RLS filtering to alerting query/transition paths in `backend/src/domain/alerting/models.py`
- [X] T040 [US2] Apply RLS filtering to replenishment query/review paths in `backend/src/domain/replenishment/models.py`
- [X] T041 [US2] Apply RLS filtering to forecasting query paths in `backend/src/domain/forecasting/models.py`
- [X] T042 [US2] Apply RLS filtering to transfer/priority query paths in `backend/src/domain/transfer_balance/models.py`
- [X] T043 [US2] Enforce record-level out-of-scope 404 response mapping in API routers in `backend/src/api/main.py`
- [X] T044 [US2] Add RLS-denied audit logging for out-of-scope attempts in `backend/src/domain/admin/audit.py`
- [X] T045 [US2] Remove client-controlled identity headers from frontend service calls in `frontend/src/services/apiClient.ts`

**Checkpoint**: User Story 2 complete and independently testable.

---

## Phase 5: User Story 3 - Refreshed Light Theme Visual System (Priority: P2)

**Goal**: Apply the specified light-theme palette, typography, spacing, tables, badges, nav pills, and buttons across all in-scope screens.

**Independent Test**: Every in-scope screen renders with new light-theme tokens and interaction states, with no legacy flat/plain styling left.

### Tests and Harness for User Story 3

- [X] T046 [P] [US3] Add token regression tests for light-theme color/spacing/typography requirements in `frontend/tests/theme/test_light_theme_tokens.test.tsx`
- [X] T047 [P] [US3] Add component integration tests for nav-pill, button, and table-state styles in `frontend/tests/integration/test_light_theme_components.test.tsx`
- [X] T048 [US3] Add e2e visual consistency harness for redesigned light-theme surfaces in `frontend/tests/e2e/responsive/test_light_theme_redesign.spec.ts`

### Implementation for User Story 3

- [X] T049 [US3] Implement requested light-theme token palette and typography scale in `frontend/src/theme/tokens.ts`
- [X] T050 [US3] Apply updated typography and spacing tokens at provider level in `frontend/src/theme/AppThemeProvider.tsx`
- [X] T051 [US3] Implement reusable icon+pill navigation item component in `frontend/src/components/NavItem.tsx`
- [X] T052 [US3] Implement redesigned bordered-pill status badge styling in `frontend/src/components/StatusBadge.tsx`
- [X] T053 [US3] Implement rounded sticky-header table container with hover states in `frontend/src/components/ScrollableTableContainer.tsx`
- [X] T054 [US3] Apply redesigned navigation shell, spacing, and button styles in `frontend/src/app/App.tsx`
- [X] T055 [US3] Apply light-theme redesign styles to inventory and alerts views in `frontend/src/features/inventory/InventoryPositionView.tsx` and `frontend/src/features/alerting/AlertWorklist.tsx`
- [X] T056 [US3] Apply light-theme redesign styles to replenishment and forecasting views in `frontend/src/features/replenishment/RecommendationPanel.tsx` and `frontend/src/features/forecasting/ForecastView.tsx`
- [X] T057 [US3] Apply light-theme redesign styles to transfer and store-priority views in `frontend/src/features/transfer-balance/TransferSuggestions.tsx` and `frontend/src/features/transfer-balance/StorePriorityView.tsx`
- [X] T058 [US3] Apply light-theme redesign styles to analytics and admin views in `frontend/src/features/analytics/Dashboard.tsx`, `frontend/src/features/admin/ProductLocationPolicyAdmin.tsx`, and `frontend/src/features/admin/SampleDataPanel.tsx`

**Checkpoint**: User Story 3 complete and independently testable.

---

## Phase 6: User Story 4 - Dark Theme Parity (Priority: P2)

**Goal**: Deliver equivalent redesigned experience in dark mode with WCAG 2.2 AA contrast conformance.

**Independent Test**: Theme toggle switches all redesigned components to dark palette consistently with no contrast regressions.

### Tests and Harness for User Story 4

- [X] T059 [P] [US4] Add dark-theme token and contrast unit tests for key semantic tokens in `frontend/tests/theme/test_dark_theme_tokens.test.tsx`
- [X] T060 [P] [US4] Add dual-theme parity integration tests for shared components in `frontend/tests/integration/test_theme_parity_components.test.tsx`
- [X] T061 [US4] Add axe-core dual-theme accessibility harness across all in-scope routes in `frontend/tests/e2e/responsive/test_dark_theme_parity_accessibility.spec.ts`

### Implementation for User Story 4

- [X] T062 [US4] Implement requested dark-theme palette tokens in `frontend/src/theme/tokens.ts`
- [X] T063 [US4] Ensure all redesigned components consume semantic tokens (no hardcoded theme values) in `frontend/src/components/StatusBadge.tsx`
- [X] T064 [US4] Ensure app-level theme toggle applies redesigned dark tokens to all nav/surface elements in `frontend/src/theme/AppThemeProvider.tsx`

**Checkpoint**: User Story 4 complete and independently testable.

---

## Phase 7: User Story 5 - KPI Summary Cards Above Detail Tables (Priority: P3)

**Goal**: Add at-a-glance KPI cards per dashboard surface, scoped by RLS and synchronized with underlying data.

**Independent Test**: KPI cards render above detail tables with correct scoped values, loading, and error states.

### Tests and Harness for User Story 5

- [X] T065 [P] [US5] Add backend KPI-scope integration tests to verify aggregates are RLS-filtered in `backend/tests/integration/auth/test_kpi_scope_aggregation.py`
- [X] T066 [P] [US5] Add frontend KPI card loading/error/value integration tests in `frontend/tests/integration/test_kpi_cards.test.tsx`
- [X] T067 [US5] Add e2e KPI consistency harness comparing cards vs table data in `frontend/tests/e2e/responsive/test_kpi_cards_consistency.spec.ts`

### Implementation for User Story 5

- [X] T068 [US5] Implement reusable KPI card component in `frontend/src/components/KpiCard.tsx`
- [X] T069 [US5] Add inventory KPI summary computation hook in `frontend/src/features/inventory/hooks/useInventoryKpis.ts`
- [X] T070 [US5] Add alerting KPI summary computation hook in `frontend/src/features/alerting/hooks/useAlertKpis.ts`
- [X] T071 [US5] Add transfer KPI summary computation hook in `frontend/src/features/transfer-balance/hooks/useTransferKpis.ts`
- [X] T072 [US5] Render KPI card rows above inventory/alerts/transfers tables in `frontend/src/features/inventory/InventoryPositionView.tsx`, `frontend/src/features/alerting/AlertWorklist.tsx`, and `frontend/src/features/transfer-balance/TransferSuggestions.tsx`

**Checkpoint**: User Story 5 complete and independently testable.

---

## Phase 8: User Story 6 - Consistent Navigation Iconography (Priority: P3)

**Goal**: Ensure all primary navigation items include consistent icons and preserve readability in all states/themes.

**Independent Test**: Every primary nav entry displays a consistent icon with text in active/inactive/hover states across light and dark themes.

### Tests and Harness for User Story 6

- [X] T073 [P] [US6] Add navigation icon coverage test for all in-scope destinations in `frontend/tests/integration/test_navigation_icons.test.tsx`
- [X] T074 [US6] Add e2e navigation scanability harness across themes and breakpoints in `frontend/tests/e2e/responsive/test_navigation_iconography.spec.ts`

### Implementation for User Story 6

- [X] T075 [US6] Define canonical navigation icon mapping in `frontend/src/app/navigation.ts`
- [X] T076 [US6] Apply canonical icon mapping to app navigation rendering in `frontend/src/app/App.tsx`
- [X] T077 [US6] Ensure icon state styling parity for active/inactive/hover in `frontend/src/components/NavItem.tsx`

**Checkpoint**: User Story 6 complete and independently testable.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and validation across stories.

- [X] T078 [P] Update feature documentation and quickstart steps in `specs/003-auth-rls-theme-redesign/quickstart.md`
- [X] T079 Perform backend auth/RLS code cleanup and refactoring in `backend/src/domain/auth/service.py`
- [X] T080 [P] Add additional auth/session edge-case unit tests in `backend/tests/unit/auth/test_auth_edge_cases.py`
- [X] T081 [P] Run full frontend responsiveness and dark/light parity suite in `frontend/tests/e2e/responsive/test_dark_theme_parity_accessibility.spec.ts`
- [X] T082 [P] Validate auth and RLS observability/audit events for login, logout, lockout, and denied access in `backend/tests/harness/auth_rls/test_audit_observability_harness.py`
- [X] T083 Security hardening pass for cookie/session settings and generic auth errors in `backend/src/api/routers/auth.py`
- [X] T084 Run end-to-end quickstart validation in `specs/003-auth-rls-theme-redesign/quickstart.md`
- [X] T085 [P] Validate SC-003 login-to-dashboard latency (<10s) with an executable e2e timing harness in `frontend/tests/e2e/responsive/test_login_latency_budget.spec.ts`
- [X] T086 [P] Validate SC-006 time-to-comprehension (<=5s using KPI cards) with a scripted usability/performance harness in `frontend/tests/e2e/responsive/test_kpi_time_to_comprehension.spec.ts`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Stories (Phase 3-8)**: Depend on Foundational completion.
  - US1 and US2 should be completed first (both P1 security-critical).
  - US3 and US4 follow after core auth/RLS is stable.
  - US5 and US6 follow after redesign primitives are in place.
- **Polish (Phase 9)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on other stories.
- **US2 (P1)**: Starts after Phase 2; functionally depends on US1 session identity being available.
- **US3 (P2)**: Starts after Phase 2; should consume stabilized auth shell routes from US1.
- **US4 (P2)**: Depends on US3 token/component redesign completion.
- **US5 (P3)**: Depends on US2 scoped data semantics and US3 component primitives.
- **US6 (P3)**: Depends on US3 navigation component baseline.

### Within Each User Story

- Tests and harness tasks first, and failing before implementation.
- Core models/services before API wiring.
- Shared UI components before feature-surface integrations.
- Story-level checkpoint validation before moving to the next priority.

### Parallel Opportunities

- Phase 1 tasks marked [P] can run concurrently.
- Phase 2 tasks marked [P] can run in parallel with migration/service split work.
- Within each user story, [P] tests and independent component/model tasks can run in parallel.
- After Phase 2, frontend redesign work (US3/US4) and backend RLS coverage extensions (US2) can be staffed in parallel once US1 API contract is stable.

---

## Parallel Example: User Story 1

```bash
# Parallel tests
T021 backend/tests/contract/test_auth_endpoints.py
T022 backend/tests/unit/auth/test_auth_service.py
T024 frontend/tests/integration/auth/test_login_guard.test.tsx

# Parallel implementation slices
T026 backend/src/api/routers/auth.py
T030 frontend/src/features/auth/LoginPage.tsx
T032 backend/src/domain/auth/service.py
```

## Parallel Example: User Story 2

```bash
# Parallel domain RLS enforcement work
T038 backend/src/domain/inventory/models.py
T039 backend/src/domain/alerting/models.py
T040 backend/src/domain/replenishment/models.py
T041 backend/src/domain/forecasting/models.py
T042 backend/src/domain/transfer_balance/models.py
```

## Parallel Example: User Story 3

```bash
# Parallel design-system updates
T051 frontend/src/components/NavItem.tsx
T052 frontend/src/components/StatusBadge.tsx
T053 frontend/src/components/ScrollableTableContainer.tsx
T049 frontend/src/theme/tokens.ts
```

## Parallel Example: User Story 4

```bash
# Parallel validation passes
T059 frontend/tests/theme/test_dark_theme_tokens.test.tsx
T060 frontend/tests/integration/test_theme_parity_components.test.tsx
T061 frontend/tests/e2e/responsive/test_dark_theme_parity_accessibility.spec.ts
```

## Parallel Example: User Story 5

```bash
# Parallel KPI hooks
T069 frontend/src/features/inventory/hooks/useInventoryKpis.ts
T070 frontend/src/features/alerting/hooks/useAlertKpis.ts
T071 frontend/src/features/transfer-balance/hooks/useTransferKpis.ts
```

## Parallel Example: User Story 6

```bash
# Parallel nav icon verification and implementation
T073 frontend/tests/integration/test_navigation_icons.test.tsx
T075 frontend/src/app/navigation.ts
T077 frontend/src/components/NavItem.tsx
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1 and Phase 2.
2. Deliver US1 login/logout/session and validate independently.
3. Deliver US2 RLS filtering + 404 semantics and validate independently.
4. Demo secure authenticated + scoped platform behavior.

### Incremental Delivery

1. Add US3 light-theme redesign baseline.
2. Add US4 dark-theme parity and WCAG validation.
3. Add US5 KPI cards scoped by RLS.
4. Add US6 navigation icon consistency.
5. Finish Phase 9 polish and end-to-end quickstart validation.

### Parallel Team Strategy

1. Core backend team: Phase 2, US1, US2.
2. Frontend design-system team: US3, US4.
3. UX data team: US5 KPI overlays.
4. Shared QA/automation: Harness and e2e suites per phase.

---

## Notes

- `[P]` tasks indicate no file-level dependency conflicts.
- `[USx]` labels map tasks to specific user story scope for traceability.
- Every user story includes executable validation tasks before implementation closeout.
- Avoid cross-story leakage: complete and validate each story checkpoint independently.
