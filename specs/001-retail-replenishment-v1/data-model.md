# Data Model: Retail Replenishment V1 Foundation

**Input**: `specs/001-retail-replenishment-v1/spec.md` Key Entities and Functional Requirements | **Research**: [research.md](./research.md)

All entities are relational (Azure SQL Database). Fields marked *(audited)* are covered by FR-014/FR-018
audit logging. Enterprise-scale volume (1,000+ stores, 100,000+ SKUs, per Clarifications) informs indexing:
every entity keyed by SKU-location or store MUST have a composite index on (`sku_id`, `location_id`) or
(`store_id`) respectively.

## InventoryPosition

Current and projected quantity state for a SKU-location, with shelf/backroom split and freshness metadata (US1, FR-001, FR-012).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `sku_id` | string | Indexed with `location_id` |
| `location_id` | string | Store or warehouse identifier |
| `shelf_quantity` | integer | >= 0 |
| `backroom_quantity` | integer | >= 0 |
| `reconciled_total` | integer | Derived: `shelf_quantity + backroom_quantity` |
| `last_event_id` | UUID | FK to `IntegrationEvent`, for idempotency/ordering |
| `freshness_at` | timestamp | Last successful update time; drives SC-001 |
| `data_freshness_warning` | boolean | Set true while replaying queued events per FR-022 |

**Validation**: Reject negative quantities. Deduplicate by `(sku_id, location_id, last_event_id)` to satisfy the
"duplicate or out-of-order events" edge case.

**Relationships**: Many `IntegrationEvent` records reduce into one `InventoryPosition` per SKU-location.

## StockAlert

Alert record for low stock or out-of-stock conditions (US2, FR-002, FR-003).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `sku_id` / `location_id` | string | Indexed pair |
| `severity` | enum | `low_stock`, `out_of_stock` |
| `status` | enum | Lifecycle (see below) |
| `owner_user_id` | string | Assigned operator, nullable until acknowledged |
| `routing_channel` | string | Resolved delivery channel |
| `suppressed_until` | timestamp | Suppression window per policy (FR-003) |
| `created_at` / `updated_at` *(audited)* | timestamp | |

**Lifecycle (Clarifications Q4)**: `Open → Acknowledged → Escalated → Snoozed → Resolved`. Valid transitions:
`Open → Acknowledged`, `Open → Escalated`, `Acknowledged → Escalated`, `Acknowledged → Snoozed`,
`Escalated → Snoozed`, any of `{Acknowledged, Escalated, Snoozed} → Resolved`. `Resolved` is terminal until a new
breach re-opens a new alert record (alerts are not reopened in place, to preserve audit history).

## ReplenishmentRecommendation

Reorder recommendation with quantity, timing, constraints, and explanation factors (US3, FR-004, FR-005).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `sku_id` / `location_id` | string | Indexed pair |
| `recommended_quantity` | integer | >= 0 |
| `recommended_by_date` | date | Reorder timing |
| `policy_snapshot` | jsonb | Reorder point, min-max, lead-time, safety-stock inputs used |
| `rationale` | jsonb | Structured explanation factors (Copilot SDK-generated narration + deterministic factor list) |
| `status` | enum | `proposed`, `accepted`, `overridden`, `dismissed` |
| `override_reason` *(audited)* | string | Required when `status = overridden` |

**Validation**: `rationale` MUST NOT be empty (Constitution: preserve explanation payloads).

## DemandForecast

Future demand projection by SKU and store (US4, FR-006, FR-007).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `sku_id` / `location_id` | string | Indexed pair |
| `horizon_start` / `horizon_end` | date | Forecast window |
| `projected_demand` | numeric | |
| `seasonality_factor` / `promotion_factor` | numeric | Adjustment inputs |
| `error_indicator` | numeric | Forecast quality metric (FR-007) |

## TransferSuggestion

Proposed transfer action between source and destination (US5, FR-008, FR-009).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `sku_id` | string | |
| `source_location_id` / `destination_location_id` | string | |
| `suggested_quantity` | integer | >= 1 |
| `feasibility_status` | enum | `feasible`, `infeasible` |
| `priority_rank` | integer | Populated from `StorePriorityProfile` when constrained (FR-020) |
| `status` | enum | `suggested`, `accepted`, `in_transit`, `completed`, `rejected` |

## KPIView

Aggregated operational metrics for inventory health, fill rate, aging, and forecast/recommendation performance (US6, FR-010, FR-011). Materialized/aggregated read model, not a source-of-truth table; recomputed on a schedule from the entities above.

| Field | Type | Notes |
|---|---|---|
| `metric_key` | string | e.g., `fill_rate`, `aging_days`, `forecast_accuracy` |
| `dimension` | jsonb | Region/store/category/time filters (FR-010) |
| `value` | numeric | |
| `computed_at` | timestamp | |

## ProductLocationPolicy

Configuration record linking a product to a location with alert thresholds, replenishment controls, activation state, and change history (US7, FR-016, FR-017, FR-018, FR-023).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `sku_id` / `location_id` | string | Indexed pair, unique together |
| `low_stock_threshold` / `out_of_stock_threshold` | integer | |
| `reorder_point` / `min_qty` / `max_qty` / `safety_stock` | integer | Replenishment control values |
| `is_active` | boolean | |
| `edit_lock_held` | boolean | True while an evaluation cycle is in progress (FR-023) |
| `updated_by` / `updated_at` *(audited)* | string / timestamp | |
| `change_history` | jsonb array *(audited)* | Prior values for audit trail (FR-018) |

**Validation**: `low_stock_threshold < out_of_stock_threshold` is invalid... actually out-of-stock is 0 by
definition; reject if `low_stock_threshold <= 0` or `min_qty > max_qty`. Reject edits while `edit_lock_held = true`
(FR-023); return validation errors per FR-016 Acceptance Scenario 3.

## StorePriorityProfile

Store-level prioritization record capturing region, consumption indicators, weighting factors, and current
restoration rank (US8, FR-019, FR-020, FR-021).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `store_id` | string | Indexed |
| `region` | string | |
| `recent_consumption_rate` | numeric | Rolling window metric |
| `region_weight` / `consumption_weight` | numeric | Configurable factors (FR-019) |
| `current_priority_rank` | integer | Recomputed on schedule/trigger |
| `priority_factors` | jsonb | Explanation payload for FR-021 review |

## IntegrationEvent

Normalized inbound inventory, sales, and return event with source and processing state (cross-cutting, FR-012,
FR-022).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `source_system` | string | |
| `event_type` | enum | `stock_update`, `sale`, `return` |
| `payload` | jsonb | Normalized event body |
| `processing_state` | enum | `queued`, `processing`, `applied`, `replayed`, `dead_lettered` |
| `received_at` / `applied_at` | timestamp | |

**Lifecycle**: `queued → processing → applied`, or `queued → dead_lettered → replayed → applied` when the source
was unavailable (FR-022).

## UserRoleAssignment

Mapping of user responsibilities and access rights to operational functions (cross-cutting, FR-013).

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | string | |
| `role` | enum | `store_manager`, `inventory_manager`, `procurement_officer`, `regional_manager`, `admin` |
| `location_scope` | jsonb | Store/region scope the role applies to, nullable for global roles |
