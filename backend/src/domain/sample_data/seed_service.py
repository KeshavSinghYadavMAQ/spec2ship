"""`SampleDataSeedService` (T018-T020, US1, FR-001, FR-002, FR-003, FR-005, FR-012).

Orchestrates per-store batched generation of realistic, pilot-scale sample data across
every existing domain (inventory, alerting, replenishment, forecasting, transfer_balance,
store priority), delegating all writes to the existing domain services/repositories so
seeded data obeys the same validation rules as real data. Every write is recorded in the
seed-record ledger (`SeedLedger`) so the run is:

- **Idempotent / resumable** (FR-003): already-ledger-tracked entities are skipped, so an
  interrupted run can be safely re-run to completion without duplicating records.
- **Non-destructive of real data** (FR-012): before creating a record, a fail-fast
  collision check (`SeedLedger.assert_no_collision`) refuses to proceed if a real,
  non-seed record already occupies the same natural key rather than silently overwriting
  or duplicating it.

Seeding intentionally writes `StockAlert` rows directly via `StockAlertRepository`
instead of `ThresholdEvaluationService.evaluate()`, because that service also dispatches
live notifications and mutates suppression state in the cache - side effects that make
sense for real-time alerting but not for populating demo data.
"""

from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.orm import Session

from src.domain.admin.audit import AuditLogWriter
from src.domain.alerting.models import Severity, StockAlertRepository
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.alerting.policy_service import PolicyService
from src.domain.alerting.routing import resolve_channel
from src.domain.forecasting.engine import ForecastingEngine
from src.domain.forecasting.models import DemandForecastRepository
from src.domain.inventory.models import InventoryPositionRepository
from src.domain.replenishment.engine import ReplenishmentEngine
from src.domain.replenishment.models import ReplenishmentRecommendationRepository
from src.domain.sample_data.ledger import SeedLedger
from src.domain.sample_data.reference_data import (
    generate_sku_catalog,
    generate_store_ids,
    make_rng,
    store_region_for_id,
)
from src.domain.transfer_balance.engine import TransferBalanceEngine
from src.domain.transfer_balance.models import TransferSuggestionRepository
from src.domain.transfer_balance.priority_models import StorePriorityProfile
from src.domain.transfer_balance.priority_service import StorePriorityService

DEFAULT_STORE_COUNT = 1_000
DEFAULT_CATALOG_SIZE = 100_000
DEFAULT_ASSORTMENT_SIZE = 150
_MAX_STORES_PER_SKU_FOR_TRANSFER_PAIRING = 25


@dataclass
class SeedRunResult:
    seed_batch_id: str
    counts_by_entity_type: dict[str, int]
    started_at: datetime
    completed_at: datetime | None
    store_ids: list[str] = field(default_factory=list)
    sku_catalog: list[str] = field(default_factory=list)


def _pick_health_status(rng) -> str:
    roll = rng.random()
    if roll < 0.55:
        return "healthy"
    if roll < 0.80:
        return "low_stock"
    if roll < 0.90:
        return "out_of_stock"
    return "overstock"


