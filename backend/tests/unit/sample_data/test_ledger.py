"""Unit tests for `SeedLedger` (T051, US1, FR-003, FR-011, FR-012).

Covers `is_seeded`/`mark_seeded` resumability, `assert_no_collision` fail-fast behavior,
and the `counts_by_entity_type`/`entity_ids_by_type` read helpers used by the seed/clear
services and the admin status endpoint.
"""

from __future__ import annotations

import pytest
from src.domain.sample_data.ledger import SeedIdentifierCollisionError, SeedLedger


def test_is_seeded_false_for_unknown_entity(db_session):
    ledger = SeedLedger(db_session)
    assert ledger.is_seeded("inventory_position", "SKU-1::STORE-1") is False


def test_mark_seeded_then_is_seeded_true(db_session):
    ledger = SeedLedger(db_session)
    ledger.mark_seeded(
        entity_type="inventory_position", entity_id="SKU-1::STORE-1", seed_batch_id="batch-1"
    )
    assert ledger.is_seeded("inventory_position", "SKU-1::STORE-1") is True


def test_mark_seeded_is_idempotent_and_keeps_original_batch(db_session):
    ledger = SeedLedger(db_session)
    first = ledger.mark_seeded(
        entity_type="inventory_position", entity_id="SKU-1::STORE-1", seed_batch_id="batch-1"
    )
    second = ledger.mark_seeded(
        entity_type="inventory_position", entity_id="SKU-1::STORE-1", seed_batch_id="batch-2"
    )
    assert second.id == first.id
    assert second.seed_batch_id == "batch-1"


def test_assert_no_collision_passes_when_no_real_record_exists(db_session):
    ledger = SeedLedger(db_session)
    ledger.assert_no_collision(
        entity_type="inventory_position", entity_id="SKU-1::STORE-1", exists_fn=lambda: False
    )  # should not raise


def test_assert_no_collision_passes_when_entity_already_ledger_tracked(db_session):
    ledger = SeedLedger(db_session)
    ledger.mark_seeded(
        entity_type="inventory_position", entity_id="SKU-1::STORE-1", seed_batch_id="batch-1"
    )
    # exists_fn would return True (record now exists) but it's already ours - no raise.
    ledger.assert_no_collision(
        entity_type="inventory_position", entity_id="SKU-1::STORE-1", exists_fn=lambda: True
    )


def test_assert_no_collision_raises_for_genuine_non_seed_record(db_session):
    ledger = SeedLedger(db_session)
    with pytest.raises(SeedIdentifierCollisionError) as exc_info:
        ledger.assert_no_collision(
            entity_type="inventory_position", entity_id="SKU-1::STORE-1", exists_fn=lambda: True
        )
    assert exc_info.value.entity_type == "inventory_position"
    assert exc_info.value.entity_id == "SKU-1::STORE-1"


def test_counts_by_entity_type_aggregates_across_types(db_session):
    ledger = SeedLedger(db_session)
    ledger.mark_seeded(entity_type="inventory_position", entity_id="a", seed_batch_id="batch-1")
    ledger.mark_seeded(entity_type="inventory_position", entity_id="b", seed_batch_id="batch-1")
    ledger.mark_seeded(entity_type="stock_alert", entity_id="c", seed_batch_id="batch-1")

    counts = ledger.counts_by_entity_type("batch-1")
    assert counts == {"inventory_position": 2, "stock_alert": 1}


def test_counts_by_entity_type_filters_by_batch(db_session):
    ledger = SeedLedger(db_session)
    ledger.mark_seeded(entity_type="inventory_position", entity_id="a", seed_batch_id="batch-1")
    ledger.mark_seeded(entity_type="inventory_position", entity_id="b", seed_batch_id="batch-2")

    assert ledger.counts_by_entity_type("batch-1") == {"inventory_position": 1}
    assert ledger.counts_by_entity_type() == {"inventory_position": 2}


def test_entity_ids_by_type_returns_only_matching_type(db_session):
    ledger = SeedLedger(db_session)
    ledger.mark_seeded(entity_type="inventory_position", entity_id="a", seed_batch_id="batch-1")
    ledger.mark_seeded(entity_type="stock_alert", entity_id="c", seed_batch_id="batch-1")

    assert ledger.entity_ids_by_type("inventory_position") == ["a"]


def test_all_records_and_delete_record(db_session):
    ledger = SeedLedger(db_session)
    record = ledger.mark_seeded(
        entity_type="inventory_position", entity_id="a", seed_batch_id="batch-1"
    )
    assert len(ledger.all_records()) == 1

    ledger.delete_record(record)
    assert ledger.all_records() == []
