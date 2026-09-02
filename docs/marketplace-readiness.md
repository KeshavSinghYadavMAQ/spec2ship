# Azure Marketplace Readiness

**Assessment date**: 2026-08-27

**Current disposition**: **Ready for controlled staging deployment; not ready for Marketplace certification**.

## Repository-Verified Gates

| Gate | Status | Evidence |
|---|---|---|
| Versioned specification and contracts | PASS | `specs/001-retail-replenishment-v1/` and `contracts/openapi.yaml` |
| Deterministic business decisions | PASS | Typed inventory, alert, replenishment, forecast, transfer, KPI, and RBAC services |
| Runtime agent boundary | PASS | `.github/agent-skill-value-map.md`, `backend/src/agents/` |
| Operational harness/evaluation tests | PRESENT | `backend/tests/harness/`, `backend/tests/evaluation/`, `frontend/tests/evaluation.test.tsx` |
| Frontend/backend packaging | PASS | `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf` |
| Azure deployment baseline | PASS | `infra/main.bicep`, `infra/dev.bicepparam`; Bicep compile and deployment snapshot have no diagnostics |
| Readiness probes | PASS | `/healthz`, `/readyz`, Container Apps liveness/readiness configuration |
| CI quality-gate definition | PRESENT | `.github/workflows/quality-gates.yml` |
| Marketplace release checklist | PRESENT | `marketplace/README.md`, `marketplace/offer-metadata.template.yml` |

## Release Blockers

1. Azure Entra tenant/app registration, issuer, audience, JWKS, and staging token validation must be supplied and tested.
2. Azure subscription deployment must validate private networking, region/SKU availability, migrations, secret storage, and rollback.
3. Notification delivery must be integrated with an approved provider, including retries, delivery receipts, dead-letter handling, and monitoring. Current routing is a persistence-safe placeholder.
4. OpenTelemetry/Azure Monitor exporters, correlation IDs, retention, alert rules, and operational dashboards must be enabled and validated in staging.
5. Enterprise-scale load, dependency-failure, synthetic availability, restore, and cost-budget tests must pass with evidence.
6. Backend and frontend tests must run in CI with installed dependencies; local verification is incomplete when `pytest` or `node_modules` are unavailable.
7. Marketplace publisher enrollment, legal URLs, EULA, privacy policy, terms, support SLA, data residency statement, pricing, screenshots, SBOM, vulnerability report, and Partner Center certification remain outstanding.

## Go-Live Rule

Do not report the offer as Marketplace-ready until every release blocker is checked in
`marketplace/README.md` and the release owner has attached staging evidence. Repository code alone
cannot establish Azure service availability, real-world SLOs, provider delivery, billing limits, or
Partner Center certification.
