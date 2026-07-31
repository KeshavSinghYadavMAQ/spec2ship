"""Alerting API router (T046, US2).

`GET /v1/alerts` and `POST /v1/alerts/{alertId}/transition` (FR-002, FR-003).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.alerting.models import (
    AlertStatus,
    InvalidTransitionError,
    StockAlertRead,
    StockAlertRepository,
)
from src.infrastructure.db import get_db_session
from src.schemas.errors import ProblemDetail

router = APIRouter(prefix="/alerts", tags=["alerting"])


class TransitionRequest(BaseModel):
    status: AlertStatus


@router.get("", response_model=list[StockAlertRead])
async def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[StockAlertRead]:
    def _query() -> list[StockAlertRead]:
        repo = StockAlertRepository(session)
        return [StockAlertRead.model_validate(a) for a in repo.list(status=status, severity=severity)]

    return await run_in_threadpool(_query)


@router.post("/{alert_id}/transition", response_model=StockAlertRead)
async def transition_alert(
    alert_id: str,
    body: TransitionRequest,
    session: Session = Depends(get_db_session),
    _current_user: CurrentUser = Depends(require_role(*Role)),
) -> StockAlertRead:
    def _transition() -> StockAlertRead:
        repo = StockAlertRepository(session)
        alert = repo.get(alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="Alert not found")
        try:
            alert.transition_to(body.status)
        except InvalidTransitionError as exc:
            raise HTTPException(
                status_code=409,
                detail=ProblemDetail(
                    title="Invalid lifecycle transition", status=409, detail=str(exc)
                ).model_dump(),
            ) from exc
        return StockAlertRead.model_validate(alert)

    return await run_in_threadpool(_transition)
