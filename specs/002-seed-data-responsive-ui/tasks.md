# Tasks: Realistic Store Demo Data & Colorful Responsive Theming

**Input**: Design documents from `/specs/002-seed-data-responsive-ui/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests and Harness**: Test and harness tasks are REQUIRED. Every user story includes contract/integration tests and a harness scenario (happy path, failure path, data-quality/edge case) before implementation is considered complete.

**Organization**: Tasks are grouped by user story (US1–US4, per [spec.md](./spec.md)) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- File paths follow the Option 2 (web app) structure defined in [plan.md](./plan.md#project-structure)

## Path Conventions

- Backend: `backend/src/domain/sample_data/`, `backend/src/api/routers/admin_sample_data.py`, `backend/src/schemas/sample_data.py`, `backend/tests/{unit,integration,contract,harness}/sample_data/`
- Frontend: `frontend/src/theme/{tokens.ts,AppThemeProvider.tsx}`, `frontend/src/features/{inventory,alerting,replenishment,forecasting,transfer-balance,analytics,admin}/`, `frontend/src/components/`, `frontend/tests/{theme,integration,e2e/responsive}/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for this feature

- [X] T001 Create backend `sample_data` domain package: `backend/src/domain/sample_data/__init__.py` and `backend/tests/{unit,integration,contract,harness}/sample_data/` directories per [plan.md](./plan.md#project-structure)
- [X] T002 [P] Create frontend theme/testing scaffolding: `frontend/src/theme/tokens.ts` skeleton and `frontend/tests/theme/`, `frontend/tests/integration/`, `frontend/tests/e2e/responsive/` directories per [plan.md](./plan.md#project-structure)
- [X] T003 [P] Configure Playwright viewport projects (360px mobile minimum, 768px tablet, 1440px desktop) and `@axe-core/playwright` wiring in `frontend/playwright.config.ts`
- [X] T004 Establish backend harness scaffolding (fixtures for `APP_ENVIRONMENT` overrides, admin/non-admin test clients, fresh DB session) in `backend/tests/harness/sample_data/conftest.py`

**Checkpoint**: Tooling and scaffolding ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement `SampleDataSeedRecord` model + Alembic migration for the `sample_data_seed_records` ledger table in `backend/src/domain/sample_data/models.py` (per [data-model.md](./data-model.md)) — blocks US1
- [X] T006 [P] Implement the seed-record ledger repository (idempotent record-by-natural-key, query by `seed_batch_id`/`entity_type`, delete-by-entity) in `backend/src/domain/sample_data/ledger.py` — blocks US1
- [X] T007 [P] Implement the non-production + admin-role guard dependency (`require_non_production_admin`, extending `Settings.environment` and the existing `require_role(Role.ADMIN)`) in `backend/src/domain/sample_data/guards.py` (FR-004, FR-011) — blocks US1
- [X] T008 [P] Implement curated static reference pools (region/city codes, product categories/variants) and a deterministic, fixed-seed `random.Random`-based identifier generator in `backend/src/domain/sample_data/reference_data.py` (FR-001; [research.md](./research.md) #1) — blocks US1
- [X] T009 [P] Define `SeedRunSummary`/`ClearRunSummary` Pydantic schemas in `backend/src/schemas/sample_data.py` per [contracts/sample-data.yaml](./contracts/sample-data.yaml) — blocks US1
- [X] T010 [P] Generate a custom Fluent UI `BrandVariants` palette and wire `createLightTheme`/`createDarkTheme` in `frontend/src/theme/tokens.ts` ([research.md](./research.md) #5) — blocks US2, US3, US4
- [X] T011 [P] Add a semantic `statusTokens` map (`success`/`warning`/`danger`/`info`, each paired with an icon/text label) in `frontend/src/theme/tokens.ts` (FR-010) — blocks US2, US4
- [X] T012 Update `frontend/src/theme/AppThemeProvider.tsx` to consume the new `tokens.ts` themes in place of `webLightTheme`/`webDarkTheme` — blocks US2, US3, US4

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Explore the Platform with Realistic Multi-Store Sample Data (Priority: P1) 🎯 MVP

**Goal**: Admins can seed the environment with realistic, pilot-scale, fictitious retail data across every domain, safely re-run seeding, and explicitly clear all seeded data — all gated by role + non-production environment.

**Independent Test**: Trigger the sample-data seeding action in a non-production environment and verify every existing dashboard (inventory, alerts, replenishment, forecasting, transfers, analytics, admin) shows populated, realistic-looking records; then trigger clear and verify dashboards return to empty state.

### Tests and Harness for User Story 1 (REQUIRED) ⚠️

- [X] T013 [P] [US1] Contract test `POST /v1/admin/sample-data/seed` (incl. 403 for non-admin and for production environment) in `backend/tests/contract/test_admin_sample_data_seed.py`
- [X] T014 [P] [US1] Contract test `GET /v1/admin/sample-data/status` in `backend/tests/contract/test_admin_sample_data_status.py`
- [X] T015 [P] [US1] Contract test `DELETE /v1/admin/sample-data` (incl. 403 gate) in `backend/tests/contract/test_admin_sample_data_clear.py`
- [X] T016 [P] [US1] Integration test verifying seeding populates every domain (inventory positions, policies, alerts, recommendations, forecasts, transfer suggestions, store priority profiles) in `backend/tests/integration/test_sample_data_seed_coverage.py`
- [X] T017 [US1] Harness scenario — happy path (full seed + clear round-trip leaves no residue), failure path (interrupted seeding resumes without duplicates), data-quality edge case (seed/real-data identifier collision fails fast, FR-012) in `backend/tests/harness/sample_data/test_seed_harness.py`

### Implementation for User Story 1

- [X] T018 [US1] Implement `SampleDataSeedService.seed()` orchestrating per-store batched generation, delegating all writes to existing domain services (inventory, alerting, replenishment, forecasting, transfer_balance) and recording each write in the ledger in `backend/src/domain/sample_data/seed_service.py` (depends on T005-T009; FR-001, FR-002, FR-005)
- [X] T019 [US1] Implement fail-fast collision detection against pre-existing non-seed records in `SampleDataSeedService` (FR-012)
- [X] T020 [US1] Implement resumability: before each per-store batch, check the ledger and skip already-seeded stores/entities in `backend/src/domain/sample_data/seed_service.py` (FR-003)
- [X] T021 [US1] Implement `SampleDataClearService.clear()` deleting exactly the ledger-tracked records via existing domain services, leaving genuine non-seed data untouched, in `backend/src/domain/sample_data/clear_service.py` (FR-011)
- [X] T022 [US1] Implement `POST /v1/admin/sample-data/seed`, `GET /v1/admin/sample-data/status`, and `DELETE /v1/admin/sample-data` endpoints wired to the guard dependency (T007) in `backend/src/api/routers/admin_sample_data.py`
- [X] T023 [US1] Wire seed/clear actions to the existing audit log writer (`backend/src/domain/admin/audit.py`) for operational trustworthiness (Constitution V)
- [X] T024 [P] [US1] Build an admin "Sample Data" panel (seed button, run status, clear button) in `frontend/src/features/admin/SampleDataPanel.tsx`
- [X] T025 [US1] Wire the Sample Data panel to the API via TanStack Query hooks in `frontend/src/features/admin/hooks/useSampleData.ts`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Consistent, Colorful, Modern Visual Design Across the App (Priority: P1)

**Goal**: Every existing feature screen shares the same modern, colorful design system (palette, typography, spacing, iconography), with status/severity indicators distinguishable beyond color alone.

**Independent Test**: Visually audit every in-scope screen against the design tokens (palette, typography, spacing, iconography) and confirm consistent application without one-off styling.

### Tests and Harness for User Story 2 (REQUIRED) ⚠️

- [X] T026 [P] [US2] Unit test asserting in-scope feature components consume shared `tokens.ts` values (no hard-coded one-off colors) in `frontend/tests/theme/test_token_consistency.test.tsx`
- [X] T027 [P] [US2] Integration test verifying shared components (buttons, cards, status badges, charts) render consistent styles across two different feature screens in `frontend/tests/integration/test_shared_components_consistency.test.tsx`
- [X] T028 [US2] Harness scenario — happy path (palette/typography/spacing consistently applied across all in-scope screens), failure path (a screen still using default Fluent styling is flagged), edge case (status indicator distinguishable without color, FR-010) in `frontend/tests/e2e/responsive/test_visual_consistency_harness.spec.ts`

### Implementation for User Story 2

- [X] T029 [P] [US2] Apply design tokens to inventory feature screens in `frontend/src/features/inventory/`
- [X] T030 [P] [US2] Apply design tokens to alerting feature screens in `frontend/src/features/alerting/`
- [X] T031 [P] [US2] Apply design tokens to replenishment feature screens in `frontend/src/features/replenishment/`
- [X] T032 [P] [US2] Apply design tokens to forecasting feature screens in `frontend/src/features/forecasting/`
- [X] T033 [P] [US2] Apply design tokens to transfer-balance feature screens in `frontend/src/features/transfer-balance/`
- [X] T034 [P] [US2] Apply design tokens to analytics feature screens in `frontend/src/features/analytics/`
- [X] T035 [P] [US2] Apply design tokens to admin feature screens (including the new Sample Data panel from US1) in `frontend/src/features/admin/`
- [X] T036 [US2] Update shared UI primitives (buttons, cards, status badges, charts) to consume tokens and pair status color with an icon/text label in `frontend/src/components/` (FR-010)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Responsive Layouts Across Devices (Priority: P2)

**Goal**: Every in-scope screen adapts cleanly from a 360px-wide mobile viewport up through tablet and desktop widths, with no cut-off content or required horizontal scrolling for primary workflows.

**Independent Test**: Load each in-scope screen at 360px (mobile), 768px (tablet), and 1440px (desktop) and verify no cut-off content, overlapping elements, or required horizontal scrolling for primary workflows.

### Tests and Harness for User Story 3 (REQUIRED) ⚠️

- [X] T037 [P] [US3] Integration test verifying a primary workflow (e.g., alert triage) remains usable at 360px without horizontal scrolling in `frontend/tests/integration/test_responsive_primary_workflow.test.tsx`
- [X] T038 [US3] Harness scenario — happy path (360px/768px/1440px breakpoints render cleanly across all in-scope screens), failure path (data-dense analytics screen at 360px), edge case (table-to-card reflow at tablet width) in `frontend/tests/e2e/responsive/test_breakpoints_harness.spec.ts`

### Implementation for User Story 3

- [X] T039 [P] [US3] Add responsive layout rules (stacking/scrollable containers) to inventory and alerting screens in `frontend/src/features/inventory/`, `frontend/src/features/alerting/`
- [X] T040 [P] [US3] Add responsive layout rules to replenishment and forecasting screens in `frontend/src/features/replenishment/`, `frontend/src/features/forecasting/`
- [X] T041 [P] [US3] Add responsive layout rules to transfer-balance and analytics screens in `frontend/src/features/transfer-balance/`, `frontend/src/features/analytics/`
- [X] T042 [US3] Add responsive layout rules to admin screens (including the Sample Data panel) in `frontend/src/features/admin/`

**Checkpoint**: At this point, User Stories 1-3 should all work independently.

---

## Phase 6: User Story 4 - Reliable Dark/Light Theme Parity (Priority: P2)

**Goal**: Every in-scope screen, including the new colorful design and sample data, remains fully legible and WCAG AA-compliant in both dark and light themes, with the user's theme preference persisted.

**Independent Test**: Toggle between dark and light themes on every in-scope screen and verify there is no unreadable text, low-contrast element, or visual glitch; reload and confirm the preference persists.

### Tests and Harness for User Story 4 (REQUIRED) ⚠️

- [X] T043 [P] [US4] Integration test verifying the theme toggle preference persists across reload/new session in `frontend/tests/integration/test_theme_persistence.test.tsx`
- [X] T044 [US4] Harness scenario — happy path (WCAG AA contrast validated via axe-core in both themes across all in-scope screens), failure path (a low-contrast element is flagged), edge case (status indicator legible without color in both themes) in `frontend/tests/e2e/responsive/test_theme_parity_harness.spec.ts`

### Implementation for User Story 4

- [X] T045 [US4] Verify and adjust WCAG AA contrast for `brandVariants`/`statusTokens` in both themes in `frontend/src/theme/tokens.ts` (depends on T010, T011)
- [X] T046 [US4] Confirm theme-mode persistence (localStorage) and system-preference fallback continue to function correctly with the new tokens in `frontend/src/theme/AppThemeProvider.tsx`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T047 [P] Update cross-references in `specs/002-seed-data-responsive-ui/quickstart.md` if endpoint paths or breakpoint values changed during implementation
- [X] T048 Code cleanup and refactoring across `backend/src/domain/sample_data/` and `frontend/src/theme/`
- [X] T049 [P] Performance validation: pilot-scale seeding (1,000+ stores, 100,000+ SKUs) completes in under 30 minutes (SC-001, SC-006) in `backend/tests/harness/sample_data/test_seed_performance.py`
- [X] T050 [P] Performance validation: dashboards remain responsive (no unhandled slowdowns) at pilot-scale data volumes (SC-008) in `frontend/tests/e2e/responsive/test_scale_performance.spec.ts`
- [X] T051 [P] Additional unit tests for the reference-data generator and ledger repository in `backend/tests/unit/sample_data/`
- [ ] T052 [P] Final full-pass validation of dashboard responsiveness, visual consistency, and dark/light mode behavior across all in-scope screens (SC-007)
- [ ] T053 Security hardening: confirm 403/error responses from `admin_sample_data.py` never leak details distinguishing real vs. seed data beyond what's necessary
- [ ] T054 Run [quickstart.md](./quickstart.md) validation end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (backend seeding) and US2 (frontend design tokens) can proceed in parallel once Phase 2 is done — different codebases
  - US3 depends on US2's token/component work being in place for its own layout changes to be meaningful, but can start once Phase 2 completes if staffed separately
  - US4 depends on US2's token work (T010, T011) for contrast validation
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependency on other stories; fully backend-focused (plus one small admin UI panel)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) — no dependency on US1; independently testable via visual audit
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) — benefits from US2's token work being applied first to avoid rework, but is independently testable at the layout level
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) — depends on US2's `tokens.ts` (T010, T011) for contrast validation, but is independently testable

### Within Each User Story

- Contract tests, integration tests, and harness scenarios MUST be written and FAIL before implementation
- Models/ledger before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to the next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 and US2 can start in parallel (different codebases); US3 and US4 can follow once US2's tokens exist
- All tests for a user story marked [P] can run in parallel
- Feature-folder styling tasks within US2/US3 marked [P] can run in parallel (different directories)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test POST /v1/admin/sample-data/seed in backend/tests/contract/test_admin_sample_data_seed.py"
Task: "Contract test GET /v1/admin/sample-data/status in backend/tests/contract/test_admin_sample_data_status.py"
Task: "Contract test DELETE /v1/admin/sample-data in backend/tests/contract/test_admin_sample_data_clear.py"
Task: "Integration test for seed coverage across all domains in backend/tests/integration/test_sample_data_seed_coverage.py"
```

## Parallel Example: User Story 2

```bash
# Launch design-token application across feature folders together:
Task: "Apply design tokens to inventory feature screens in frontend/src/features/inventory/"
Task: "Apply design tokens to alerting feature screens in frontend/src/features/alerting/"
Task: "Apply design tokens to replenishment feature screens in frontend/src/features/replenishment/"
Task: "Apply design tokens to forecasting feature screens in frontend/src/features/forecasting/"
Task: "Apply design tokens to transfer-balance feature screens in frontend/src/features/transfer-balance/"
Task: "Apply design tokens to analytics feature screens in frontend/src/features/analytics/"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (sample-data seeding/clear) — deliver a populated demo environment
4. Complete Phase 4: User Story 2 (colorful, consistent design) — deliver the visual refresh
5. **STOP and VALIDATE**: Run US1's and US2's independent tests; demo the populated, restyled environment
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Seeded demo data available
3. Add User Story 2 → Test independently → Consistent colorful UI live
4. Add User Story 3 → Test independently → Responsive layouts validated
5. Add User Story 4 → Test independently → Theme parity validated
6. Each story adds value without breaking previous stories
