"""Seed-record ledger repository (T006, US1, FR-003, FR-011, FR-012).

Higher-level idempotency helpers on top of `SampleDataSeedRecordRepository`:
- `is_seeded` / `mark_seeded` support resumability (FR-003): a batched seed run can skip
  entities it already recorded.
- `assert_no_collision` supports the fail-fast data-quality edge case (FR-012): seeding
  must never silently overwrite a pre-existing, non-seed record that happens to share a
  natural key.
- `entity_ids_by_type` / `delete_all` support the clear/reset action (FR-011).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.sample_data.models import SampleDataSeedRecord, SampleDataSeedRecordRepository


class SeedIdentifierCollisionError(Exception):
    """Raised when a to-be-seeded natural key already exists as genuine (non-seed) data."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            f"Refusing to seed {entity_type!r} entity_id={entity_id!r}: a record with this "
            "identifier already exists and is not tracked as sample data"
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class SeedLedger:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = SampleDataSeedRecordRepository(session)

    def is_seeded(self, entity_type: str, entity_id: str) -> bool:
        return self._repo.find(entity_type, entity_id) is not None

    def mark_seeded(self, *, entity_type: str, entity_id: str, seed_batch_id: str) -> SampleDataSeedRecord:
        existing = self._repo.find(entity_type, entity_id)
        if existing is not None:
            return existing
        return self._repo.create(
            entity_type=entity_type, entity_id=entity_id, seed_batch_id=seed_batch_id
        )

    def assert_no_collision(self, *, entity_type: str, entity_id: str, exists_fn) -> None:
        """`exists_fn` is a zero-arg callable that returns True if a real domain record
        already exists for this natural key. Only raises when the record exists AND is
        not already ledger-tracked (i.e. it is genuine, non-seed data)."""
        if self.is_seeded(entity_type, entity_id):
            return
        if exists_fn():
            raise SeedIdentifierCollisionError(entity_type, entity_id)

    def counts_by_entity_type(self, seed_batch_id: str | None = None) -> dict[str, int]:
        records = self._repo.list_all()
        counts: dict[str, int] = {}
        for record in records:
            if seed_batch_id is not None and record.seed_batch_id != seed_batch_id:
                continue
            counts[record.entity_type] = counts.get(record.entity_type, 0) + 1
        return counts

    def entity_ids_by_type(self, entity_type: str) -> list[str]:
        return [record.entity_id for record in self._repo.list_by_entity_type(entity_type)]

    def all_records(self) -> list[SampleDataSeedRecord]:
        return self._repo.list_all()

    def delete_record(self, record: SampleDataSeedRecord) -> None:
        self._repo.delete(record)
