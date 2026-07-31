# Data Model: Realistic Store Demo Data & Colorful Responsive Theming

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Research**: [research.md](./research.md)

## New Entities

### SampleDataSeedRecord (backend, table `sample_data_seed_records`)

Ledger entry recording that a specific domain record was created by sample-data seeding, so the
clear/reset action (FR-011) can remove exactly — and only — seeded records.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` (UUID, PK) | Ledger row identifier. |
| `entity_type` | `str` | Logical domain table the seeded record belongs to (e.g., `location`, `product`, `product_location_policy`, `inventory_position`, `alert`, `recommendation`, `forecast`, `transfer_suggestion`, `store_priority_profile`). |
| `entity_id` | `str` | Natural key of the seeded record within `entity_type` (e.g., a `sku_id`/`location_id` composite or a record's primary key). |
| `seed_batch_id` | `str` (UUID) | Groups all ledger rows created by a single seeding run; supports auditing/observability of individual seeding executions. |
| `created_at` | `datetime` | When the ledger entry (and the corresponding seeded record) was created. |

**Constraints**:
- Unique on (`entity_type`, `entity_id`) — re-seeding an already-seeded record MUST NOT create a
  duplicate ledger row (supports FR-003 idempotency).
- Indexed on `seed_batch_id` for efficient per-run auditing.

**Relationships**: Logical (not a foreign key) reference from `entity_type` + `entity_id` to the
corresponding row in the relevant existing domain table (e.g., `inventory_positions`,
`product_location_policies`, `alerts`, `recommendations`, `forecasts`, `transfer_suggestions`,
`store_priority_profiles`). Kept logical rather than a physical FK so the ledger stays a
standalone, domain-agnostic module per the isolation decision in research.md item 2.

**Lifecycle**:
- Created: one row per seeded domain record, written in the same logical unit of work as the
  domain record itself (via each existing domain service).
- Read: by the clear/reset action, to enumerate exactly which domain records to delete.
- Deleted: all ledger rows for a batch are removed once the corresponding domain records have
  been successfully deleted by the clear/reset action.

### Design Tokens (frontend only, no backend schema)

A static, versioned TypeScript module (`frontend/src/theme/tokens.ts`), not a persisted entity.

| Token group | Description |
|---|---|
| `brandVariants` | 14-step Fluent UI `BrandVariants` ramp used to derive both the light and dark themes via `createLightTheme`/`createDarkTheme`. |
| `statusTokens` | Semantic color tokens (`success`, `warning`, `danger`, `info`) each paired with a non-color affordance (icon name / text label) for FR-010 colorblind-accessible status indicators. |

No database migration is required for this entity; it is consumed entirely client-side by
`AppThemeProvider` and feature components.

## Existing Entities Reused (no schema changes)

Sample-data seeding writes to the following existing domain entities (from spec 001's
`data-model.md`) strictly through their existing domain services — no new columns or migrations
are introduced on any of these tables:

- Location / Store
- Product / SKU
- ProductLocationPolicy
- InventoryPosition
- Alert
- Recommendation
- Forecast
- TransferSuggestion
- StorePriorityProfile
- AuditLogEntry (seeding/clear actions are recorded here like any other admin action, per FR-004
  and the constitution's Operational Trustworthiness principle)

## State Transitions

**Sample Data Set** (conceptual, spanning the ledger + existing domain tables):

```text
[Not Seeded] --(POST /v1/admin/sample-data/seed)--> [Seeding In Progress]
[Seeding In Progress] --(interrupted)--> [Partially Seeded]
[Partially Seeded] --(POST /v1/admin/sample-data/seed, re-run)--> [Seeding In Progress] --(completes)--> [Fully Seeded]
[Seeding In Progress] --(completes)--> [Fully Seeded]
[Fully Seeded] --(DELETE /v1/admin/sample-data)--> [Not Seeded]
[Partially Seeded] --(DELETE /v1/admin/sample-data)--> [Not Seeded]
```

Both the seed and clear transitions are gated by the same precondition: caller has the `admin`
role AND the deployment's `environment` is not `production` (FR-004, FR-011).
