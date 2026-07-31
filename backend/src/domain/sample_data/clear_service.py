"""`SampleDataClearService` (T021, US1, FR-011).

Deletes exactly the domain records tracked in the seed-record ledger for a given
`entity_type`/`entity_id`, then removes the corresponding ledger rows themselves. Genuine
(non-seed) data is never touched because only ledger-tracked natural keys are ever
deleted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.domain.admin.audit import AuditLogWriter
from src.domain.alerting.models import StockAlert
from src.domain.alerting.policy_models import ProductLocationPolicy
from src.domain.forecasting.models import DemandForecast
from src.domain.inventory.models import InventoryPosition
from src.domain.replenishment.models import ReplenishmentRecommendation
from src.domain.sample_data.ledger import SeedLedger
from src.domain.transfer_balance.models import TransferSuggestion
from src.domain.transfer_balance.priority_models import StorePriorityProfile


@dataclass
class ClearRunResult:
    removed_counts_by_entity_type: dict[str, int]
    cleared_at: datetime
    remaining_ledger_rows: int = field(default=0)


def _split_composite(entity_id: str) -> list[str]:
    return entity_id.split("::")


class SampleDataClearService:
    def __init__(self, session: Session, *, actor_user_id: str = "system-seed") -> None:
        self._session = session
        self._actor_user_id = actor_user_id
        self._ledger = SeedLedger(session)
        self._audit = AuditLogWriter(session)

    def clear(self) -> ClearRunResult:
        removed_counts: dict[str, int] = {}
        for record in self._ledger.all_records():
            self._delete_domain_record(record.entity_type, record.entity_id)
            removed_counts[record.entity_type] = removed_counts.get(record.entity_type, 0) + 1
            self._ledger.delete_record(record)

        cleared_at = datetime.now(UTC)
        self._audit.record(
            actor_user_id=self._actor_user_id,
            action="sample_data.clear",
            entity_type="sample_data_seed_batch",
            entity_id="all",
            after={"removed_counts_by_entity_type": removed_counts},
        )
        return ClearRunResult(
            removed_counts_by_entity_type=removed_counts,
            cleared_at=cleared_at,
            remaining_ledger_rows=len(self._ledger.all_records()),
        )

    def _delete_domain_record(self, entity_type: str, entity_id: str) -> None:
        parts = _split_composite(entity_id)

        if entity_type == "inventory_position" and len(parts) == 2:
            sku_id, location_id = parts
            self._session.query(InventoryPosition).filter_by(
                sku_id=sku_id, location_id=location_id
            ).delete()
        elif entity_type == "product_location_policy" and len(parts) == 2:
            sku_id, location_id = parts
            self._session.query(ProductLocationPolicy).filter_by(
                sku_id=sku_id, location_id=location_id
            ).delete()
        elif entity_type == "stock_alert" and len(parts) == 2:
            sku_id, location_id = parts
            self._session.query(StockAlert).filter_by(
                sku_id=sku_id, location_id=location_id
            ).delete()
        elif entity_type == "replenishment_recommendation" and len(parts) == 2:
            sku_id, location_id = parts
            self._session.query(ReplenishmentRecommendation).filter_by(
                sku_id=sku_id, location_id=location_id
            ).delete()
        elif entity_type == "demand_forecast" and len(parts) == 2:
            sku_id, location_id = parts
            self._session.query(DemandForecast).filter_by(
                sku_id=sku_id, location_id=location_id
            ).delete()
        elif entity_type == "transfer_suggestion" and len(parts) == 3:
            sku_id, source_id, destination_id = parts
            self._session.query(TransferSuggestion).filter_by(
                sku_id=sku_id, source_location_id=source_id, destination_location_id=destination_id
            ).delete()
        elif entity_type == "store_priority_profile":
            self._session.query(StorePriorityProfile).filter_by(store_id=entity_id).delete()

        self._session.flush()
