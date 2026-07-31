"""Admin product-location policy API router (T078, US7, FR-016, FR-017, FR-018).

`GET`/`POST /v1/admin/product-location-policies`. Write access requires the `admin`
role (FR-013); validation failures return 422 and edit-lock conflicts return 409, both
as `ProblemDetail` bodies.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.alerting.policy_models import ProductLocationPolicyRead
from src.domain.alerting.policy_service import (
    PolicyEditLockedError,
    PolicyService,
    PolicyValidationError,
)
from src.infrastructure.db import get_db_session
from src.schemas.errors import ProblemDetail

router = APIRouter(prefix="/admin/product-location-policies", tags=["admin"])


class ProductLocationPolicyInput(BaseModel):
    sku_id: str
    location_id: str
    low_stock_threshold: int
    out_of_stock_threshold: int = 0
    reorder_point: int = 0
    min_qty: int = 0
    max_qty: int = 0
    safety_stock: int = 0


@router.get("", response_model=list[ProductLocationPolicyRead])
async def list_policies(
    sku_id: str | None = None,
    location_id: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[ProductLocationPolicyRead]:
    def _query() -> list[ProductLocationPolicyRead]:
        service = PolicyService(session)
        return [
            ProductLocationPolicyRead.model_validate(p)
            for p in service.list_policies(sku_id=sku_id, location_id=location_id)
        ]

    return await run_in_threadpool(_query)


@router.post("", response_model=ProductLocationPolicyRead)
async def upsert_policy(
    body: ProductLocationPolicyInput,
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(Role.ADMIN)),
) -> ProductLocationPolicyRead:
    def _upsert() -> ProductLocationPolicyRead:
        service = PolicyService(session)
        try:
            policy = service.upsert_policy(updated_by=current_user.user_id, **body.model_dump())
        except PolicyValidationError as exc:
            raise HTTPException(
                status_code=422,
                detail=ProblemDetail(
                    title="Invalid policy values",
                    status=422,
                    detail=str(exc),
                    errors={"policy": exc.errors},
                ).model_dump(),
            ) from exc
        except PolicyEditLockedError as exc:
            raise HTTPException(
                status_code=409,
                detail=ProblemDetail(
                    title="Policy locked by an in-flight evaluation", status=409, detail=str(exc)
                ).model_dump(),
            ) from exc
        return ProductLocationPolicyRead.model_validate(policy)

    return await run_in_threadpool(_upsert)
