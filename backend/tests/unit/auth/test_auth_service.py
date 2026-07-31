"""Unit tests for auth service lockout and session issuance (T022, US1)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.domain.auth.models import UserAccount
from src.domain.auth.password_policy import hash_password
from src.domain.auth.service import AccountLockedError, AuthService, InvalidCredentialsError


def _add_account(db_session) -> UserAccount:
    account = UserAccount(
        id="user-lockout",
        login_identifier="store_mgr_a",
        password_hash=hash_password("SecurePass!123"),
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


def test_authenticate_issues_session(db_session):
    account = _add_account(db_session)

    issued = AuthService(db_session).authenticate("store_mgr_a", "SecurePass!123")

    assert issued.user_account_id == account.id
    assert issued.id


def test_lockout_after_five_failures(db_session):
    _add_account(db_session)
    service = AuthService(db_session)

    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            service.authenticate("store_mgr_a", "WrongPass!123")

    with pytest.raises(AccountLockedError):
        service.authenticate("store_mgr_a", "SecurePass!123")
