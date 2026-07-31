"""Audit log writer service (T023, FR-014, FR-018).

Every alert, recommendation, transfer, and admin configuration change that requires an
audit trail should call `AuditLogWriter.record(...)`. Backed by a dedicated
`AuditLogEntry` table so history survives independent of the entities it describes.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_user_id: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(36))
    before: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditLogEntryRead(BaseModel):
    id: str
    actor_user_id: str
    action: str
    entity_type: str
    entity_id: str
    before: dict[str, Any] | None
    after: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}



class AuditLogWriter:
    def __init__(self, session: Session) -> None:
        self._session = session

    def record(
        self,
        *,
        actor_user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=before,
            after=after,
            created_at=datetime.now(UTC),
        )
        self._session.add(entry)
        self._session.flush()
        return entry

    def list_entries(
        self, *, entity_type: str | None = None, entity_id: str | None = None
    ) -> list[AuditLogEntry]:
        query = self._session.query(AuditLogEntry)
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        return query.order_by(AuditLogEntry.created_at.desc()).all()

    def record_auth_event(
        self,
        *,
        event_type: str,
        actor_user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        return self.record(
            actor_user_id=actor_user_id or "anonymous",
            action=event_type,
            entity_type="auth_session",
            entity_id="auth",
            after=metadata,
        )

    def record_rls_denied(
        self,
        *,
        actor_user_id: str,
        resource_type: str,
        resource_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        return self.record(
            actor_user_id=actor_user_id,
            action="rls_denied",
            entity_type=resource_type,
            entity_id=resource_id,
            after=metadata,
        )
