# Quickstart: Realistic Store Demo Data & Colorful Responsive Theming

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This quickstart validates the two independently testable capabilities delivered by this feature:
sample-data seeding/clear (US1) and the colorful, responsive, theme-consistent UI (US2-US4).

## Prerequisites

- Backend running locally per `specs/001-retail-replenishment-v1/quickstart.md` (FastAPI app,
  `APP_ENVIRONMENT` defaulted to `local`, which satisfies the non-production safeguard).
- Frontend running locally (`npm run dev` in `frontend/`).
- An `admin`-role identity for API calls, e.g. headers `X-User-Id: demo-admin` and
  `X-User-Role: admin` (per the existing v1 RBAC placeholder in
  `backend/src/domain/admin/rbac.py`).

## 1. Seed the environment

```powershell
curl -Method POST http://localhost:8000/v1/admin/sample-data/seed `
  -Headers @{ "X-User-Id" = "demo-admin"; "X-User-Role" = "admin" }
```

Expected: `202` with a `SeedRunSummary` (`seed_batch_id`, `status: "completed"` once finished,
`counts_by_entity_type` showing non-zero counts for locations, products, policies, inventory
positions, alerts, recommendations, forecasts, transfer suggestions, and store priority profiles).

Re-run the same command: expect the same summary shape with counts unchanged (no duplicates —
FR-003 idempotency).

## 2. Verify every dashboard is populated

Open the frontend and visit each existing feature screen (inventory, alerting, replenishment,
forecasting, transfers, analytics, admin). Expected: no empty states; every screen shows
realistic-looking, fictitious multi-store data (SC-002).

## 3. Clear the sample data

```powershell
curl -Method DELETE http://localhost:8000/v1/admin/sample-data `
  -Headers @{ "X-User-Id" = "demo-admin"; "X-User-Role" = "admin" }
```

Expected: `200` with a `ClearRunSummary` showing removed counts matching what was seeded. Re-visit
the dashboards: expected empty states return, and any genuine (non-seed) data created manually
before/after seeding remains untouched.

## 4. Verify the non-production safeguard

Set `APP_ENVIRONMENT=production` and repeat step 1. Expected: `403 Forbidden` `ProblemDetail`,
even when calling with a valid `admin` role (FR-004 defense-in-depth).

## 5. Verify the colorful, responsive, theme-consistent UI

1. Toggle the theme switch in the app header between light and dark. Expected: the preference
   persists across a page reload (FR-009), and every screen remains legible with no low-contrast
   text or broken visuals (FR-008).
2. Resize the browser to 360px (mobile, the minimum supported width), 768px (tablet), and 1440px
   (desktop) widths on each in-scope screen. Expected: no horizontal scrolling or clipped content
   for primary workflows (FR-007, SC-003).
3. Compare two different screens side-by-side. Expected: shared color palette, typography, and
   component styling (buttons, cards, status badges, charts) look and behave consistently
   (FR-006).
4. Inspect a status/severity indicator (e.g., an alert severity badge). Expected: distinguishable
   via icon or text label, not color alone (FR-010).

## Automated harness

- Backend: `pytest backend/tests/harness/sample_data` — covers idempotent re-seeding, resumption
  after a simulated partial failure, and the non-production/role gate failure paths.
- Frontend: `npx playwright test tests/e2e/responsive` — covers the three breakpoints (360px
  minimum mobile width, tablet, desktop) and axe-core WCAG AA contrast checks in both themes
  across all in-scope screens.
