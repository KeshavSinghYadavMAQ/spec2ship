"""Admin sample-data lifecycle API router (T022, US1, FR-001 to FR-005, FR-011).

`POST /v1/admin/sample-data/seed`, `GET /v1/admin/sample-data/status`,
`DELETE /v1/admin/sample-data` - all gated by `require_non_production_admin` (T007).
Seeding/clearing run synchronously within the request (bulk operations complete well
within the request timeout at pilot scale per T049's performance validation) rather than
via a background job queue, keeping this v1 surface simple per the constitution's
guidance to avoid speculative infrastructure.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.rbac import CurrentUser
from src.domain.sample_data.clear_service import SampleDataClearService
from src.domain.sample_data.guards import require_non_production_admin
from src.domain.sample_data.ledger import SeedLedger
from src.domain.sample_data.seed_service import (
    DEFAULT_ASSORTMENT_SIZE,
    DEFAULT_CATALOG_SIZE,
    DEFAULT_STORE_COUNT,
    SampleDataSeedService,
)
from src.infrastructure.db import get_db_session
from src.schemas.sample_data import ClearRunSummary, SeedRunStatus, SeedRunSummary

router = APIRouter(prefix="/admin/sample-data", tags=["admin-sample-data"])


@router.post("/seed", response_model=SeedRunSummary, status_code=202)
async def seed_sample_data(
    store_count: int = DEFAULT_STORE_COUNT,
    catalog_size: int = DEFAULT_CATALOG_SIZE,
    assortment_size: int = DEFAULT_ASSORTMENT_SIZE,
    current_user: CurrentUser = Depends(require_non_production_admin),
    session: Session = Depends(get_db_session),
) -> SeedRunSummary:
    """`store_count`/`catalog_size`/`assortment_size` default to pilot scale (1,000+
    stores, 100,000+ SKUs, SC-001/SC-006) but are overridable via query params for
    smaller demo/test runs."""

    def _run() -> SeedRunSummary:
        service = SampleDataSeedService(session, actor_user_id=current_user.user_id)
        result = service.seed(
            store_count=store_count, catalog_size=catalog_size, assortment_size=assortment_size
        )
        return SeedRunSummary(
            seed_batch_id=result.seed_batch_id,
            status=SeedRunStatus.COMPLETED,
            counts_by_entity_type=result.counts_by_entity_type,
            started_at=result.started_at,
            completed_at=result.completed_at,
        )

    return await run_in_threadpool(_run)


@router.get("/status", response_model=SeedRunSummary)
async def get_sample_data_status(
    current_user: CurrentUser = Depends(require_non_production_admin),
    session: Session = Depends(get_db_session),
) -> SeedRunSummary:
    def _query() -> SeedRunSummary:
        ledger = SeedLedger(session)
        records = ledger.all_records()
        if not records:
            raise HTTPException(
                status_code=404, detail="No seeding run has ever been executed in this environment"
            )
        latest_batch_id = max(records, key=lambda record: record.created_at).seed_batch_id
        batch_records = [record for record in records if record.seed_batch_id == latest_batch_id]
        return SeedRunSummary(
            seed_batch_id=latest_batch_id,
            status=SeedRunStatus.COMPLETED,
            counts_by_entity_type=ledger.counts_by_entity_type(latest_batch_id),
            started_at=min(record.created_at for record in batch_records),
            completed_at=max(record.created_at for record in batch_records),
        )

    return await run_in_threadpool(_query)


@router.delete("", response_model=ClearRunSummary)
async def clear_sample_data(
    current_user: CurrentUser = Depends(require_non_production_admin),
    session: Session = Depends(get_db_session),
) -> ClearRunSummary:
    def _run() -> ClearRunSummary:
        service = SampleDataClearService(session, actor_user_id=current_user.user_id)
        result = service.clear()
        return ClearRunSummary(
            removed_counts_by_entity_type=result.removed_counts_by_entity_type,
            cleared_at=result.cleared_at,
        )

    return await run_in_threadpool(_run)
