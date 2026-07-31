"""Authenticated-session dependency resolvers (T011)."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.domain.auth.service import AuthService
from src.infrastructure.config import get_settings
from src.infrastructure.db import get_db_session


class SessionPrincipal(BaseModel):
    user_id: str


def _get_session_id(request: Request) -> str | None:
    cookie_name = get_settings().auth_session_cookie_name
    return request.cookies.get(cookie_name)


def optional_authenticated_session(
    request: Request,
    session: Session = Depends(get_db_session),
) -> SessionPrincipal | None:
    session_id = _get_session_id(request)
    if not session_id:
        return None

    account = AuthService(session).resolve_user_from_session(session_id)
    if account is None:
        return None
    return SessionPrincipal(user_id=account.id)


def get_authenticated_session(
    principal: SessionPrincipal | None = Depends(optional_authenticated_session),
) -> SessionPrincipal:
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return principal
