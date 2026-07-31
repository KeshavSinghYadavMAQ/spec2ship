"""Harness coverage for auth + RLS audit observability (T082)."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.admin.audit import AuditLogEntry
from src.domain.admin.rbac import UserRoleAssignment
from src.domain.auth.models import UserAccount
from src.domain.auth.password_policy import hash_password
from src.domain.inventory.models import InventoryPosition


def test_auth_and_rls_events_are_auditable(client, db_session):
    db_session.add(
        UserRoleAssignment(
            id="audit-role-1",
            user_id="audit-user",
            role="store_manager",
            location_scope={"location_ids": ["STORE-A"]},
        )
    )
    db_session.add(
        UserAccount(
            id="audit-user",
            login_identifier="audit-user",
            password_hash=hash_password("AuditPass!123"),
            is_active=True,
            locked_until=None,
            failed_attempt_count_window=0,
            failed_attempt_window_started_at=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db_session.add(
        InventoryPosition(
            id="audit-pos-b",
            sku_id="SKU-1",
            location_id="STORE-B",
            shelf_quantity=5,
            backroom_quantity=5,
            last_event_id=None,
            freshness_at=datetime.now(UTC),
            data_freshness_warning=False,
        )
    )
    db_session.flush()

    bad_login = client.post("/v1/auth/login", json={"identifier": "audit-user", "password": "bad"})
    assert bad_login.status_code == 401

    good_login = client.post(
        "/v1/auth/login",
        json={"identifier": "audit-user", "password": "AuditPass!123"},
    )
    assert good_login.status_code == 200

    denied = client.get(
        "/v1/inventory/positions/audit-pos-b",
        headers={"X-User-Id": "audit-user", "X-User-Role": "store_manager"},
    )
    assert denied.status_code == 404

    logout = client.post("/v1/auth/logout")
    assert logout.status_code == 200

    actions = {entry.action for entry in db_session.query(AuditLogEntry).all()}
    assert "login_failure" in actions
    assert "login_success" in actions
    assert "logout" in actions
    assert "rls_denied" in actions
