# Research: Realistic Store Demo Data & Colorful Responsive Theming

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This document resolves the technical unknowns implied by the Technical Context before Phase 1 design.
All items below were resolved directly (no external research agents were required); no
`NEEDS CLARIFICATION` markers remain.

## 1. Realistic identifier generation strategy

- **Decision**: Generate fictitious but realistic-looking identifiers (e.g., `STORE-CHICAGO-014`,
  `SKU-COFFEE-12OZ`) from small, curated, static reference pools (region/city codes, product
  category and variant tokens) combined deterministically using a fixed-seed `random.Random`
  instance owned by the `sample_data` domain module.
- **Rationale**: The spec explicitly limits scope to realistic-looking identifiers, not full
  descriptive reference data (deferred fast-follow per Clarifications). A curated pool plus a
  fixed seed avoids adding a third-party fake-data dependency, keeps generation fully
  deterministic (a prerequisite for the idempotency/resumability requirement, FR-003), and avoids
  any risk of generating real trademarked brand names (Assumption).
- **Alternatives considered**: `Faker` library — rejected, adds a new backend dependency and
  license/maintenance surface for a need already satisfiable with a small static pool; random
  UUIDs — rejected, fails the "realistic-looking" requirement (FR-001).

## 2. Seed-data traceability and removal (FR-011)

- **Decision**: Introduce a single new ledger table, `sample_data_seed_records`
  (`entity_type`, `entity_id`, `seed_batch_id`, `created_at`), owned by the new `sample_data`
  domain module. Every record created by seeding is also recorded in the ledger. The clear/reset
  action deletes exactly the rows referenced by the ledger (via each domain's existing service
  methods), then clears the ledger.
- **Rationale**: Keeps existing domain tables and migrations completely untouched (no new column
  on every domain model), isolates the sample-data lifecycle concern from core domain logic per
  the constitution's separation-of-concerns guidance, and gives a precise, auditable answer to
  "was this record seeded?" without relying on naming-convention heuristics.
- **Alternatives considered**: A boolean `is_seed_data` column added to every seeded table —
  rejected, requires a migration across six domains for a fast-follow-sensitive feature; a
  naming-convention heuristic (e.g., treat all `STORE-*` IDs as seed data) — rejected, fragile and
  risks deleting genuine non-seed data that happens to match the pattern.

## 3. Non-production environment safeguard (FR-004)

- **Decision**: Reuse the existing `Settings.environment` field (`backend/src/infrastructure/config.py`,
  already defaults to `"local"`). Seeding/clear endpoints require both the existing `admin`-role
  RBAC dependency (`require_role(Role.ADMIN)`) and a new guard that rejects the request unless
  `settings.environment != "production"`.
- **Rationale**: No new configuration mechanism is needed; this satisfies the defense-in-depth
  requirement (role alone or environment alone is insufficient) with minimal code.
- **Alternatives considered**: A separate feature flag/table — rejected as redundant with the
  environment setting that already distinguishes deployment tiers.

## 4. Bulk insert strategy for pilot-scale volumes

- **Decision**: Seed in per-store batches using SQLAlchemy Core bulk `insert()` execution
  (chunked, e.g., 500-1,000 rows per statement) inside short-lived transactions, checking the
  seed ledger before each store's batch to skip already-seeded stores on re-run.
- **Rationale**: Meets the under-30-minute pilot-scale seeding target (SC-001, SC-006) without new
  infrastructure; per-store batch granularity gives natural resumability after interruption
  (FR-003) since incomplete stores are simply re-processed.
- **Alternatives considered**: Per-row ORM object inserts — rejected, too slow at 100,000+ SKU
  scale; an external ETL/bulk-load tool — rejected, unnecessary infrastructure for this scope.

## 5. Colorful, modern, responsive design system

- **Decision**: Generate a custom Fluent UI v9 `BrandVariants` palette and build light/dark themes
  via `createLightTheme`/`createDarkTheme`, replacing `webLightTheme`/`webDarkTheme` in
  `AppThemeProvider`. Add a small semantic token layer (`success`/`warning`/`danger`/`info`) in a
  new `theme/tokens.ts`, paired with icons/text labels (not color alone) for status/severity
  indicators (FR-010).
- **Rationale**: Stays within the existing `@fluentui/react-components` dependency (Assumption:
  extend, don't replace, the existing theming foundation), and Fluent's theme generator is
  designed to preserve accessible contrast ratios across both themes.
- **Alternatives considered**: A second styling system (CSS variables/Tailwind) — rejected,
  contradicts the "extend, not replace" assumption and would create two parallel styling
  mechanisms; keeping the stock `webLightTheme`/`webDarkTheme` — rejected, does not satisfy the
  "colorful modern" requirement (today's default is plain).

## 6. Responsive and accessibility validation approach

- **Decision**: Reuse the existing Playwright + `@axe-core/playwright` frontend dependencies
  (already in `package.json`) to add a harness suite that loads every in-scope screen at three
  fixed viewport presets (360px mobile — the clarified minimum supported width, 768px tablet,
  1440px desktop) and asserts no horizontal scroll/clipped content plus zero axe-core WCAG AA
  violations in both themes.
- **Rationale**: No new tooling required; directly satisfies the Harness-First Validation
  constitution principle for US2-US4.
- **Alternatives considered**: Manual QA only — rejected, not repeatable or CI-enforceable.
