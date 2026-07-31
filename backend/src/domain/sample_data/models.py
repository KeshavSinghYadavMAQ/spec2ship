"""`SampleDataSeedRecord` ledger model (T005, US1, FR-003, FR-011).

Standalone, domain-agnostic ledger table: records exactly which existing domain records
were created by a sample-data seeding run so the clear/reset action can remove precisely
those records without a physical foreign key coupling to every domain table (research.md
item 2 - isolation decision).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class SampleDataSeedRecord(Base):
    __tablename__ = "sample_data_seed_records"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_sample_data_seed_entity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(256), index=True)
    seed_batch_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SampleDataSeedRecordRead(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    seed_batch_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SampleDataSeedRecordRepository:
    """Thin persistence layer over `SampleDataSeedRecord`; higher-level idempotency and
    query helpers live in `ledger.py`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find(self, entity_type: str, entity_id: str) -> SampleDataSeedRecord | None:
        return (
            self._session.query(SampleDataSeedRecord)
            .filter_by(entity_type=entity_type, entity_id=entity_id)
            .one_or_none()
        )

    def create(
        self, *, entity_type: str, entity_id: str, seed_batch_id: str
    ) -> SampleDataSeedRecord:
        record = SampleDataSeedRecord(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            seed_batch_id=seed_batch_id,
            created_at=datetime.now(UTC),
        )
        self._session.add(record)
        self._session.flush()
        return record

    def list_all(self) -> list[SampleDataSeedRecord]:
        return self._session.query(SampleDataSeedRecord).all()

    def list_by_entity_type(self, entity_type: str) -> list[SampleDataSeedRecord]:
        return (
            self._session.query(SampleDataSeedRecord)
            .filter_by(entity_type=entity_type)
            .all()
        )

    def delete(self, record: SampleDataSeedRecord) -> None:
        self._session.delete(record)
        self._session.flush()
