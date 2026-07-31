# Documentation Index

Cross-links between the delivery specs under `specs/001-retail-replenishment-v1/` and the
review notes produced during Phase 11 polish (T096).

## Feature specification artifacts

- [Feature spec](../specs/001-retail-replenishment-v1/spec.md) — user stories, functional
  requirements, success criteria (SC-001..SC-009), key entities.
- [Implementation plan](../specs/001-retail-replenishment-v1/plan.md) — tech stack,
  architecture, constitution gate checks.
- [Architecture](../specs/001-retail-replenishment-v1/architecture.md) — system context
  and component diagram.
- [Tasks](../specs/001-retail-replenishment-v1/tasks.md) — the full phase-by-phase task
  breakdown tracked during `/speckit.implement`.
- [Research decisions](../specs/001-retail-replenishment-v1/research.md) — stack and
  design rationale (cost guardrails, queue/replay approach, RBAC placeholder, etc).
- [Data model](../specs/001-retail-replenishment-v1/data-model.md) — entities and
  relationships.
- [API contracts](../specs/001-retail-replenishment-v1/contracts/openapi.yaml) — OpenAPI
  spec for all `/v1` endpoints.
- [Quickstart](../specs/001-retail-replenishment-v1/quickstart.md) — local setup, test
  commands, and the constitution PR self-check.
- [Requirements checklist](../specs/001-retail-replenishment-v1/checklists/requirements.md)

## Phase 11 polish review notes

- [Security review](./security-review.md) — OWASP Top 10 pass (T102): RBAC enforcement,
  injection/XSS review, dependency vulnerabilities, and documented residual risks.
- [Performance validation](./performance-validation.md) — design-level validation against
  SC-001 (60s stock visibility), SC-003 (2min alert notification), SC-007 (2min triage
  workflows) (T098).
- [Reliability and cost](./reliability-and-cost.md) — SC-008 (cost guardrail dashboard)
  and SC-009 (99.9% uptime design) validation (T104).

## Governance

- [Constitution](../.specify/memory/constitution.md) — non-negotiable delivery gates
  (specification, architecture, harness-first validation, observability/security,
  UX, Azure Well-Architected/cost).
