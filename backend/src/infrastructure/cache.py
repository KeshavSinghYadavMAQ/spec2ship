"""Redis client wrapper (T011).

Backs alert suppression windows (FR-003), threshold-edit evaluation locks (FR-023), and
per-source-system rate-limit token buckets (FR-024). Exposes a minimal `CacheClient`
protocol so production code (real Redis) and tests (fakeredis) share the same interface.
"""

from __future__ import annotations

from typing import Protocol

import redis

from src.infrastructure.config import get_settings


class CacheClient(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ex: int | None = None) -> None: ...

    def set_nx(self, key: str, value: str, ex: int | None = None) -> bool:
        """Set key only if it does not already exist. Returns True if set (lock acquired)."""
        ...

    def delete(self, key: str) -> None: ...

    def incr(self, key: str) -> int: ...

    def expire(self, key: str, seconds: int) -> None: ...

    def ttl(self, key: str) -> int: ...


class RedisCacheClient:
    """Production cache client backed by redis-py."""

    def __init__(self, url: str | None = None) -> None:
        settings = get_settings()
        self._client = redis.Redis.from_url(url or settings.redis_url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._client.set(key, value, ex=ex)

    def set_nx(self, key: str, value: str, ex: int | None = None) -> bool:
        return bool(self._client.set(key, value, ex=ex, nx=True))

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def incr(self, key: str) -> int:
        return int(self._client.incr(key))

    def expire(self, key: str, seconds: int) -> None:
        self._client.expire(key, seconds)

    def ttl(self, key: str) -> int:
        return int(self._client.ttl(key))


_cache_client: CacheClient | None = None


def get_cache_client() -> CacheClient:
    """FastAPI dependency / module-level accessor for the shared cache client.

    Tests should override this (e.g. via FastAPI dependency_overrides or by calling
    `set_cache_client_for_testing`) to inject a fakeredis-backed instance so no real
    Redis server is required.
    """
    global _cache_client
    if _cache_client is None:
        _cache_client = RedisCacheClient()
    return _cache_client


def set_cache_client_for_testing(client: CacheClient) -> None:
    global _cache_client
    _cache_client = client
