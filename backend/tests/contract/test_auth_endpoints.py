"""Contract tests for auth endpoints (T021, US1)."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.auth.models import UserAccount
from src.domain.auth.password_policy import hash_password


def _create_account(db_session, *, identifier: str = "admin_demo", password: str = "StrongPass!123") -> UserAccount:
    account = UserAccount(
        id="user-1",
        login_identifier=identifier,
        password_hash=hash_password(password),
        is_active=True,
        locked_until=None,
        failed_attempt_count_window=0,
        failed_attempt_window_started_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(account)
    db_session.flush()
    return account


def test_login_sets_session_cookie(client, db_session):
    _create_account(db_session)

    response = client.post(
        "/v1/auth/login",
        json={"identifier": "admin_demo", "password": "StrongPass!123"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "authenticated"
    assert "set-cookie" in response.headers


def test_login_rejects_invalid_credentials(client, db_session):
    _create_account(db_session)

    response = client.post(
        "/v1/auth/login",
        json={"identifier": "admin_demo", "password": "WrongPass!999"},
    )

    assert response.status_code == 401


def test_logout_revokes_session(client, db_session):
    _create_account(db_session)

    login = client.post(
        "/v1/auth/login",
        json={"identifier": "admin_demo", "password": "StrongPass!123"},
    )
    assert login.status_code == 200

    logout = client.post("/v1/auth/logout")
    assert logout.status_code == 200

    session_status = client.get("/v1/auth/session")
    assert session_status.status_code == 401
