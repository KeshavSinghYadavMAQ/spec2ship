# Research: Authentication, Row-Level Security & Modern Theme Redesign

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This document resolves all technical unknowns from the plan's Technical Context. No `NEEDS CLARIFICATION` markers remain.

## 1. Session transport and server trust boundary

- **Decision**: Use server-validated session IDs in HttpOnly secure cookies for authentication state.
- **Rationale**: Aligns with clarification outcomes, prevents JavaScript token exfiltration from XSS paths, and cleanly replaces the current client-supplied identity-header placeholder without exposing credentials/token material in frontend state.
- **Alternatives considered**: Bearer token in client storage (rejected: higher theft/exfiltration risk and more client complexity), hybrid access/refresh tokens (rejected: unnecessary complexity for current internal v1 scope).

## 2. Login failure and lockout policy

- **Decision**: Enforce lockout for 30 minutes after 5 failed attempts in a rolling 15-minute window per account identifier, with generic failure messaging.
- **Rationale**: Satisfies clarified security requirement and provides deterministic, testable brute-force defense while avoiding account-enumeration leaks.
- **Alternatives considered**: Exponential backoff only (rejected: weaker deterministic boundary), hard admin-reset lockout (rejected: excessive operator friction for v1).

## 3. Password policy and compromised-password defense

- **Decision**: Enforce minimum 12 chars with upper/lower/number/symbol classes and reject known common-compromised passwords.
- **Rationale**: Directly maps to clarification and gives measurable policy checks; supports stronger baseline posture without introducing MFA/SSO dependencies.
- **Alternatives considered**: Length-only policy (rejected: weaker against predictable composition patterns), reuse legacy/no new policy (rejected: conflicts with clarified requirement).

## 4. Role/scope resolution strategy for RLS

- **Decision**: Resolve role and scope from authoritative server-side assignment data on every request (or strictly invalidated short cache that guarantees next-request consistency).
- **Rationale**: Meets FR-013/FR-013a (scope changes effective by next request) and avoids stale over-privileged sessions.
- **Alternatives considered**: Persist scope claims at login until logout (rejected: stale authorization risk), periodic background refresh (rejected: non-deterministic update timing).

## 5. RLS response semantics to prevent data enumeration

- **Decision**: Return 404 for record-level out-of-scope lookups; return 200 for list endpoints with server-side filtering to in-scope rows only.
- **Rationale**: Reduces record-existence leakage while preserving list UX and pagination/filter semantics.
- **Alternatives considered**: Always 403 (rejected: stronger enumeration signal for record existence), mixed behavior without standardization (rejected: inconsistent client expectations).

## 6. UI redesign implementation pattern within existing Fluent stack

- **Decision**: Keep Fluent UI v9 and implement requested colors, typography, spacing, table treatment, nav pills, badges, button states, and KPI cards through token updates and reusable shared components.
- **Rationale**: No new styling framework is needed; existing token consistency guards and responsive harnesses from feature 002 remain enforceable.
- **Alternatives considered**: Introduce second styling system (rejected: parallel theming complexity), per-screen ad hoc CSS overrides (rejected: inconsistency and maintenance risk).

## 7. Iconography choice

- **Decision**: Use the existing `@fluentui/react-icons` package as the single icon set for navigation and status-adjacent scanability.
- **Rationale**: Already installed and design-consistent with Fluent components; avoids dependency churn while satisfying consistency requirement.
- **Alternatives considered**: Lucide/Heroicons additions (rejected: unnecessary new dependency for equivalent outcome).

## 8. Harness-first validation strategy

- **Decision**: Add backend contract/harness tests for auth/login/logout/lockout/RLS and frontend Playwright + axe-core coverage for redesign parity across all in-scope routes in both themes and breakpoints.
- **Rationale**: Directly satisfies constitution Principle III and IV; keeps quality gates measurable and CI-enforceable.
- **Alternatives considered**: Manual QA only (rejected: non-repeatable, insufficient for required gates).
