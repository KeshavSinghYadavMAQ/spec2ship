"""Integration test: seeding populates every existing domain (T016, US1, FR-001, FR-002).

Exercises `SampleDataSeedService` directly (small scale) and asserts every domain table
that an existing dashboard reads from ends up with at least one row, so no dashboard is
left empty after seeding.
"""

from __future__ import annotations

from src.domain.alerting.models import StockAlert
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.forecasting.models import DemandForecast
from src.domain.inventory.models import InventoryPosition
from src.domain.replenishment.models import ReplenishmentRecommendation
from src.domain.sample_data.seed_service import SampleDataSeedService
from src.domain.transfer_balance.models import TransferSuggestion
from src.domain.transfer_balance.priority_models import StorePriorityProfile


def test_seeding_populates_every_domain(db_session):
    service = SampleDataSeedService(db_session)
    result = service.seed(store_count=6, catalog_size=10, assortment_size=6)

    assert result.counts_by_entity_type["inventory_position"] > 0
    assert result.counts_by_entity_type["product_location_policy"] > 0
    assert result.counts_by_entity_type["store_priority_profile"] == 6

    assert db_session.query(InventoryPosition).count() > 0
    assert db_session.query(ProductLocationPolicy).count() > 0
    assert db_session.query(DemandForecast).count() > 0
    assert db_session.query(StorePriorityProfile).count() == 6

    # With a small catalog and generous per-store assortment, at least some stores share
    # SKUs, so alerts, recommendations, and transfer suggestions should also be populated.
    assert db_session.query(StockAlert).count() > 0
    assert db_session.query(ReplenishmentRecommendation).count() > 0
    assert db_session.query(TransferSuggestion).count() > 0


def test_seeding_is_idempotent_on_rerun(db_session):
    service = SampleDataSeedService(db_session)
    service.seed(store_count=4, catalog_size=8, assortment_size=4)
    positions_after_first_run = db_session.query(InventoryPosition).count()

    service.seed(store_count=4, catalog_size=8, assortment_size=4)
    positions_after_second_run = db_session.query(InventoryPosition).count()

    assert positions_after_first_run == positions_after_second_run
