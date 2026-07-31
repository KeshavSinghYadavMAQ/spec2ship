# API Contracts: Retail Replenishment V1 Foundation

This directory documents the external interface contracts exposed by the backend to the React frontend and to
authorized integrations. The full machine-readable contract is [openapi.yaml](./openapi.yaml) (OpenAPI 3.0).

## Structure

- One tag per domain, matching `backend/src/domain/*` and the retail agent Capability Ownership Map:
  `inventory` (US1), `alerting` (US2, US7 admin thresholds), `replenishment` (US3), `forecasting` (US4),
  `transfer-balance` (US5, US8 store priority), `analytics` (US6), `admin` (RBAC/audit cross-cutting).
- All endpoints require an authenticated principal with a role from `UserRoleAssignment` (FR-013); role checks are
  enforced in the API layer before delegating to domain services (constitution: business logic stays out of
  transport layers, but authorization is a boundary concern).
- All mutating endpoints emit an audit log entry (FR-014, FR-018).
- Error responses use a consistent `ProblemDetail` shape (RFC 7807-style: `type`, `title`, `status`, `detail`,
  `errors[]`) so the frontend can render consistent error states.

## Versioning

- Contracts are versioned via the `/v1` path prefix. Breaking changes require a new prefix (`/v2`) per
  Constitution II ("API contracts MUST be explicitly versioned").

## Review Checklist

- [ ] Every functional requirement (FR-001 to FR-024) is reachable through at least one documented endpoint.
- [ ] Every mutating endpoint has an explicit request schema and validation error shape.
- [ ] Every list endpoint supports the filter dimensions required by its user story (e.g., region/store/SKU/time
      for analytics, FR-010).
