"""Transfer-balance API router (T071, US5).

`GET /v1/transfers/suggestions` and `POST /v1/transfers/suggestions/{id}/status`
(FR-008, FR-009, FR-020). The status endpoint writes an audit trail entry (FR-014:
"auditable logs for ... transfers").
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.audit import AuditLogWriter
from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.transfer_balance.models import (
    TransferStatus,
    TransferSuggestionRead,
    TransferSuggestionRepository,
)
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/transfers", tags=["transfer-balance"])


class TransferStatusRequest(BaseModel):
    status: TransferStatus


@router.get("/suggestions", response_model=list[TransferSuggestionRead])
async def list_transfer_suggestions(
    session: Session = Depends(get_db_session),
) -> list[TransferSuggestionRead]:
    def _query() -> list[TransferSuggestionRead]:
        repo = TransferSuggestionRepository(session)
        return [TransferSuggestionRead.model_validate(s) for s in repo.list()]

    return await run_in_threadpool(_query)


@router.post("/suggestions/{suggestion_id}/status", response_model=TransferSuggestionRead)
async def update_transfer_status(
    suggestion_id: str,
    body: TransferStatusRequest,
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(*Role)),
) -> TransferSuggestionRead:
    def _update() -> TransferSuggestionRead:
        repo = TransferSuggestionRepository(session)
        suggestion = repo.get(suggestion_id)
        if suggestion is None:
            raise HTTPException(status_code=404, detail="Transfer suggestion not found")
        before_status = suggestion.status
        suggestion.status = body.status.value
        session.flush()

        AuditLogWriter(session).record(
            actor_user_id=current_user.user_id,
            action="transfer_suggestion_status_change",
            entity_type="transfer_suggestion",
            entity_id=suggestion.id,
            before={"status": before_status},
            after={"status": suggestion.status},
        )
        return TransferSuggestionRead.model_validate(suggestion)

    return await run_in_threadpool(_update)
