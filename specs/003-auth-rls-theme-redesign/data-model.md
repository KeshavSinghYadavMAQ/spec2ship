# Data Model: Authentication, Row-Level Security & Modern Theme Redesign

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Research**: [research.md](./research.md)

## New Entities

### UserAccount (backend)

Authenticatable operator identity replacing placeholder request-header impersonation.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` (UUID, PK) | Internal stable account identifier |
| `login_identifier` | `str` (unique) | Username/email-like identifier used at login |
| `password_hash` | `str` | Strong one-way hash of current password |
| `is_active` | `bool` | Disabled accounts cannot authenticate |
| `locked_until` | `datetime \| null` | Account lockout expiry timestamp |
| `failed_attempt_count_window` | `int` | Count of failed attempts in current rolling window |
| `failed_attempt_window_started_at` | `datetime \| null` | Window anchor for lockout policy |
| `created_at` | `datetime` | Audit trail |
| `updated_at` | `datetime` | Audit trail |

**Validation/Rules**:
- Password policy (FR-001a): min 12 chars, upper/lower/number/symbol; reject common-compromised values.
- Lockout policy (FR-006): lock for 30 minutes after 5 failed attempts within rolling 15 minutes.
- Generic response semantics (FR-002/FR-006a): no account enumeration via error details.

### AuthSession (backend)

Server-side authenticated session bound to UserAccount and transported via HttpOnly secure cookie.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` (opaque random token or UUID, PK) | Session identifier value stored in cookie |
| `user_account_id` | `str` (FK -> UserAccount.id) | Authenticated principal |
| `created_at` | `datetime` | Session issuance time |
| `expires_at` | `datetime` | Session validity boundary |
| `revoked_at` | `datetime \| null` | Set on logout/invalidation |
| `last_seen_at` | `datetime` | Optional activity tracking |

**Validation/Rules**:
- Only non-revoked, unexpired sessions are valid (FR-003, FR-004, FR-005).
- Logout sets revocation state immediately (FR-004).

### AuthAuditEvent (logical; persisted through existing audit log)

Authentication and authorization security event record emitted through existing audit infrastructure.

| Field | Type | Notes |
|---|---|---|
| `event_type` | enum | `login_success`, `login_failure`, `lockout`, `logout`, `session_invalid`, `rls_denied` |
| `actor_user_id` | `str \| null` | Null when identity unknown during failed login |
| `target_entity` | `str \| null` | Optional requested resource for RLS deny |
| `occurred_at` | `datetime` | Event timestamp |
| `metadata` | `dict` | Non-sensitive operational context |

### KpiSummary (frontend/backed by APIs)

Per-screen scoped aggregate metrics displayed above detail tables.

| Field | Type | Notes |
|---|---|---|
| `key` | `str` | Metric key (`total_sku`, `fresh_pct`, `low_stock_count`, etc.) |
| `label` | `str` | Human-readable KPI label |
| `value` | `number \| string` | KPI value formatted for display |
| `delta` | `number \| null` | Optional trend signal |
| `status` | enum | `normal`, `warning`, `critical` for visual cue |

**Validation/Rules**:
- Must be computed only from in-scope rows per authenticated user (FR-028).
- Must expose loading/error state in UI layer (FR-029).

## Existing Entities Reused/Extended

- `UserRoleAssignment` (existing): authoritative role and `location_scope` source for RLS decisions (FR-013a).
- Existing domain entities (`InventoryPosition`, `StockAlert`, `ReplenishmentRecommendation`, `DemandForecast`, `TransferSuggestion`, `StorePriorityProfile`, policy/admin entities): now filtered and authorized by resolved scope.
- Existing `AuditLogEntry`: used for auth and RLS deny audit events.

## State Transitions

### Authentication Session Lifecycle

```text
[Logged Out]
  --(valid login)-> [Active Session]
  --(invalid login)-> [Logged Out]
  --(5 failures in 15m)-> [Locked 30m]

[Locked 30m]
  --(lockout period expires)-> [Logged Out]

[Active Session]
  --(logout)-> [Logged Out]
  --(session expires/revoked)-> [Logged Out]
```

### RLS Access Outcome

```text
[Authenticated Request]
  --(scope resolved, resource in scope)-> [Allowed]
  --(scope resolved, record endpoint out of scope)-> [404 Not Found]
  --(scope resolved, list endpoint)-> [200 with filtered rows]
  --(scope missing/misconfigured)-> [No data access / deny]
```

### UI Theme + KPI Interaction

```text
[Screen Load]
  -> [Theme tokens applied (light/dark)]
  -> [KPI loading state]
  -> [KPI resolved from scoped data] OR [KPI error state]
```