class SampleDataSeedService:
    def __init__(self, session: Session, *, actor_user_id: str = "system-seed") -> None:
        self._session = session
        self._actor_user_id = actor_user_id
        self._ledger = SeedLedger(session)
        self._audit = AuditLogWriter(session)
        self._positions = InventoryPositionRepository(session)
        self._policy_service = PolicyService(session, self._audit)
        self._alerts = StockAlertRepository(session)
        self._recommendations = ReplenishmentRecommendationRepository(session)
        self._replenishment_engine = ReplenishmentEngine(self._recommendations)
        self._forecasts = DemandForecastRepository(session)
        self._forecasting_engine = ForecastingEngine(self._forecasts)
        self._transfers = TransferSuggestionRepository(session)
        self._transfer_engine = TransferBalanceEngine(self._transfers)
        self._priority_service = StorePriorityService(session)

    def seed(
        self,
        *,
        store_count: int = DEFAULT_STORE_COUNT,
        catalog_size: int = DEFAULT_CATALOG_SIZE,
        assortment_size: int = DEFAULT_ASSORTMENT_SIZE,
        seed_batch_id: str | None = None,
    ) -> SeedRunResult:
        seed_batch_id = seed_batch_id or str(uuid.uuid4())
        started_at = datetime.now(UTC)
        rng = make_rng()

        store_ids = generate_store_ids(store_count, rng)
        sku_catalog = generate_sku_catalog(catalog_size)

        store_assortments: dict[str, list[str]] = {
            store_id: rng.sample(sku_catalog, min(assortment_size, len(sku_catalog)))
            for store_id in store_ids
        }

        for store_id in store_ids:
            if self._ledger.is_seeded("store_priority_profile", store_id):
                continue  # resumability (FR-003): this store was already fully seeded
            self._seed_store(store_id, store_assortments[store_id], rng, seed_batch_id)

        region_priority_scores = {
            store_id: round(rng.uniform(0.0, 1.0), 3) for store_id in store_ids
        }
        self._priority_service.recompute_rankings(region_priority_scores=region_priority_scores)

        sku_to_stores: dict[str, list[str]] = {}
        for store_id, assortment in store_assortments.items():
            for sku_id in assortment:
                sku_to_stores.setdefault(sku_id, []).append(store_id)
        self._seed_transfers(sku_to_stores, seed_batch_id)

        completed_at = datetime.now(UTC)
        self._audit.record(
            actor_user_id=self._actor_user_id,
            action="sample_data.seed",
            entity_type="sample_data_seed_batch",
            entity_id=seed_batch_id,
            after={"store_count": store_count, "catalog_size": catalog_size},
        )
        return SeedRunResult(
            seed_batch_id=seed_batch_id,
            counts_by_entity_type=self._ledger.counts_by_entity_type(seed_batch_id),
            started_at=started_at,
            completed_at=completed_at,
            store_ids=store_ids,
            sku_catalog=sku_catalog,
        )

    def _seed_store(
        self, store_id: str, assortment: list[str], rng, seed_batch_id: str
    ) -> None:
        for sku_id in assortment:
            self._seed_position_and_downstream(store_id, sku_id, rng, seed_batch_id)

        region = store_region_for_id(store_id)
        consumption_rate = round(rng.uniform(5.0, 500.0), 2)
        self._seed_store_priority_profile(store_id, region, consumption_rate, seed_batch_id)

    def _seed_position_and_downstream(
        self, store_id: str, sku_id: str, rng, seed_batch_id: str
    ) -> None:
        composite_key = f"{sku_id}::{store_id}"

        low_stock_threshold = rng.randint(15, 30)
        out_of_stock_threshold = rng.randint(2, min(8, low_stock_threshold))
        reorder_point = low_stock_threshold + rng.randint(0, 10)
        min_qty = rng.randint(5, 15)
        max_qty = rng.randint(80, 150)
        safety_stock = rng.randint(10, 25)

        health = _pick_health_status(rng)
        if health == "healthy":
            total = rng.randint(reorder_point + 1, max_qty)
        elif health == "low_stock":
            total = rng.randint(out_of_stock_threshold + 1, low_stock_threshold)
        elif health == "out_of_stock":
            total = rng.randint(0, out_of_stock_threshold)
        else:  # overstock
            total = rng.randint(max_qty + 1, max_qty + 50)

        shelf_delta = round(total * 0.6)
        backroom_delta = total - shelf_delta

        # Inventory position
        self._ledger.assert_no_collision(
            entity_type="inventory_position",
            entity_id=composite_key,
            exists_fn=lambda: self._positions.get_by_sku_location(sku_id, store_id) is not None,
        )
        if not self._ledger.is_seeded("inventory_position", composite_key):
            self._positions.upsert_delta(
                sku_id=sku_id,
                location_id=store_id,
                shelf_delta=shelf_delta,
                backroom_delta=backroom_delta,
                event_id=f"seed-{seed_batch_id}-{composite_key}",
            )
            self._ledger.mark_seeded(
                entity_type="inventory_position", entity_id=composite_key, seed_batch_id=seed_batch_id
            )
        position = self._positions.get_by_sku_location(sku_id, store_id)

        # Product/location policy
        self._ledger.assert_no_collision(
            entity_type="product_location_policy",
            entity_id=composite_key,
            exists_fn=lambda: len(
                self._policy_service.list_policies(sku_id=sku_id, location_id=store_id)
            )
            > 0,
        )
        if not self._ledger.is_seeded("product_location_policy", composite_key):
            self._policy_service.upsert_policy(
                sku_id=sku_id,
                location_id=store_id,
                low_stock_threshold=low_stock_threshold,
                out_of_stock_threshold=out_of_stock_threshold,
                reorder_point=reorder_point,
                min_qty=min_qty,
                max_qty=max_qty,
                safety_stock=safety_stock,
                updated_by=self._actor_user_id,
            )
            self._ledger.mark_seeded(
                entity_type="product_location_policy", entity_id=composite_key, seed_batch_id=seed_batch_id
            )
        policy = self._policy_service.list_policies(sku_id=sku_id, location_id=store_id)[0]

        # Stock alert (only when the health roll actually breached a threshold)
        severity: Severity | None = None
        if total <= out_of_stock_threshold:
            severity = Severity.OUT_OF_STOCK
        elif total <= low_stock_threshold:
            severity = Severity.LOW_STOCK

        if severity is not None:
            self._ledger.assert_no_collision(
                entity_type="stock_alert",
                entity_id=composite_key,
                exists_fn=lambda: self._alerts.find_active_for_sku_location(sku_id, store_id)
                is not None,
            )
            if not self._ledger.is_seeded("stock_alert", composite_key):
                self._alerts.create(
                    sku_id=sku_id,
                    location_id=store_id,
                    severity=severity,
                    routing_channel=resolve_channel(severity),
                )
                self._ledger.mark_seeded(
                    entity_type="stock_alert", entity_id=composite_key, seed_batch_id=seed_batch_id
                )

        # Replenishment recommendation (engine decides whether a reorder is warranted)
        if not self._ledger.is_seeded("replenishment_recommendation", composite_key):
            recommendation = self._replenishment_engine.generate_recommendation(position, policy)
            if recommendation is not None:
                self._ledger.mark_seeded(
                    entity_type="replenishment_recommendation",
                    entity_id=composite_key,
                    seed_batch_id=seed_batch_id,
                )

        # Demand forecast (always produced, with a data-quality error indicator)
        if not self._ledger.is_seeded("demand_forecast", composite_key):
            base_demand = rng.uniform(5.0, 120.0)
            history = [max(0.0, round(rng.gauss(base_demand, base_demand * 0.2), 1)) for _ in range(12)]
            today = date.today()
            self._forecasting_engine.generate_forecast(
                sku_id=sku_id,
                location_id=store_id,
                history=history,
                period_start=today,
                period_end=today + timedelta(days=6),
            )
            self._ledger.mark_seeded(
                entity_type="demand_forecast", entity_id=composite_key, seed_batch_id=seed_batch_id
            )

    def _seed_store_priority_profile(
        self, store_id: str, region: str, consumption_rate: float, seed_batch_id: str
    ) -> None:
        self._ledger.assert_no_collision(
            entity_type="store_priority_profile",
            entity_id=store_id,
            exists_fn=lambda: self._session.query(StorePriorityProfile)
            .filter_by(store_id=store_id)
            .one_or_none()
            is not None,
        )
        if self._ledger.is_seeded("store_priority_profile", store_id):
            return
        profile = StorePriorityProfile(
            id=str(uuid.uuid4()),
            store_id=store_id,
            region=region,
            recent_consumption_rate=consumption_rate,
            region_weight=0.5,
            consumption_weight=0.5,
            current_priority_rank=0,
        )
        self._session.add(profile)
        self._session.flush()
        self._ledger.mark_seeded(
            entity_type="store_priority_profile", entity_id=store_id, seed_batch_id=seed_batch_id
        )

    def _seed_transfers(
        self, sku_to_stores: dict[str, list[str]], seed_batch_id: str
    ) -> None:
        for sku_id, stores in sku_to_stores.items():
            if len(stores) < 2:
                continue
            candidate_stores = stores[:_MAX_STORES_PER_SKU_FOR_TRANSFER_PAIRING]
            for source_id, destination_id in itertools.permutations(candidate_stores, 2):
                entity_id = f"{sku_id}::{source_id}::{destination_id}"
                if self._ledger.is_seeded("transfer_suggestion", entity_id):
                    continue
                source_position = self._positions.get_by_sku_location(sku_id, source_id)
                destination_position = self._positions.get_by_sku_location(sku_id, destination_id)
                if source_position is None or destination_position is None:
                    continue
                source_policy = self._first_policy(sku_id, source_id)
                destination_policy = self._first_policy(sku_id, destination_id)
                if source_policy is None or destination_policy is None:
                    continue

                destination_profile = (
                    self._session.query(StorePriorityProfile)
                    .filter_by(store_id=destination_id)
                    .one_or_none()
                )
                priority_rank = (
                    destination_profile.current_priority_rank if destination_profile else 0
                )

                suggestion = self._transfer_engine.generate_suggestion(
                    source_position=source_position,
                    source_policy=source_policy,
                    destination_position=destination_position,
                    destination_policy=destination_policy,
                    priority_rank=priority_rank,
                )
                if suggestion is not None:
                    self._ledger.mark_seeded(
                        entity_type="transfer_suggestion",
                        entity_id=entity_id,
                        seed_batch_id=seed_batch_id,
                    )

    def _first_policy(self, sku_id: str, location_id: str) -> ProductLocationPolicy | None:
        policies = self._policy_service.list_policies(sku_id=sku_id, location_id=location_id)
        return policies[0] if policies else None
