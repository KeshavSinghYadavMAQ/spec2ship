"""Additional auth/session edge-case unit tests (T080)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.domain.auth.models import AuthSession, UserAccount
from src.domain.auth.password_policy import hash_password
from src.domain.auth.service import AuthService


def _seed_account(db_session) -> UserAccount:
    account = UserAccount(
        id="edge-user-1",
        login_identifier="edge-user",
        password_hash=hash_password("EdgePass!123"),
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


def test_expired_session_is_not_active(db_session):
    account = _seed_account(db_session)
    expired = AuthSession(
      id="sess-expired",
      user_account_id=account.id,
      created_at=datetime.now(UTC) - timedelta(hours=2),
      expires_at=datetime.now(UTC) - timedelta(minutes=5),
      revoked_at=None,
      last_seen_at=datetime.now(UTC) - timedelta(hours=1),
    )
    db_session.add(expired)
    db_session.flush()

    assert AuthService(db_session).get_active_session("sess-expired") is None


def test_revoked_session_is_not_active(db_session):
    account = _seed_account(db_session)
    revoked = AuthSession(
      id="sess-revoked",
      user_account_id=account.id,
      created_at=datetime.now(UTC) - timedelta(hours=1),
      expires_at=datetime.now(UTC) + timedelta(hours=1),
      revoked_at=datetime.now(UTC),
      last_seen_at=datetime.now(UTC),
    )
    db_session.add(revoked)
    db_session.flush()

    assert AuthService(db_session).get_active_session("sess-revoked") is None
