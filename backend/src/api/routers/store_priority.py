"""Store-priority API router (T085, US8, FR-019, FR-020, FR-021).

`GET /v1/store-priority/profiles` and `POST /v1/store-priority/rules`. Rule updates
require an elevated role since they change org-wide restoration weighting (FR-013).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.transfer_balance.priority_models import StorePriorityProfileRead
from src.domain.transfer_balance.priority_service import StorePriorityService
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/store-priority", tags=["transfer-balance"])


class PriorityRulesRequest(BaseModel):
    region_weight: float | None = None
    consumption_weight: float | None = None


@router.get("/profiles", response_model=list[StorePriorityProfileRead])
async def list_store_priority_profiles(
    region: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[StorePriorityProfileRead]:
    def _query() -> list[StorePriorityProfileRead]:
        service = StorePriorityService(session)
        return [
            StorePriorityProfileRead.model_validate(p) for p in service.list_profiles(region=region)
        ]

    return await run_in_threadpool(_query)


@router.post("/rules", response_model=list[StorePriorityProfileRead])
async def update_priority_rules(
    body: PriorityRulesRequest,
    session: Session = Depends(get_db_session),
    _current_user: CurrentUser = Depends(require_role(Role.ADMIN, Role.REGIONAL_MANAGER)),
) -> list[StorePriorityProfileRead]:
    def _update() -> list[StorePriorityProfileRead]:
        service = StorePriorityService(session)
        profiles = service.update_rules(
            region_weight=body.region_weight, consumption_weight=body.consumption_weight
        )
        return [StorePriorityProfileRead.model_validate(p) for p in profiles]

    return await run_in_threadpool(_update)
