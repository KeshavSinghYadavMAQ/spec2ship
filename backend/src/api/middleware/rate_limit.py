"""Per-source-system ingestion rate-limiting middleware (T015, FR-024).

Implements a Redis-backed token-bucket-style fixed-window counter keyed by the
`X-Source-System` header, applied to ingestion endpoints (currently
`POST /v1/inventory/events`). Requests exceeding the configured window limit receive
HTTP 429 with a `Retry-After` header, independent of the FR-022 outage queue-and-replay
path (excess events are rejected, not buffered).
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.infrastructure.cache import get_cache_client
from src.infrastructure.config import get_settings

RATE_LIMITED_PATHS = {"/v1/inventory/events"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path not in RATE_LIMITED_PATHS or request.method != "POST":
            return await call_next(request)

        source_system = request.headers.get("X-Source-System", "unknown")
        settings = get_settings()
        cache = get_cache_client()
        key = f"rate-limit:{source_system}:{request.url.path}"

        current = cache.get(key)
        if current is None:
            cache.set(key, "1", ex=settings.rate_limit_window_seconds)
            count = 1
        else:
            count = cache.incr(key)
            if count == 1:
                cache.expire(key, settings.rate_limit_window_seconds)

        if count > settings.rate_limit_requests_per_window:
            retry_after = max(cache.ttl(key), 1)
            problem = {
                "type": "about:blank",
                "title": "Too Many Requests",
                "status": 429,
                "detail": (
                    f"Source system '{source_system}' exceeded the ingestion rate limit "
                    f"of {settings.rate_limit_requests_per_window} requests per "
                    f"{settings.rate_limit_window_seconds}s (FR-024)."
                ),
            }
            return JSONResponse(
                status_code=429,
                content=problem,
                headers={"Retry-After": str(retry_after)},
                media_type="application/problem+json",
            )

        return await call_next(request)
