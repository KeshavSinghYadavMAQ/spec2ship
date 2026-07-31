"""Auth lifecycle harness scenario (T023, US1)."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.auth.models import UserAccount
from src.domain.auth.password_policy import hash_password


def test_login_logout_and_session_lifecycle(client, db_session):
    account = UserAccount(
        id="harness-user-1",
        login_identifier="regional_mgr_west",
        password_hash=hash_password("RegionalPass!123"),
        is_active=True,
        locked_until=None,
        failed_attempt_count_window=0,
        failed_attempt_window_started_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(account)
    db_session.flush()

    login = client.post(
        "/v1/auth/login",
        json={"identifier": "regional_mgr_west", "password": "RegionalPass!123"},
    )
    assert login.status_code == 200

    active = client.get("/v1/auth/session")
    assert active.status_code == 200
    assert active.json()["authenticated"] is True

    logout = client.post("/v1/auth/logout")
    assert logout.status_code == 200

    expired = client.get("/v1/auth/session")
    assert expired.status_code == 401
