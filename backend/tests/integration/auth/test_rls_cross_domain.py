"""Cross-domain RLS integration checks (T034, US2)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from src.domain.admin.rbac import UserRoleAssignment
from src.domain.alerting.models import StockAlert
from src.domain.forecasting.models import DemandForecast
from src.domain.replenishment.models import ReplenishmentRecommendation
from src.domain.transfer_balance.models import TransferSuggestion
from src.domain.transfer_balance.priority_models import StorePriorityProfile

_HEADERS = {"X-User-Id": "mgr-a", "X-User-Role": "store_manager"}


def _seed_scope(db_session) -> None:
    db_session.add(
        UserRoleAssignment(
            id="ura-x",
            user_id="mgr-a",
            role="store_manager",
            location_scope={"location_ids": ["STORE-A"]},
        )
    )


def _seed_cross_domain_rows(db_session) -> None:
    now = datetime.now(UTC)
    db_session.add_all(
        [
            StockAlert(
                id="alert-a",
                sku_id="SKU-1",
                location_id="STORE-A",
                severity="low_stock",
                status="Open",
                owner_user_id=None,
                routing_channel=None,
                suppressed_until=None,
                created_at=now,
                updated_at=now,
            ),
            StockAlert(
                id="alert-b",
                sku_id="SKU-2",
                location_id="STORE-B",
                severity="out_of_stock",
                status="Open",
                owner_user_id=None,
                routing_channel=None,
                suppressed_until=None,
                created_at=now,
                updated_at=now,
            ),
            ReplenishmentRecommendation(
                id="rec-a",
                sku_id="SKU-1",
                location_id="STORE-A",
                recommended_quantity=10,
                recommended_by_date=date.today(),
                policy_snapshot={},
                rationale={"narration": "in scope"},
                status="proposed",
                override_reason=None,
                actionability_rating=None,
                created_at=now,
            ),
            ReplenishmentRecommendation(
                id="rec-b",
                sku_id="SKU-2",
                location_id="STORE-B",
                recommended_quantity=8,
                recommended_by_date=date.today(),
                policy_snapshot={},
                rationale={"narration": "out scope"},
                status="proposed",
                override_reason=None,
                actionability_rating=None,
                created_at=now,
            ),
            DemandForecast(
                id="fc-a",
                sku_id="SKU-1",
                location_id="STORE-A",
                period_start=date.today(),
                period_end=date.today(),
                forecast_quantity=15.0,
                trend_factor=1.0,
                seasonality_factor=1.0,
                promotion_factor=1.0,
                history_points_used=30,
                error_indicator="low",
                factors={},
                narration=None,
                created_at=now,
            ),
            DemandForecast(
                id="fc-b",
                sku_id="SKU-2",
                location_id="STORE-B",
                period_start=date.today(),
                period_end=date.today(),
                forecast_quantity=9.0,
                trend_factor=1.0,
                seasonality_factor=1.0,
                promotion_factor=1.0,
                history_points_used=30,
                error_indicator="low",
                factors={},
                narration=None,
                created_at=now,
            ),
            TransferSuggestion(
                id="ts-a",
                sku_id="SKU-1",
                source_location_id="STORE-A",
                destination_location_id="STORE-C",
                suggested_quantity=4,
                feasibility_status="feasible",
                feasibility_reason="ok",
                priority_rank=1,
                status="proposed",
                factors={},
                created_at=now,
            ),
            TransferSuggestion(
                id="ts-b",
                sku_id="SKU-2",
                source_location_id="STORE-B",
                destination_location_id="STORE-C",
                suggested_quantity=5,
                feasibility_status="feasible",
                feasibility_reason="ok",
                priority_rank=2,
                status="proposed",
                factors={},
                created_at=now,
            ),
            StorePriorityProfile(
                id="sp-a",
                store_id="STORE-A",
                region="west",
                recent_consumption_rate=4.5,
                region_weight=0.5,
                consumption_weight=0.5,
                current_priority_rank=1,
                priority_factors=None,
                narration=None,
            ),
            StorePriorityProfile(
                id="sp-b",
                store_id="STORE-B",
                region="west",
                recent_consumption_rate=3.5,
                region_weight=0.5,
                consumption_weight=0.5,
                current_priority_rank=2,
                priority_factors=None,
                narration=None,
            ),
        ]
    )
    db_session.flush()


def test_cross_domain_lists_are_scope_filtered(client, db_session):
    _seed_scope(db_session)
    _seed_cross_domain_rows(db_session)

    alerts = client.get("/v1/alerts", headers=_HEADERS)
    recs = client.get("/v1/replenishment/recommendations", headers=_HEADERS)
    forecasts = client.get("/v1/forecasts", headers=_HEADERS)
    transfers = client.get("/v1/transfers/suggestions", headers=_HEADERS)
    priorities = client.get("/v1/store-priority/profiles", headers=_HEADERS)

    assert alerts.status_code == 200
    assert all(item["location_id"] == "STORE-A" for item in alerts.json())

    assert recs.status_code == 200
    assert all(item["location_id"] == "STORE-A" for item in recs.json())

    assert forecasts.status_code == 200
    assert all(item["location_id"] == "STORE-A" for item in forecasts.json())

    assert transfers.status_code == 200
    assert all(
        item["source_location_id"] == "STORE-A" or item["destination_location_id"] == "STORE-A"
        for item in transfers.json()
    )

    assert priorities.status_code == 200
    assert all(item["store_id"] == "STORE-A" for item in priorities.json())
