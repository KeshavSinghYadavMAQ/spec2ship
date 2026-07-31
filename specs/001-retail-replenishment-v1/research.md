# Phase 0 Research: Retail Replenishment V1 Foundation

**Input**: [plan.md](./plan.md) Technical Context | **Constitution**: `.specify/memory/constitution.md` v1.1.0

All Technical Context fields were resolvable from the constitution (mandated stack), the spec's Clarifications
session (2026-07-31), and standard production practice for the mandated stack. No NEEDS CLARIFICATION markers
remain.

## Decision: Backend web framework — FastAPI

- **Decision**: Use FastAPI as the async API layer wrapping domain services and Microsoft Agent Framework (MAF)
  agent invocations.
- **Rationale**: Async-native for API request handling and MAF's async tool-calling patterns (database calls to
  Azure SQL Database run through SQLAlchemy's thread-pooled sync-driver bridge, see the Relational storage
  decision below); built-in Pydantic-based request/response validation supports the constitution's "explicit
  schemas, validation at system boundaries" requirement; strong typing and OpenAPI generation support the
  contract-first approach required for Phase 1.
- **Alternatives considered**: Django REST Framework (heavier, sync-first ORM friction with MAF's async model);
  Flask (lacks native async and schema validation, would require bolting on Pydantic/async support manually).

## Decision: Agent orchestration — Microsoft Agent Framework + Copilot SDK

- **Decision**: Use MAF for agent orchestration/tool invocation and Copilot SDK for reasoning surfaces
  (replenishment rationale, forecast narration, store-priority explanation). Deterministic policy logic (reorder
  math, threshold evaluation, priority scoring) stays in plain Python domain services; agents are invoked only
  to enrich explanations and operator assistance, never to make the underlying policy decision.
- **Rationale**: Constitution II mandates this stack. Separating deterministic policy from agent-generated
  explanation keeps recommendation quality auditable (Constitution V) and testable independent of LLM behavior
  (Constitution III harness-first).
- **Alternatives considered**: None — mandated by constitution; no deviation requested or justified.

## Decision: Relational storage — Azure SQL Database

- **Decision**: Use Azure SQL Database (vCore, general purpose tier) for InventoryPosition, StockAlert,
  ReplenishmentRecommendation, DemandForecast, TransferSuggestion, ProductLocationPolicy, StorePriorityProfile,
  and audit log tables. SQLAlchemy 2.0 accesses it via the `mssql+pyodbc` dialect; because no first-party async
  driver exists for SQL Server, database calls run through SQLAlchemy's async-compatible sync-driver bridge
  (thread-pooled execution) rather than a native async DBAPI.
- **Rationale**: Relational integrity fits the entity relationships in the spec (SKU-location keys, policy
  history, audit trails); vCore general-purpose tier supports serverless/auto-pause and right-sized compute for
  cost control (Constitution VI) and scales to the enterprise volume clarified in the spec (1,000+ stores,
  100,000+ SKUs) via read replicas, elastic pools, and partitioning by store/region if needed later. Standardizing
  on Azure SQL Database also aligns with a Microsoft-native data platform choice alongside MAF/Copilot SDK and
  simplifies Azure AD-integrated authentication and auditing (Constitution V).
- **Alternatives considered**: Cosmos DB (better for schema-less high-throughput event data but weaker fit for
  relational policy/audit integrity and adds cost complexity for a pilot); Azure Database for PostgreSQL Flexible
  Server (fully async-native via `asyncpg`, but standardizing on Azure SQL Database was preferred for this
  solution's Microsoft-native data platform alignment; the tradeoff is accepting thread-pooled synchronous
  database I/O instead of a native async driver).

## Decision: Event ingestion resilience — Azure Service Bus (queue-and-replay)

- **Decision**: Use Azure Service Bus queues/topics for inbound inventory, sales, and returns events, with
  dead-letter handling and automatic replay on reconnect, directly implementing FR-022 (queue-and-replay with
  freshness warning) from the Clarifications session.
- **Rationale**: Service Bus provides at-least-once delivery, ordering (via sessions) to help with the "duplicate
  or out-of-order events" edge case, and native retry/dead-letter semantics needed for source-system outages
  without building custom queueing infrastructure.
- **Alternatives considered**: Azure Storage Queues (simpler/cheaper but weaker ordering and dead-letter
  ergonomics); Kafka/Event Hubs (higher operational and cost overhead than justified for enterprise-scale but
  pilot-phased rollout; can be revisited if throughput requires it post-pilot).

## Decision: Caching / evaluation locks — Azure Cache for Redis

- **Decision**: Use Redis for alert deduplication/suppression windows (FR-003) and the threshold-edit lock during
  in-flight evaluations (FR-023, Clarifications Q3).
- **Rationale**: Redis TTL-based keys are a natural fit for suppression windows and short-lived evaluation locks;
  low latency keeps alert evaluation within the SC-003 (2-minute) target.
- **Alternatives considered**: Database-row locking (adds contention/latency to the primary datastore under
  enterprise-scale load); in-memory process locks (do not work across horizontally scaled instances).

## Decision: Frontend framework and component library — React 18 + Fluent UI v9

- **Decision**: React 18 with TypeScript, Vite tooling, and `@fluentui/react-components` (Fluent UI v9) as the
  component library.
- **Rationale**: Constitution IV mandates React with responsive, dark/light theming and WCAG 2.2 AA validation
  for core workflows. Fluent UI v9 ships built-in light/dark themes, accessibility-audited components, and fits
  a Microsoft-ecosystem solution (MAF/Copilot SDK backend) for visual and interaction consistency.
- **Alternatives considered**: Material UI (strong accessibility but visual identity mismatched with a
  Microsoft-aligned solution); a fully custom design system (higher build cost, slower to reach WCAG 2.2 AA
  compliance for v1).

## Decision: Server-state data fetching — TanStack Query

- **Decision**: Use TanStack Query for all API data fetching/caching in the React app, keeping fetching logic
  separate from presentational components (per copilot-instructions.md React guidance).
- **Rationale**: Built-in loading/error/stale-data states map directly to the constitution's explicit
  loading/empty/error/stale-data requirement for operational screens; reduces custom state-management code.
- **Alternatives considered**: Redux Toolkit + RTK Query (more boilerplate for this scope); plain `fetch` +
  custom hooks (would require re-implementing caching/staleness handling already solved by TanStack Query).

## Decision: Testing strategy

- **Decision**: pytest + pytest-asyncio + httpx for backend unit/contract/integration tests; a dedicated harness
  scenario runner under `backend/tests/harness` for Constitution III (happy path, failure path, data-quality edge
  cases per domain); Vitest + React Testing Library for frontend unit tests; Playwright for critical-path UI
  flows (alert triage, recommendation review, admin threshold edits).
- **Rationale**: Matches the constitution's non-negotiable harness-first requirement and the existing
  `backend/tests/{unit,integration,contract,harness}` structure already defined in `.github/copilot-instructions.md`.
- **Alternatives considered**: unittest (less ergonomic async support than pytest-asyncio); Cypress (Playwright
  chosen for better parallelization and native TypeScript support).

## Decision: Deployment target — Azure Container Apps + Azure Static Web Apps

- **Decision**: Backend services run on Azure Container Apps (Linux, consumption + dedicated plan mix for cost
  control); frontend is deployed as a static build via Azure Static Web Apps.
- **Rationale**: Container Apps gives autoscaling boundaries and scale-to-zero options for non-critical
  background workers, supporting Constitution VI's minimal-cost strategy, while remaining a managed, low-ops
  Azure Well-Architected-aligned choice. Static Web Apps is a low-cost, CDN-backed hosting option for the React
  SPA with built-in CI/CD.
- **Alternatives considered**: Azure Kubernetes Service (excessive operational overhead/cost for pilot scale);
  Azure Functions for all backend logic (poor fit for long-lived agent orchestration sessions and stateful
  evaluation locks).

## Decision: Cost guardrails — $15,000/month pilot ceiling with $0.00005/event ingestion assumption

- **Decision**: Set an explicit pilot-phase monthly Azure infrastructure spend ceiling of $15,000 (Container Apps,
  Azure SQL Database, Redis, Service Bus, Static Web Apps combined), and a per-ingested-event budget assumption of
  $0.00005 to keep FR-012/FR-022 ingestion costs predictable as volume scales toward the enterprise-scale target.
- **Rationale**: Constitution VI requires cost-impacting decisions to include measurable targets (estimated
  monthly spend ceilings and per-transaction budget assumptions), not just qualitative "guardrails." A pilot-scope
  ceiling (selected stores/categories per Assumptions) sized well below full enterprise-scale cost keeps the
  pilot affordable while the per-event assumption gives a concrete unit-economics check as ingestion volume grows.
- **Alternatives considered**: No explicit numeric ceiling (rejected — fails Constitution VI's measurable-target
  requirement); a per-store monthly ceiling instead of an aggregate figure (rejected for v1 — aggregate is simpler
  to track against a single Azure Cost Management budget alert at pilot scope).

## Decision: Ingestion rate limiting — per-source token bucket in FastAPI + Redis

- **Decision**: Enforce FR-024's per-source-system rate limit as FastAPI middleware backed by a Redis token-bucket
  counter keyed by source-system identifier, rejecting excess requests with HTTP 429 and a `Retry-After` header.
- **Rationale**: Reuses the same Redis instance already provisioned for suppression windows and evaluation locks,
  avoiding a new managed dependency (e.g., Azure API Management) for a single, well-defined limiting rule; keeps
  the limiting rule co-located with FR-022's ingestion path so both concerns are visible in one module.
- **Alternatives considered**: Azure API Management as an ingestion gateway (stronger built-in throttling/quota
  tooling but adds a new managed resource and cost for a single rate-limiting rule not otherwise needed in v1);
  no rate limiting (rejected — leaves ingestion endpoints unprotected against a misbehaving source system).

## Decision: Reliability and availability design — single-region managed PaaS meeting SC-009

- **Decision**: Meet the 99.9% monthly uptime target (SC-009) with a single-region deployment across Azure
  Container Apps (multi-replica, zone-redundant where available), Azure SQL Database (zone-redundant
  general-purpose tier), Azure Cache for Redis (standard tier with replica), and Azure Service Bus (standard
  tier), each of which independently publishes SLAs at or above 99.9%.
- **Rationale**: A composite single-region, zone-redundant architecture meets the 99.9% target without the cost
  and operational complexity of multi-region active-active failover, consistent with Constitution VI's
  minimal-cost strategy and the pilot-phase cost guardrails (SC-008); zone redundancy protects against
  data-center-level failures, the most likely failure mode at pilot scale.
- **Alternatives considered**: Multi-region active-active (higher availability ceiling but significant added cost
  and data-synchronization complexity not justified for a pilot-phase 99.9% target); single-instance
  non-zone-redundant deployment (cheaper but does not reliably meet 99.9% given no protection against
  zone-level failure).
