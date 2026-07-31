"""Middleware that exposes the auth session id on request state for downstream dependencies."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.infrastructure.config import get_settings


class SessionContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        cookie_name = get_settings().auth_session_cookie_name
        request.state.auth_session_id = request.cookies.get(cookie_name)
        return await call_next(request)
