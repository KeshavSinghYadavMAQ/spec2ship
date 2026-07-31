# Quickstart: Authentication, RLS, and UI Redesign

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This quickstart validates login/logout, row-level security, and the full theme redesign.

## Prerequisites

- Backend running locally from `backend/` (default non-production environment).
- Frontend running from `frontend/` (`npm run dev`).
- Test accounts provisioned with scoped role assignments:
  - `admin_demo` (admin, global scope)
  - `store_mgr_a` (store_manager scoped to Store A)
  - `regional_mgr_west` (regional scope)

## 1. Login and Session Cookie

```powershell
curl -i -X POST http://localhost:8000/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"identifier":"admin_demo","password":"<valid-password>"}'
```

Expected:
- `200 OK`
- `Set-Cookie` includes secure session cookie (HttpOnly)
- response body contains non-sensitive session/user summary

## 2. Access Protected Endpoint Without Session

```powershell
curl -i http://localhost:8000/v1/inventory/positions
```

Expected:
- unauthorized response (no protected data leaked)

## 3. Logout Invalidates Session

```powershell
curl -i -X POST http://localhost:8000/v1/auth/logout `
  -H "Cookie: <session-cookie-from-login>"
```

Expected:
- logout success
- repeating protected call with same cookie is rejected

## 4. Lockout Policy

Submit invalid credentials for the same identifier 5 times within 15 minutes.

Expected:
- lockout state applied for 30 minutes
- subsequent login attempts return generic lockout/failure message (no account existence leak)

## 5. RLS List Filtering and Record-Level 404

1. Login as `store_mgr_a`.
2. Call list endpoint (e.g., inventory/alerts/recommendations) with mixed-store data present.

Expected:
- `200` with only Store A rows.

3. Call record endpoint for known Store B record ID.

Expected:
- `404` with no out-of-scope record details.

## 6. Scope Change Reflects Next Request

1. While logged in as scoped user, update that user's assignment (admin action).
2. Repeat same list endpoint request.

Expected:
- results reflect new scope on next request (no re-login required).

## 7. UI Redesign Validation (All In-Scope Screens)

Visit all primary routes (Inventory, Alerts, Replenishment, Forecasts, Transfers, Store Priority, Analytics, Admin):

- Light theme uses soft background, white cards/tables/navbar, indigo primary states, muted border palette.
- Tables show sticky header, rounded container, subtle shadow, hover row state, and updated row height.
- Status badges are bordered rounded pills with semantic coloring and labels/icons.
- Navigation items show icons with active/inactive/hover pill states.
- KPI summary cards appear above table views where applicable.
- Spacing and typography reflect updated scale.

## 8. Dark Theme + Accessibility + Responsive

1. Toggle dark mode and repeat route pass.
2. Run responsive checks at 360/768/1440 widths.
3. Run accessibility harness.

Expected:
- visual parity in dark theme
- no horizontal overflow regressions
- WCAG 2.2 AA checks pass (axe-core)

## Automated Validation

- Backend:
  - `pytest backend/tests/contract/test_auth_endpoints.py backend/tests/contract/test_rls_inventory_contract.py`
  - `pytest backend/tests/integration/auth/test_rls_cross_domain.py backend/tests/integration/auth/test_kpi_scope_aggregation.py`
  - `pytest backend/tests/harness/auth_rls/test_auth_lifecycle_harness.py backend/tests/harness/auth_rls/test_rls_scope_refresh_harness.py backend/tests/harness/auth_rls/test_audit_observability_harness.py`
- Frontend:
  - `npm run test -- --run tests/integration/auth/test_login_guard.test.tsx tests/integration/auth/test_scope_filtered_views.test.tsx tests/integration/test_light_theme_components.test.tsx tests/integration/test_theme_parity_components.test.tsx tests/integration/test_kpi_cards.test.tsx tests/integration/test_navigation_icons.test.tsx`
  - `npx playwright test tests/e2e/responsive/test_light_theme_redesign.spec.ts tests/e2e/responsive/test_dark_theme_parity_accessibility.spec.ts tests/e2e/responsive/test_kpi_cards_consistency.spec.ts tests/e2e/responsive/test_navigation_iconography.spec.ts tests/e2e/responsive/test_login_latency_budget.spec.ts tests/e2e/responsive/test_kpi_time_to_comprehension.spec.ts`
