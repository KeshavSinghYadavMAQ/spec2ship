"""Performance validation for pilot-scale seeding (T049, SC-001, SC-006).

Seeding a genuine 1,000-store / 100,000-SKU-catalog pilot run inside a test process would
take on the order of tens of minutes end-to-end (measured: ~1.3s/store against an
in-memory SQLite session), which is impractical to run on every test invocation. Instead,
this harness seeds a representative sample at the full catalog size (100,000, matching
production-scale `rng.sample` cost) with a smaller store count, measures wall-clock
throughput, and extrapolates to the full 1,000-store pilot scale to validate the SC-001 /
SC-006 "under 30 minutes" budget with a safety margin.
"""

from __future__ import annotations

import time

from src.domain.sample_data.seed_service import (
    DEFAULT_CATALOG_SIZE,
    DEFAULT_STORE_COUNT,
    SampleDataSeedService,
)

SAMPLE_STORE_COUNT = 20
PILOT_SCALE_BUDGET_SECONDS = 30 * 60
# Modest buffer for run-to-run variance in the extrapolation; measured throughput sits at
# roughly 23 minutes projected for the full 1,000-store pilot scale, i.e. this delegated
# per-row (not bulk) write path has real but limited headroom under the 30-minute budget.
SAFETY_MARGIN = 1.2


def test_seeding_throughput_projects_within_pilot_scale_budget(db_session):
    service = SampleDataSeedService(db_session)

    started = time.perf_counter()
    result = service.seed(
        store_count=SAMPLE_STORE_COUNT,
        catalog_size=DEFAULT_CATALOG_SIZE,
        assortment_size=150,
    )
    elapsed = time.perf_counter() - started

    assert result.counts_by_entity_type["inventory_position"] > 0

    per_store_seconds = elapsed / SAMPLE_STORE_COUNT
    projected_full_scale_seconds = per_store_seconds * DEFAULT_STORE_COUNT * SAFETY_MARGIN

    assert projected_full_scale_seconds < PILOT_SCALE_BUDGET_SECONDS, (
        f"Projected full pilot-scale seeding time ({projected_full_scale_seconds:.0f}s) "
        f"exceeds the {PILOT_SCALE_BUDGET_SECONDS}s (30 minute) budget (SC-001, SC-006); "
        f"measured {per_store_seconds:.3f}s/store over a {SAMPLE_STORE_COUNT}-store sample."
    )
