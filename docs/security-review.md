# Security Review (T102 — OWASP Top 10)

Point-in-time review of the retail replenishment v1 backend and frontend against the
OWASP Top 10 (2021), performed as part of Phase 11 polish. This is a design/code review
augmented with automated checks (`ruff`, `mypy --strict`, `pytest`), not a penetration
test or dependency scan run by a dedicated security tool — see "Residual risks" below for
what is intentionally out of scope for v1.

## A01:2021 – Broken Access Control

- All mutating (`POST`) endpoints now require an authenticated, role-bearing caller via
  `require_role(...)` (`backend/src/domain/admin/rbac.py`), resolved from the
  `X-User-Id` / `X-User-Role` request headers (a v1 placeholder for Azure AD-integrated
  auth per `research.md`; see the module docstring for the intended production
  replacement).
  - `POST /v1/admin/product-location-policies` — `admin` only.
  - `POST /v1/store-priority/rules` — `admin` or `regional_manager`.
  - `POST /v1/alerts/{alertId}/transition` — any of the five defined roles.
  - `POST /v1/replenishment/recommendations/{id}/decision` — any of the five defined roles.
  - `POST /v1/transfers/suggestions/{id}/status` — any of the five defined roles.
  - Missing/invalid headers now return `401`; an unrecognized role returns `403`.
- `POST /v1/inventory/events` intentionally has no per-user RBAC: it's a machine-to-machine
  ingestion endpoint from POS/warehouse systems, protected instead by
  `RateLimitMiddleware` (per-source-system throttling) — user-role RBAC does not apply to
  this integration surface.
- Read (`GET`) endpoints remain open to any caller in v1, matching the existing
  admin-policies/store-priority precedent — fine-grained per-role read restrictions are
  deferred to the business role-mapping exercise called out in spec.md's assumptions.
- **Residual risk**: `require_role(*Role)` on the alert/replenishment/transfer endpoints
  accepts *any* of the five defined roles rather than a narrower, action-specific subset,
  because spec.md explicitly defers precise role-to-action mapping to business definition
  before go-live. This closes the "anyone, unauthenticated" gap while avoiding inventing
  unspecified business rules.

## A02:2021 – Cryptographic Failures

- No secrets or credentials are logged; `configure_observability()` uses structured
  logging of domain fields only (see `backend/src/infrastructure/observability.py`).
- Database/queue/cache connection strings are sourced from environment configuration
  (`backend/src/infrastructure/config.py`) via `pydantic-settings`, never hard-coded.

## A03:2021 – Injection

- All database access goes through SQLAlchemy's ORM/Core query builder
  (`select(...)`, `session.execute(select(...))`); no raw string-interpolated SQL exists
  anywhere in `backend/src`. Confirmed via a repo-wide search for `.execute(` / f-string
  SQL patterns.
- No use of `eval`, `innerHTML`, or `dangerouslySetInnerHTML` in the frontend; React's
  default JSX escaping handles all user-supplied text (SKU IDs, override reasons,
  narration strings, etc.), so stored-XSS via those fields is not possible through normal
  rendering paths.

## A04:2021 – Insecure Design

- Deterministic policy logic (thresholds, reorder points, min/max) is kept separate from
  agent/LLM-driven explanation text (`backend/src/agents/*_explainer.py`), so an agent
  cannot alter a business decision — it only narrates a decision already computed by
  domain code. This matches the constitution's "agent reasoning enriches explanations,
  policy logic stays deterministic" principle.
- `PolicyService._validate` rejects negative thresholds and inconsistent
  min/max/threshold orderings before persistence (see
  `backend/tests/unit/test_policy_validation.py`).

## A05:2021 – Security Misconfiguration

- CORS (`backend/src/api/main.py`) is restricted to `settings.cors_allow_origins` (an
  explicit configured list), not a `"*"` wildcard, even though `allow_credentials=True`.
- Exception handlers return structured `ProblemDetail` bodies without stack traces or
  internal exception text for unhandled errors; validation errors surface only
  field/message pairs.
- `mypy --strict` and `ruff` are both clean (`mypy src` → 64 files, 0 issues), reducing the
  risk of type-confusion bugs reaching production.

## A06:2021 – Vulnerable and Outdated Components

- `npm audit --omit=dev` on the frontend reports **2 high-severity** advisories, both for
  `react-router`/`react-router-dom` 7.18.2 (GHSA-qwww-vcr4-c8h2, "RSC Mode CSRF Bypass").
  This app uses classic client-side `BrowserRouter` SPA mode (see `frontend/src/main.tsx`)
  and does **not** use React Router's RSC/framework server mode, so the vulnerable code
  path is not exercised. Documented as a residual risk rather than force-upgrading/
  downgrading, since the suggested fix (`npm audit fix --force`) would downgrade to
  `7.11.0`, a breaking change with no functional benefit given the vulnerability doesn't
  apply to this app's routing mode.
- Remaining `npm audit` findings (moderate/critical) are in devDependencies (Playwright,
  ESLint toolchain) that never ship to the production bundle.
- Recommendation for a follow-up: track the `react-router` advisory and upgrade once a
  patched 7.x/8.x release is available, rather than downgrading now.

## A07:2021 – Identification and Authentication Failures

- `get_current_user` (`backend/src/domain/admin/rbac.py`) rejects missing or unrecognized
  role headers with `401`. This is an explicit v1 placeholder for real Azure AD token
  validation (documented in the module docstring and `research.md`); production
  deployment must replace header-based identity with verified bearer tokens before this
  is safe against a spoofed `X-User-Id`/`X-User-Role` header from an untrusted client.
  **This is the most significant open item from this review** — it's a known,
  intentional placeholder, not an oversight.

## A08:2021 – Software and Data Integrity Failures

- No use of `pickle` or other insecure deserialization anywhere in the codebase.
- CI-equivalent local gates (`pytest`, `ruff`, `mypy --strict`, `tsc --noEmit`, `eslint`,
  Playwright) all pass before work is marked complete in `tasks.md`, reducing the risk of
  shipping broken/tampered code paths.

## A09:2021 – Security Logging and Monitoring Failures

- Structured logs, metrics, and traces are wired via `configure_observability()` and used
  throughout alert routing, inventory ingestion, and recommendation/transfer decisions.
- Every replenishment decision and transfer status change now writes an `AuditLogWriter`
  entry (`before`/`after` state, actor, timestamp) satisfying FR-014/FR-018's audit-trail
  requirement — see T101 for the fix that closed this gap for those two flows.
- `GET /v1/admin/audit-log` gives operators a read surface over the audit trail.

## A10:2021 – Server-Side Request Forgery (SSRF)

- No outbound HTTP requests to caller-supplied URLs exist anywhere in the backend; all
  outbound integrations (SQL, Redis, Service Bus) target fixed, configuration-driven
  endpoints, not user input. SSRF is not applicable to this codebase's current design.

## Summary of residual risks (not fixed in this pass, tracked for follow-up)

1. **Header-based identity is a placeholder, not real authentication.** Must be replaced
   with Azure AD-validated tokens before production go-live (A07).
2. **`react-router` GHSA-qwww-vcr4-c8h2`** — high severity per `npm audit`, but not
   exploitable in this app's SPA routing mode. Track for a future non-breaking upgrade
   (A06).
3. **Role-to-action mapping is intentionally broad** (any of the 5 roles) for alert/
   replenishment/transfer actions, pending a business-defined fine-grained mapping
   (A01).
