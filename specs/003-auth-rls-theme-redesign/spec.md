# Feature Specification: Authentication, Row-Level Security & Modern Theme Redesign

**Feature Branch**: `003-auth-rls-theme-redesign`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "1. Add login and logout functionality and RLS should be implemented 2. Overhaul the light/dark theme visual design system (background/card/navbar colors, indigo primary color, text hierarchy, borders, modern rounded table with sticky header and hover states, redesigned status badges, pill-style active navigation, Inter/Geist typography scale, redesigned primary/secondary buttons, KPI summary cards above tables, dark theme palette, consistent icon set for navigation, increased spacing/padding)."

## Clarifications

### Session 2026-08-01

- Q: Which session transport should authentication use? -> A: HttpOnly secure cookie session.
- Q: How should out-of-scope RLS requests be handled? -> A: Return 404 for record-level lookups; return 200 with filtered results for list endpoints.
- Q: How should role/scope assignment be resolved at request time? -> A: Resolve role/scope from server-side assignment storage on every request (or strictly invalidated short cache).
- Q: What failed-login safeguard should be enforced? -> A: Lock account for 30 minutes after 5 failed attempts within 15 minutes.
- Q: What password policy strength should be required? -> A: Minimum 12 characters with upper+lower+number+symbol, and deny common-compromised passwords.

## Constitution Alignment *(mandatory)*

