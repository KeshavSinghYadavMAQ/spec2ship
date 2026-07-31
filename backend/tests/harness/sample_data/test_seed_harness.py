"""Harness scenario for sample-data seeding (T017, US1, Constitution III non-negotiable).

Happy path: full seed + clear round-trip leaves no residue in the ledger or domain
tables. Failure path: an interrupted (partial) seeding run resumes without duplicating
already-seeded records. Data-quality edge case: a seed identifier colliding with a
pre-existing, non-seed record fails fast rather than silently overwriting it (FR-012).
"""

from __future__ import annotations

import pytest
from src.domain.inventory.models import InventoryPosition, InventoryPositionRepository
from src.domain.sample_data.clear_service import SampleDataClearService
from src.domain.sample_data.ledger import SeedIdentifierCollisionError
from src.domain.sample_data.reference_data import generate_sku_catalog, generate_store_ids, make_rng
from src.domain.sample_data.seed_service import SampleDataSeedService

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def test_seed_harness_scenarios(db_session):
    def happy_path() -> None:
        service = SampleDataSeedService(db_session)
        service.seed(store_count=3, catalog_size=6, assortment_size=3)

        clear_service = SampleDataClearService(db_session)
        result = clear_service.clear()

        assert sum(result.removed_counts_by_entity_type.values()) > 0
        assert result.remaining_ledger_rows == 0
        assert db_session.query(InventoryPosition).count() == 0

    def failure_path() -> None:
        # Simulate an interrupted run: seed once, then re-run with a larger store_count.
        # Already-seeded stores must not be duplicated; only the newly added stores gain
        # new records.
        service = SampleDataSeedService(db_session)
        service.seed(store_count=2, catalog_size=5, assortment_size=3, seed_batch_id="batch-1")
        positions_after_partial = db_session.query(InventoryPosition).count()

        service.seed(store_count=4, catalog_size=5, assortment_size=3, seed_batch_id="batch-2")
        positions_after_resume = db_session.query(InventoryPosition).count()

        assert positions_after_resume >= positions_after_partial
        # No duplicate (sku_id, location_id) rows were created for the already-seeded stores.
        all_positions = db_session.query(InventoryPosition).all()
        keys = [(p.sku_id, p.location_id) for p in all_positions]
        assert len(keys) == len(set(keys))

        # Reset state so the next scenario starts from a clean, unseeded ledger.
        SampleDataClearService(db_session).clear()

    def data_quality_edge_case() -> None:
        rng = make_rng()
        store_id = generate_store_ids(1, rng)[0]
        sku_id = generate_sku_catalog(1)[0]

        # A genuine (non-seed) record already occupies this natural key.
        InventoryPositionRepository(db_session).upsert_delta(
            sku_id=sku_id, location_id=store_id, shelf_delta=10, backroom_delta=5, event_id="real-event-1"
        )

        service = SampleDataSeedService(db_session)
        with pytest.raises(SeedIdentifierCollisionError):
            service.seed(store_count=1, catalog_size=1, assortment_size=1)

    run_scenarios(
        [
            HarnessScenario(
                "full seed + clear round-trip leaves no residue", ScenarioKind.HAPPY_PATH, happy_path
            ),
            HarnessScenario(
                "interrupted seeding resumes without duplicates",
                ScenarioKind.FAILURE_PATH,
                failure_path,
            ),
            HarnessScenario(
                "seed/real-data identifier collision fails fast",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
