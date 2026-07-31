"""Shared pytest fixtures: isolated SQLite DB per test, FastAPI TestClient with fakeredis
and in-memory queue overrides so the full test suite runs without Docker/Azure services.
"""

from __future__ import annotations

import os

os.environ.setdefault("APP_DATABASE_URL", "sqlite:///:memory:")

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.infrastructure import cache as cache_module
from src.infrastructure import db as db_module
from src.infrastructure import queue as queue_module


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    db_module.Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def fake_cache():
    client = fakeredis.FakeStrictRedis(decode_responses=True)

    class _FakeCacheClient:
        def get(self, key: str):
            return client.get(key)

        def set(self, key: str, value: str, ex: int | None = None) -> None:
            client.set(key, value, ex=ex)

        def set_nx(self, key: str, value: str, ex: int | None = None) -> bool:
            return bool(client.set(key, value, ex=ex, nx=True))

        def delete(self, key: str) -> None:
            client.delete(key)

        def incr(self, key: str) -> int:
            return int(client.incr(key))

        def expire(self, key: str, seconds: int) -> None:
            client.expire(key, seconds)

        def ttl(self, key: str) -> int:
            return int(client.ttl(key))

    cache_client = _FakeCacheClient()
    cache_module.set_cache_client_for_testing(cache_client)
    yield cache_client
    cache_module.set_cache_client_for_testing(None)  # type: ignore[arg-type]


@pytest.fixture
def in_memory_queue():
    client = queue_module.InMemoryQueueClient()
    queue_module.set_queue_client_for_testing(client)
    yield client
    queue_module.set_queue_client_for_testing(None)  # type: ignore[arg-type]


@pytest.fixture
def client(db_session, fake_cache, in_memory_queue):
    from src.api.main import app
    from src.infrastructure.db import get_db_session

    def _override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
