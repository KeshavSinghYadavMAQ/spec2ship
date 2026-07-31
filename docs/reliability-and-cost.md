# Reliability and Cost Guardrail Validation (T104 — SC-008, SC-009)

Design-level validation of the two infrastructure success criteria from spec.md,
performed as part of Phase 11 polish.

## SC-008 — Monthly pilot cost ceiling ($15,000/month, $0.00005/event)

> "Monthly pilot operating cost remains within a $15,000/month Azure infrastructure
> ceiling ... with per-event ingestion cost tracked against a $0.00005-per-event
> assumption, while meeting service-level goals."

- `CostGuardrailTracker` (`backend/src/infrastructure/cost_guardrails.py`) records every
  ingested event (`cost_guardrails.record_ingested_event()`, called from
  `POST /v1/inventory/events`) and exposes a snapshot with
  `estimated_ingestion_cost_usd`, `monthly_cost_ceiling_usd`, and `within_ceiling`.
- **New this task**: this snapshot is now surfaced through
  `GET /v1/admin/cost-guardrails` (`backend/src/api/routers/cost_guardrails.py`) and
  rendered as a live card on the Operational Dashboard
  (`frontend/src/features/analytics/Dashboard.tsx`, via
  `useCostGuardrails`/`hooks/useCostGuardrails.ts`) — previously the tracker existed but
  had no read surface, so SC-008 could not actually be *observed* by operators. This
  closes that gap.
- The $15,000/month ceiling and $0.00005/event assumption are both configurable via
  `backend/src/infrastructure/config.py` (`cost_ceiling_monthly_usd`,
  `cost_per_ingested_event_usd`), not hard-coded, so they can be recalibrated as real
  Azure Cost Management data becomes available post-deployment.
- **Scope/limitation** (documented in the module docstring): this is an
  *estimation aid*, not a substitute for actual Azure Cost Management billing data. It
  only tracks per-event ingestion cost, not the full infrastructure bill (compute,
  storage, cache, messaging baseline costs called out in SC-008's wording). A full cost
  validation requires pairing this in-app estimate with real Azure Cost Management
  exports once deployed.

## SC-009 — 99.9% monthly uptime, single-region managed-service deployment

> "Platform maintains at least 99.9% monthly uptime for core inventory, alerting, and
> replenishment workflows, measured against a single-region managed-service deployment."

- Per `plan.md`, the target deployment topology is Azure Container Apps (backend) +
  Azure Static Web Apps (frontend) + managed Azure SQL Database / Azure Cache for Redis /
  Azure Service Bus — all managed PaaS services with their own published SLAs, in a
  single Azure region (no multi-region failover is claimed or required by SC-009's
  wording).
- Resilience patterns already implemented in code that support this target:
  - **Queue-and-replay** (FR-022): `backend/src/domain/inventory/replay_worker.py`
    replays dead-lettered integration events once an upstream outage clears, so a
    transient failure doesn't cause permanent data loss.
  - **Per-source rate limiting** (FR-024): `RateLimitMiddleware`
    (`backend/src/api/middleware/rate_limit.py`) returns retryable `429`s with
    `Retry-After` rather than crashing under load spikes from a single noisy source
    system.
  - **Edit-lock protection** (FR-023): `PolicyService` prevents concurrent threshold edits
    during an in-flight evaluation cycle, avoiding a class of data-race-induced incidents.
  - **Structured observability**: `configure_observability()` wires logs/metrics/traces
    across all domains, which is the operational prerequisite for detecting and
    responding to availability incidents quickly enough to hit a 99.9% monthly budget
    (~43 minutes of downtime/month).
- **Scope/limitation**: 99.9% uptime is ultimately an infrastructure/operations
  commitment (deployment topology, autoscaling rules, alerting on the managed services
  themselves, on-call response), not something a codebase alone can guarantee or that a
  local test suite can measure. This repository does not yet include the actual Azure
  Bicep/Terraform provisioning definitions or autoscaling rule configuration — those are
  called out in `plan.md`'s target platform section as the deployment responsibility, not
  yet implemented as infrastructure-as-code in this repo.
- **Follow-up recommendation**: before go-live, provision the Azure resources per
  `plan.md`'s target platform, configure autoscaling boundaries and health probes on
  Container Apps, and validate the 99.9% target via the managed services' own SLA
  documentation plus a synthetic uptime monitor (e.g., Azure Monitor availability tests)
  rather than relying solely on code-level resilience patterns.
