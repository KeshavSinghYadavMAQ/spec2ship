"""Shared fixtures for sample-data harness/contract/integration tests (T004, US1).

Builds on the root `conftest.py`'s `db_session`/`client` fixtures, adding:
- `admin_headers` / `non_admin_headers`: role headers for the guard dependency.
- `set_environment`: overrides `get_settings` on the FastAPI app so tests can simulate a
  production deployment without mutating real process environment variables.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from src.infrastructure.config import Settings, get_settings

ADMIN_HEADERS = {"X-User-Id": "admin-1", "X-User-Role": "admin"}
NON_ADMIN_HEADERS = {"X-User-Id": "sm-1", "X-User-Role": "store_manager"}


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return dict(ADMIN_HEADERS)


@pytest.fixture
def non_admin_headers() -> dict[str, str]:
    return dict(NON_ADMIN_HEADERS)


@pytest.fixture
def set_environment():
    """Yields a callable `set_environment("production")` that overrides the app's
    `get_settings` dependency for the duration of the test; auto-restored afterwards."""
    from src.api.main import app

    def _set(environment: str) -> None:
        base = get_settings()
        overridden = base.model_copy(update={"environment": environment})
        app.dependency_overrides[get_settings] = lambda: overridden

    yield _set
    app.dependency_overrides.pop(get_settings, None)
