"""Authentication service: session issuance, revocation, and lockout policy (T010)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.domain.admin.audit import AuditLogWriter
from src.domain.auth.models import AuthSession, UserAccount
from src.domain.auth.password_policy import verify_password

_LOCKOUT_WINDOW = timedelta(minutes=15)
_LOCKOUT_THRESHOLD = 5
_LOCKOUT_DURATION = timedelta(minutes=30)
_SESSION_TTL = timedelta(hours=8)


class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass


class AccountLockedError(AuthError):
    def __init__(self, locked_until: datetime) -> None:
        self.locked_until = locked_until
        super().__init__("Account is temporarily locked")


class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._audit = AuditLogWriter(session)

    def authenticate(self, identifier: str, password: str) -> AuthSession:
        now = datetime.now(UTC)
        account = (
            self._session.query(UserAccount)
            .filter(UserAccount.login_identifier == identifier)
            .one_or_none()
        )
        if account is None or not account.is_active:
            self._record_auth_event("login_failure", metadata={"identifier": identifier})
            raise InvalidCredentialsError("Invalid credentials")

        if account.locked_until is not None and account.locked_until > now:
            self._record_auth_event(
                "lockout",
                actor_user_id=account.id,
                metadata={"locked_until": account.locked_until.isoformat()},
            )
            raise AccountLockedError(account.locked_until)

        if not verify_password(password, account.password_hash):
            self._record_failed_attempt(account, now)
            self._record_auth_event(
                "login_failure",
                actor_user_id=account.id,
                metadata={"identifier": identifier},
            )
            raise InvalidCredentialsError("Invalid credentials")

        self._clear_failed_attempts(account)
        issued = AuthSession(
            id=str(uuid.uuid4()),
            user_account_id=account.id,
            created_at=now,
            expires_at=now + _SESSION_TTL,
            revoked_at=None,
            last_seen_at=now,
        )
        self._session.add(issued)
        self._session.flush()
        self._record_auth_event(
            "login_success",
            actor_user_id=account.id,
            metadata={"session_id": issued.id},
        )
        return issued

    def revoke_session(self, session_id: str) -> bool:
        now = datetime.now(UTC)
        auth_session = self._session.query(AuthSession).filter(AuthSession.id == session_id).one_or_none()
        if auth_session is None or auth_session.revoked_at is not None:
            self._record_auth_event("session_invalid", metadata={"session_id": session_id})
            return False
        auth_session.revoked_at = now
        auth_session.last_seen_at = now
        self._session.flush()
        self._record_auth_event(
            "logout",
            actor_user_id=auth_session.user_account_id,
            metadata={"session_id": session_id},
        )
        return True

    def _record_auth_event(
        self,
        event_type: str,
        *,
        actor_user_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self._audit.record_auth_event(
            event_type=event_type,
            actor_user_id=actor_user_id,
            metadata=metadata,
        )

    def get_active_session(self, session_id: str) -> AuthSession | None:
        now = datetime.now(UTC)
        auth_session = self._session.query(AuthSession).filter(AuthSession.id == session_id).one_or_none()
        if auth_session is None:
            return None
        expires_at = auth_session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if auth_session.revoked_at is not None or expires_at <= now:
            return None
        auth_session.last_seen_at = now
        self._session.flush()
        return auth_session

    def resolve_user_from_session(self, session_id: str) -> UserAccount | None:
        auth_session = self.get_active_session(session_id)
        if auth_session is None:
            return None
        return (
            self._session.query(UserAccount)
            .filter(UserAccount.id == auth_session.user_account_id, UserAccount.is_active.is_(True))
            .one_or_none()
        )

    def _record_failed_attempt(self, account: UserAccount, now: datetime) -> None:
        if (
            account.failed_attempt_window_started_at is None
            or now - account.failed_attempt_window_started_at > _LOCKOUT_WINDOW
        ):
            account.failed_attempt_window_started_at = now
            account.failed_attempt_count_window = 1
        else:
            account.failed_attempt_count_window += 1

        if account.failed_attempt_count_window >= _LOCKOUT_THRESHOLD:
            account.locked_until = now + _LOCKOUT_DURATION
            account.failed_attempt_count_window = 0
            account.failed_attempt_window_started_at = None

        account.updated_at = now
        self._session.flush()

    def _clear_failed_attempts(self, account: UserAccount) -> None:
        now = datetime.now(UTC)
        account.failed_attempt_count_window = 0
        account.failed_attempt_window_started_at = None
        account.locked_until = None
        account.updated_at = now
        self._session.flush()
