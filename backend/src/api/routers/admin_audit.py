"""Admin audit-log API router (T095, FR-014, FR-018).

`GET /v1/admin/audit-log` with `entity_type`/`entity_id` filters. Read-only surface for
reviewing who changed policies, thresholds, and other admin-governed configuration.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.audit import AuditLogEntryRead, AuditLogWriter
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/admin/audit-log", tags=["admin"])


@router.get("", response_model=list[AuditLogEntryRead])
async def list_audit_log(
    entity_type: str | None = None,
    entity_id: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[AuditLogEntryRead]:
    def _query() -> list[AuditLogEntryRead]:
        writer = AuditLogWriter(session)
        return [
            AuditLogEntryRead.model_validate(entry)
            for entry in writer.list_entries(entity_type=entity_type, entity_id=entity_id)
        ]

    return await run_in_threadpool(_query)
