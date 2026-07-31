"""Analytics API router (T092, US6, FR-010, FR-011).

`GET /v1/analytics/kpis` with region/store/category/time filters. Returns a single-item
list containing the aggregated `KPIView` for the requested filter set (kept as a list to
match the contract's array response shape and allow future multi-slice breakdowns).
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.analytics.service import KPIAggregationService, KPIView
from src.domain.security.scope_service import ScopeResolutionService
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpis", response_model=list[KPIView])
async def get_kpis(
    region: str | None = None,
    store_id: str | None = None,
    category: str | None = None,
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(*Role)),
) -> list[KPIView]:
    def _query() -> list[KPIView]:
        scope = ScopeResolutionService(session).resolve_for_user(current_user.user_id)
        service = KPIAggregationService(session)
        return [
            service.compute(
                region=region,
                store_id=store_id,
                category=category,
                date_from=from_,
                date_to=to,
                scoped_store_ids=set(scope.location_ids),
                all_locations=scope.all_locations,
            )
        ]

    return await run_in_threadpool(_query)