- **Business Value Mapping**: US1-US2 (login/logout, row-level security) protect the retail replenishment platform's operational data — store managers, procurement officers, and regional managers must only authenticate as themselves and only see/act on data for stores they are accountable for, which is required before this platform can be trusted with real multi-store data. US3-US6 (theme redesign, KPI cards, iconography) raise operator trust and at-a-glance comprehension during demos, onboarding, and daily use, directly building on feature 002's design-token foundation.
- **Backend Standard**: Authentication, session handling, and row-level authorization checks are implemented in Python, as explicit domain services (`auth`/`identity` domain) separate from transport (API routers only orchestrate). No new agent workflows are required for this feature; existing Microsoft Agent Framework / Copilot SDK usage in replenishment/forecasting explainers is unaffected.
- **Harness Plan**: Harness/contract scenarios will cover: successful login issuing a valid session, failed login (wrong credentials) rejection, logout invalidating a session, unauthenticated access to protected endpoints being rejected, and row-level scoping enforcement (a user assigned to Store A cannot read or mutate Store B's inventory/alerts/recommendations/forecasts/transfers data even via direct API calls).
- **Frontend Experience**: A responsive login screen and an authenticated app shell (with logout control) are required, supporting both dark and light mode from day one. The theme redesign applies consistently across every existing dashboard/admin screen and remains responsive at existing breakpoints (mobile/tablet/desktop) established in feature 002.
- **Operational Readiness**: Login, logout, and RLS-denied access attempts are audit-logged (actor, timestamp, outcome) per the existing audit-log pattern. Session validation failures and authorization denials are structured, traceable events (not silent fallbacks).
- **Azure Architecture and Cost**: Reuses the existing backend/database/session infrastructure (no new managed services); session storage may reuse the existing cache layer already provisioned for the platform. No additional Azure resources are introduced by this feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Login and Logout (Priority: P1)

An operator (store manager, inventory manager, procurement officer, regional manager, or admin) opens the application and must log in with their credentials before reaching any dashboard. Once authenticated, they can work across the platform as themselves; when finished, they log out and their session immediately ends.

**Why this priority**: This is the foundational trust boundary for the entire platform — without real authentication, anyone can impersonate any role via the current placeholder identity headers. No other capability in this spec (or row-level security) is meaningful without it.

**Independent Test**: Can be fully tested by attempting to open any dashboard route while logged out (should be redirected to login), logging in with valid credentials (should reach the dashboard as that user), and logging out (should return to the login screen and block further authenticated actions).

**Acceptance Scenarios**:

1. **Given** a logged-out visitor, **When** they navigate directly to any dashboard URL, **Then** they are redirected to the login screen and see no protected data.
2. **Given** a user enters valid credentials on the login screen, **When** they submit, **Then** they are authenticated and taken to their landing dashboard.
3. **Given** a user enters invalid credentials, **When** they submit, **Then** they see a clear error message and remain on the login screen without being authenticated.
4. **Given** an authenticated user, **When** they select "logout", **Then** their session is invalidated and any subsequent request requires logging in again.
5. **Given** an authenticated user's session has expired or been invalidated, **When** they attempt any further action, **Then** they are prompted to log in again rather than seeing a silent failure.

---

### User Story 2 - Row-Level Security (Data Scoped to Assigned Stores) (Priority: P1)

Once authenticated, an operator only sees and can act on inventory positions, alerts, recommendations, forecasts, transfer suggestions, and store priority data for the store(s)/region(s) they are assigned to. Roles with broader accountability (e.g., regional manager, admin) see the appropriately wider scope defined by their assignment.

**Why this priority**: Without enforced row-level access boundaries, authentication alone still allows any logged-in user to view or modify another store's operational data, which is unacceptable for a real multi-store retail deployment — this is equally foundational as login itself.

**Independent Test**: Can be fully tested by logging in as a user scoped to Store A and confirming that Store B's records are absent from every list view and rejected on direct access (by ID) via both the UI and the API, while Store A's own data remains fully visible and actionable.

**Acceptance Scenarios**:

1. **Given** a store manager assigned only to Store A, **When** they view the inventory, alerts, replenishment, forecasting, or transfer screens, **Then** only Store A's records are shown.
2. **Given** a store manager assigned only to Store A, **When** they attempt to view or modify a record belonging to Store B (e.g., via a direct link or API call), **Then** the action is denied and no Store B data is revealed.
3. **Given** a regional manager assigned to a region containing multiple stores, **When** they view any dashboard, **Then** they see data for every store in their assigned region, and no stores outside it.
4. **Given** an admin user, **When** they view any dashboard or admin screen, **Then** they see data across all stores, consistent with the admin role's existing platform-wide responsibilities.
5. **Given** a transfer suggestion spanning two stores, **When** a user scoped to only one of those stores views it, **Then** the system only exposes the fields relevant to determining whether that transfer affects their own store, not full unrelated detail about the other store.

---

### User Story 3 - Refreshed Light Theme Visual System (Priority: P2)

Every dashboard, table, form, and admin screen adopts the new light-theme visual language: a soft neutral background instead of pure white, an indigo primary color for active states/buttons/links, a clear text hierarchy (heading/body/muted/disabled), softer borders, rounded card containers with subtle shadows, a modern table style (sticky header, comfortable row height, hover highlighting), redesigned status badges (colored pill with border), pill-style active navigation, an updated type scale, and increased spacing/padding throughout.

**Why this priority**: This directly fulfills the stakeholder's detailed visual design brief and is the most visible day-to-day improvement to operator experience, but it depends on login/RLS being in place first so the redesigned screens are seen by properly authenticated, properly scoped users.

**Independent Test**: Can be fully tested by visually and programmatically inspecting every in-scope screen in light mode and confirming the background, card, table, badge, navigation, button, and typography treatments match the specified design tokens, with no screen left using the old flat/plain styling.

**Acceptance Scenarios**:

1. **Given** any dashboard screen in light mode, **When** it renders, **Then** the page background is the soft neutral tone (not pure white) while cards/tables use the white card surface with a rounded, subtly-shadowed container.
2. **Given** any data table, **When** the user scrolls or hovers a row, **Then** the header stays visible (sticky) and the hovered row is subtly highlighted.
3. **Given** a status indicator (e.g., "Fresh", "Low Stock"), **When** it is displayed, **Then** it renders as a colored, bordered, rounded pill badge rather than a plain colored dot or flat label.
4. **Given** the primary navigation, **When** a section is active, **Then** it is shown as a rounded, indigo-tinted pill distinct from inactive and hovered items.
5. **Given** any primary action button, **When** displayed, **Then** it uses the indigo primary color treatment with the specified hover state and corner rounding.

---

### User Story 4 - Dark Theme Parity (Priority: P2)

Every screen that supports the new light theme also supports a matching dark theme using the specified dark palette (background, surface, card, border, text, and primary colors), preserving the same layout, hierarchy, and readability as light mode.

**Why this priority**: Dark mode is an existing platform requirement (constitution: responsive, dark/light mode support); the redesign must not regress or leave dark mode visually inconsistent with the new light theme.

**Independent Test**: Can be fully tested by toggling dark mode on every in-scope screen and confirming all redesigned elements (cards, tables, badges, navigation, buttons, KPI cards) render using the dark palette with no leftover light-only styling and no readability regressions.

**Acceptance Scenarios**:

1. **Given** a user with dark mode enabled, **When** they view any screen, **Then** background, surface, card, and border colors match the specified dark palette.
2. **Given** dark mode is active, **When** the user views text at any hierarchy level (heading/body/secondary), **Then** contrast remains readable and meets accessibility contrast guidelines.
3. **Given** a user toggles between light and dark mode, **When** the switch happens, **Then** every redesigned component (tables, badges, nav, buttons, KPI cards) updates consistently with no mismatched or unstyled elements.

---

### User Story 5 - At-a-Glance KPI Summary Cards (Priority: P3)

Dashboard-style screens show a row of KPI summary cards (e.g., total SKUs, freshness percentage, low-stock count, transfer count) above the detailed data table, so operators can assess overall status before drilling into details.

**Why this priority**: This is a valuable at-a-glance improvement called out explicitly by the stakeholder, but it is additive to (and depends on) the underlying data and redesigned table already being in place.

**Independent Test**: Can be fully tested by loading a dashboard screen and confirming summary KPI cards appear above the table, showing values consistent with the underlying (row-level-scoped) data set.

**Acceptance Scenarios**:

1. **Given** a dashboard screen with underlying data, **When** it loads, **Then** KPI summary cards appear above the detail table showing relevant aggregate figures (e.g., total SKU count, freshness percentage, low-stock count, transfer count).
2. **Given** the underlying data changes (e.g., after a transfer is approved), **When** the screen is refreshed, **Then** the KPI cards reflect the updated figures.
3. **Given** a user with restricted row-level scope, **When** they view KPI cards, **Then** the figures reflect only the data within their scope, consistent with User Story 2.

---

### User Story 6 - Consistent Iconography in Navigation (Priority: P3)

Primary navigation items (Inventory, Alerts, Replenishment, Forecasts, Transfers, Store Priority, Analytics, Admin) each display a consistent icon alongside their label, instead of plain text or ad hoc emoji.

**Why this priority**: This is a smaller polish item that improves scanability but has the least functional impact of the requested changes.

**Independent Test**: Can be fully tested by inspecting the navigation on any screen and confirming every item has an icon from the same consistent icon set, paired with its text label.

**Acceptance Scenarios**:

1. **Given** the primary navigation, **When** it renders, **Then** every navigation item shows an icon from a single consistent icon set next to its label.
2. **Given** the same navigation item, **When** viewed in light or dark mode, or active/inactive/hover state, **Then** its icon remains recognizable and consistent with the surrounding color treatment.

---

### Edge Cases

- What happens when a user's session expires while they are mid-edit (e.g., updating a threshold policy)? The system must reject the save with a clear "please log in again" outcome rather than silently discarding or misattributing the change.
- What happens when a user with no assigned store/region scope logs in? The system must show an explicit empty/no-access state rather than an error or another user's data.
- What happens when a user repeatedly submits incorrect login credentials? The system must apply a reasonable, industry-standard safeguard (e.g., temporary lockout/backoff) rather than allowing unlimited attempts.
- What happens when a regional manager's region is reassigned or a store manager's store assignment changes while they are logged in? Access must reflect the updated scope no later than their next request.
- How does the system behave if row-level scope data is missing/misconfigured for a user? Access must default to no data visibility rather than defaulting to full/unscoped access.
- How do KPI summary cards behave while their underlying data is still loading, or if it fails to load? They must show an explicit loading or error state, never a blank or stale-looking zero.
- How does the redesigned table handle very long SKU/location identifiers or a very large number of rows? The rounded/sticky-header/hover treatment must remain intact and the container must remain scrollable per the existing responsive table behavior.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication (Login/Logout)**

- **FR-001**: System MUST require every user to authenticate with credentials (identifier + password) before accessing any dashboard, admin, or data-returning API endpoint.
- **FR-001a**: System MUST enforce a password policy of minimum 12 characters including uppercase, lowercase, numeric, and symbol classes, and MUST reject known common-compromised passwords.
- **FR-002**: System MUST reject invalid credentials with a clear, generic error message that does not reveal whether the identifier or the password was incorrect.
- **FR-003**: System MUST issue a server-validated session identifier in an HttpOnly secure cookie upon successful authentication, and use that session to identify the user and their role/scope on subsequent requests, replacing reliance on client-supplied identity headers.
- **FR-004**: Users MUST be able to explicitly log out, which immediately invalidates their session so it cannot be reused for further authenticated actions.
- **FR-005**: System MUST reject any request to a protected endpoint that lacks a valid session, without leaking protected data in the response.
- **FR-006**: System MUST lock an account for 30 minutes after 5 failed login attempts within a rolling 15-minute window.
- **FR-006a**: System MUST return a generic lockout response during the lockout period without revealing whether the account identifier exists.
- **FR-007**: System MUST audit-log authentication events (login success, login failure, logout, session-invalid access attempts) with actor identifier, timestamp, and outcome.

**Row-Level Security (RLS)**

- **FR-008**: System MUST restrict every data-returning and data-mutating operation (inventory, alerts, replenishment recommendations, forecasts, transfer suggestions, store priority) to only the store(s)/region(s) the authenticated user is assigned to.
- **FR-009**: System MUST allow roles with broader accountability (regional manager, admin) to access the wider scope defined by their assignment (region-wide or platform-wide, respectively), without requiring per-store impersonation.
- **FR-010**: System MUST deny (not merely hide in the UI) any direct API request for a record outside the requesting user's assigned scope by returning 404 for record-level lookups, disclosing no data about the out-of-scope record.
- **FR-010a**: System MUST return 200 for list endpoints while filtering results to only in-scope records, never including out-of-scope rows.
- **FR-011**: System MUST default to no data access when a user's scope assignment is missing or misconfigured, rather than defaulting to unscoped/full access.
- **FR-012**: System MUST audit-log denied out-of-scope access attempts with actor, requested entity, and outcome.
- **FR-013**: System MUST reflect changes to a user's role/scope assignment no later than that user's next request after the change.
- **FR-013a**: System MUST resolve role/scope from server-side assignment storage on each request, or from a short-lived cache with strict invalidation semantics that guarantees FR-013.

**Visual Design System — Light Theme**

- **FR-014**: System MUST render the page background using a soft neutral tone (not pure white) and cards/tables/navbar using a white surface, across every in-scope screen.
- **FR-015**: System MUST use a single indigo primary color (with defined hover and light-tint variants) consistently for active navigation, primary buttons, links, selected rows, and focus states.
- **FR-016**: System MUST apply a defined text color hierarchy (heading, body, muted, disabled) consistently across all in-scope screens.
- **FR-017**: System MUST use softened, low-contrast borders in place of the current higher-contrast borders throughout tables, cards, and inputs.
- **FR-018**: System MUST render primary data tables with a sticky header, a comfortable row height, a subtle hover highlight per row, and a rounded container with a subtle shadow.
- **FR-019**: System MUST render status/severity indicators as colored, bordered, rounded pill badges (background/text/border color per status), replacing plain-colored dots or flat labels.
- **FR-020**: System MUST render primary navigation items with a distinct rounded "active" pill state, a distinct hover state, and a muted inactive state.
- **FR-021**: System MUST use a consistent modern typographic scale (page title, section title, table header, body, small text) and a consistent sans-serif typeface family across all in-scope screens.
- **FR-022**: System MUST render primary and secondary buttons with the specified color, hover, and corner-rounding treatment.
- **FR-023**: System MUST increase container padding, section spacing, table row height, and card padding relative to the current layout, consistently across in-scope screens.

**Visual Design System — Dark Theme**

- **FR-024**: System MUST provide a dark-theme palette (background, surface, card, border, primary, primary-hover, and primary/secondary text colors) that mirrors the light theme's structure and is available via the existing theme toggle.
- **FR-025**: System MUST apply the same redesigned component treatments (tables, badges, navigation, buttons, KPI cards) in dark mode as in light mode, using the dark palette instead of the light palette.
- **FR-026**: System MUST meet accessibility contrast guidelines (WCAG 2.2 AA) for text and status indicators in both light and dark themes after the redesign.

**KPI Summary Cards**

- **FR-027**: System MUST display a row of KPI summary cards above the primary data table on dashboard-style screens, showing at-a-glance aggregate figures relevant to that screen (e.g., total SKU count, freshness percentage, low-stock count, transfer count).
- **FR-028**: System MUST scope KPI summary figures to the viewing user's row-level access (per FR-008), so cards never reveal aggregate figures that include out-of-scope data.
- **FR-029**: System MUST show explicit loading and error states for KPI summary cards, consistent with the platform's existing loading/empty/error state conventions.

**Iconography**

- **FR-030**: System MUST display a consistent icon (from a single icon set) alongside every primary navigation item's text label, in place of plain text or emoji.

### Canonical Visual Token Reference

The following values are normative for FR-014 through FR-026 and FR-030:

| Token Group | Value(s) |
|---|---|
| Light background | `#F8FAFC` |
| Light surfaces (cards/table/navbar) | `#FFFFFF` |
| Navbar divider | `#E2E8F0` |
| Primary (light) | `#6366F1` |
| Primary hover (light) | `#4F46E5` |
| Primary tint (light) | `#EEF2FF` |
| Text heading/body/muted/disabled (light) | `#0F172A`, `#334155`, `#64748B`, `#94A3B8` |
| Borders (light) | `#E5E7EB` (preferred), `#EEF2F7` (alternate) |
| Table container | `border-radius: 16px`, `box-shadow: 0 1px 3px rgba(0,0,0,.06)` |
| Table row behavior | sticky header enabled, default row height target `56px` (with `52px` allowed only for explicitly documented dense-table variants), hover `background: #F8FAFC`, `transition: .2s` |
| Status badge (success example) | background `#DCFCE7`, text `#15803D`, border `#BBF7D0`, radius `999px`, padding `6px 12px` |
| Nav active/inactive/hover | active background `#EEF2FF`, active text `#4F46E5`; inactive text `#64748B`; hover background `#F1F5F9`; radius `10px` |
| Typography family | `Inter` or `Geist` |
| Typography sizes | page title `40`, section title `28`, table header `14`, body `15`, small `13` |
| Button primary | background `#6366F1`, hover `#4F46E5`, radius `10px` |
| Button secondary | background `#FFFFFF`, border `#E2E8F0` |
| Spacing targets | container padding `32px`, section gap `32px`, table row target `56px` (matching default table-row behavior), card padding `24px` |
| Dark background/surface/card | `#09090B`, `#18181B`, `#1F1F23` |
| Dark border/text | border `#27272A`; text primary `#FAFAFA`; text secondary `#A1A1AA` |
| Primary (dark) | `#818CF8` |
| Primary hover (dark) | `#6366F1` |

### Key Entities

- **User Account**: A real, authenticatable identity (credential identifier, hashed password, active/locked status) that replaces the current placeholder client-supplied identity; associated with exactly one existing role/scope assignment.
- **Session**: Represents a single authenticated login; tracks the associated user, creation time, and validity; invalidated on logout or expiry.
- **User Role Assignment** *(existing, extended)*: Maps a User Account to a role (store manager, inventory manager, procurement officer, regional manager, admin) and a location/region scope, which now drives both authorization and row-level data filtering.
- **KPI Summary**: A per-screen, per-scope aggregate figure set (e.g., total SKUs, freshness %, low-stock count, transfer count) computed from the same row-level-scoped data shown in the underlying table.
- **Design Token Set**: The named light/dark color, typography, and spacing values (background, surface, card, border, primary/hover/light, text hierarchy, status colors) applied consistently across all in-scope screens.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of attempts to reach a dashboard, admin, or data endpoint without a valid session are blocked and redirected to login, with zero protected data exposed in the response.
- **SC-002**: In testing across all in-scope data domains, 0 instances of a user viewing, exporting, or modifying data outside their assigned store/region scope are observed.
- **SC-003**: A user with valid credentials can log in and reach their landing dashboard in under 10 seconds under normal conditions.
- **SC-004**: Logging out immediately prevents any further authenticated action in the same session (verified with 0 successful post-logout actions in testing).
- **SC-005**: Every in-scope screen passes an automated WCAG 2.2 AA accessibility contrast check in both light and dark theme after the redesign, with 0 violations.
- **SC-006**: An operator can determine overall status for a dashboard area (e.g., how many items are low-stock) within 5 seconds of the page loading, without opening the detail table, using the KPI summary cards.
- **SC-007**: 100% of primary navigation items display a consistent icon paired with their label across every in-scope screen, in both themes.
- **SC-008**: 100% of in-scope screens (every existing dashboard and admin screen) visually reflect the new background, card, border, typography, table, badge, navigation, and button treatments — no screen remains on the old flat/plain styling.

## Assumptions

- Accounts are provisioned by administrators; there is no public self-service sign-up in v1 (consistent with this being an internal multi-store operations tool).
- Authentication uses a credential-identifier-plus-password model; single sign-on/federated identity and multi-factor authentication are out of scope for this v1 feature and can be layered in later without changing the row-level security model.
- Self-service "forgot password" flows are out of scope for v1; administrators can reset a user's credentials on request.
- Sessions use HttpOnly secure cookies and follow standard web session practices (valid until explicit logout or a standard inactivity-based expiry); exact expiry duration is an operational configuration detail, not a user-facing requirement.
- Row-level scoping reuses the platform's existing role/location-scope assignment concept (already present as `location_scope` on user role assignments), now enforced against a real authenticated identity instead of a client-supplied header.
- Role/scope authorization context is resolved from authoritative server-side assignment data on each request (or strictly invalidated short cache), rather than persisted as long-lived client-side claims.
- The existing placeholder client-supplied identity mechanism (`X-User-Id` / `X-User-Role` headers) is superseded by real authenticated sessions for all protected endpoints once this feature ships.
- The specific colors, typography scale, spacing values, table style, badge style, navigation style, and KPI card concept described by the stakeholder constitute the required design tokens and layout treatments for both light and dark themes, applied across every existing in-scope dashboard and admin screen (Inventory, Alerts, Replenishment, Forecasts, Transfers, Store Priority, Analytics, Admin).
- The specific icon library/technology used to achieve "a single consistent icon set" is an implementation detail left to the planning phase; the requirement is consistency, not a specific icon vendor.
- KPI summary cards are added to existing dashboard-style screens that already show aggregate-able tabular data (e.g., Inventory, Alerts, Transfers); screens without a natural aggregate concept are out of scope for KPI cards.
