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

### Indicative pilot-scope monthly cost breakdown

The $15,000/month ceiling from `research.md`'s "Cost guardrails" decision covers Container
Apps, Azure SQL Database, Redis, Service Bus, and Static Web Apps combined. The table below
is a rough, non-binding allocation across those services at pilot scope (selected
stores/categories per spec.md's Assumptions), intended to sanity-check that the ceiling is
achievable — actual costs must be confirmed against Azure Pricing Calculator output and
real Azure Cost Management data once resources are provisioned, not derived from this table.

| Service | Tier (per research.md) | Rough monthly estimate |
| --- | --- | --- |
| Azure Container Apps | Consumption + dedicated plan mix, multi-replica | ~$3,000-5,000 |
| Azure SQL Database | vCore, general purpose, zone-redundant | ~$3,000-5,000 |
| Azure Cache for Redis | Standard tier with replica | ~$500-1,000 |
| Azure Service Bus | Standard tier | ~$200-500 |
| Azure Static Web Apps | Standard plan (CDN-backed) | ~$100-200 |
| **Total (indicative)** | | **~$6,800-11,700**, leaving headroom under the $15,000 ceiling |

- This leaves roughly $3,000-8,000/month of headroom against the ceiling for
  observability tooling (Application Insights/Log Analytics ingestion), autoscale bursts,
  and the per-event ingestion cost tracked separately by `CostGuardrailTracker`.
- **Follow-up recommendation**: replace this indicative table with actual Azure Pricing
  Calculator estimates sized to the enterprise-scale data volume (1,000+ stores,
  100,000+ SKUs) once concrete throughput/storage numbers are known, and set an Azure
  Cost Management budget alert at the $15,000 ceiling so overspend is caught
  automatically rather than relying solely on the in-app per-event estimate.

## SC-009 — 99.9% monthly uptime, single-region managed-service deployment

> "Platform maintains at least 99.9% monthly uptime for core inventory, alerting, and
> replenishment workflows, measured against a single-region managed-service deployment."

- Per `plan.md`, the target deployment topology is Azure Container Apps (backend) +
  Azure Static Web Apps (frontend) + managed Azure SQL Database / Azure Cache for Redis /
  Azure Service Bus — all managed PaaS services with their own published SLAs, in a
  single Azure region (no multi-region failover is claimed or required by SC-009's
  wording).

### Zone-redundancy configuration (per research.md's "Reliability and availability design" decision)

| Service | Zone-redundancy configuration | Published SLA |
| --- | --- | --- |
| Azure Container Apps | Multi-replica, zone-redundant where available | ≥99.9% |
| Azure SQL Database | Zone-redundant, general-purpose vCore tier | ≥99.9% |
| Azure Cache for Redis | Standard tier with replica | ≥99.9% |
| Azure Service Bus | Standard tier | ≥99.9% |

- This is a **single-region, zone-redundant** design (protects against data-center/zone
  failures, the most likely failure mode at pilot scale), explicitly *not*
  multi-region active-active — that alternative was considered and rejected in
  `research.md` as unjustified cost/complexity for a pilot-phase 99.9% target (it would
  also push spend well past the SC-008 ceiling above).
- Each managed service's independently published SLA is individually ≥99.9%; the
  composite platform SLA is the product of the dependent services' SLAs, which is why
  zone redundancy (not just "managed PaaS") is required on each tier rather than relying
  on a single non-zone-redundant instance per service.
- **Not yet implemented**: this repository does not yet contain Bicep/Terraform
  definitions that actually provision these services with zone-redundancy enabled — the
  configuration above is the *design target* recorded in `research.md`/`plan.md`, not a
  verified deployed state. Provisioning must explicitly select the zone-redundant SKU/tier
  for each service (these are opt-in configurations, not defaults) before SC-009 can be
  considered met in a real deployment.
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
