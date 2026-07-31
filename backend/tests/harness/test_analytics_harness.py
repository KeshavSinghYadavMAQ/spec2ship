"""Harness scenario for User Story 6 (T090): happy path, failure path, data-quality edge
case (Constitution III non-negotiable)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.alerting.models import AlertStatus, StockAlert
from src.domain.analytics.service import KPIAggregationService
from src.domain.inventory.models import InventoryPosition

from tests.harness.runner import HarnessScenario, ScenarioKind, run_scenarios


def test_analytics_harness_scenarios(db_session):
    service = KPIAggregationService(db_session)

    def happy_path() -> None:
        db_session.add(
            InventoryPosition(
                id=str(uuid.uuid4()),
                sku_id="SKU-A1",
                location_id="STORE-A1",
                shelf_quantity=50,
                backroom_quantity=0,
                freshness_at=datetime.now(UTC),
            )
        )
        db_session.flush()
        kpi = service.compute(store_id="STORE-A1")
        assert kpi.total_positions == 1
        assert kpi.fill_rate == 1.0, "no open alerts means full fill rate"

    def failure_path() -> None:
        # Unknown/empty scope must not raise; it should return a well-formed KPIView
        # with zeroed metrics instead of erroring.
        kpi = service.compute(region="no-such-region")
        assert kpi.total_positions == 0
        assert kpi.open_alert_count == 0
        assert kpi.average_alert_age_hours == 0.0

    def data_quality_edge_case() -> None:
        # A stale open alert should raise average_alert_age_hours without breaking
        # the aggregation despite no matching recommendation/forecast rows.
        db_session.add(
            InventoryPosition(
                id=str(uuid.uuid4()),
                sku_id="SKU-A2",
                location_id="STORE-A2",
                shelf_quantity=0,
                backroom_quantity=0,
                freshness_at=datetime.now(UTC),
            )
        )
        db_session.add(
            StockAlert(
                id=str(uuid.uuid4()),
                sku_id="SKU-A2",
                location_id="STORE-A2",
                severity="out_of_stock",
                status=AlertStatus.OPEN.value,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
        db_session.flush()
        kpi = service.compute(store_id="STORE-A2")
        assert kpi.open_alert_count == 1
        assert kpi.fill_rate == 0.0
        assert kpi.average_alert_age_hours >= 0.0

    run_scenarios(
        [
            HarnessScenario(
                "healthy store shows full fill rate", ScenarioKind.HAPPY_PATH, happy_path
            ),
            HarnessScenario(
                "unknown scope returns zeroed KPIs", ScenarioKind.FAILURE_PATH, failure_path
            ),
            HarnessScenario(
                "open alert lowers fill rate without crashing",
                ScenarioKind.DATA_QUALITY_EDGE_CASE,
                data_quality_edge_case,
            ),
        ]
    )
