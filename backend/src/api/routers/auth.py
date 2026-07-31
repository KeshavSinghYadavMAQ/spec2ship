"""Authentication API endpoints for session login/logout/status (US1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.api.dependencies.auth_session import SessionPrincipal, get_authenticated_session
from src.domain.auth.service import AccountLockedError, AuthService, InvalidCredentialsError
from src.infrastructure.config import get_settings
from src.infrastructure.db import get_db_session
from src.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, SessionSummary

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_db_session),
) -> LoginResponse:
    settings = get_settings()

    def _login() -> tuple[str, LoginResponse]:
        auth_session = AuthService(session).authenticate(payload.identifier, payload.password)
        return auth_session.id, LoginResponse(status="authenticated", user_id=auth_session.user_account_id)

    try:
        session_id, login_response = await run_in_threadpool(_login)
    except AccountLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Authentication failed") from exc
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed") from exc

    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=session_id,
        httponly=True,
        secure=settings.auth_session_cookie_secure,
        samesite=settings.auth_session_cookie_samesite,
        path=settings.auth_session_cookie_path,
        max_age=8 * 60 * 60,
    )
    return login_response


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    _: SessionPrincipal = Depends(get_authenticated_session),
    session: Session = Depends(get_db_session),
) -> LogoutResponse:
    settings = get_settings()
    session_id = request.cookies.get(settings.auth_session_cookie_name)

    def _logout() -> bool:
        if session_id is None:
            return False
        return AuthService(session).revoke_session(session_id)

    revoked = await run_in_threadpool(_logout)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No valid session")

    response.delete_cookie(
        key=settings.auth_session_cookie_name,
        path=settings.auth_session_cookie_path,
    )
    return LogoutResponse(status="logged_out")


@router.get("/session", response_model=SessionSummary)
async def session_status(
    principal: SessionPrincipal = Depends(get_authenticated_session),
) -> SessionSummary:
    return SessionSummary(authenticated=True, user_id=principal.user_id)
