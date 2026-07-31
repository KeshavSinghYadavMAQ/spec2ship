"""`UserRoleAssignment` model and RBAC authorization dependency (T014, FR-013).

Five roles per spec.md: store_manager, inventory_manager, procurement_officer,
regional_manager, admin. Identity is resolved from request headers in this v1 pilot
(`X-User-Id` / `X-User-Role`) as a placeholder for the Azure AD-integrated auth mentioned
in research.md; production deployments should replace `get_current_user` with real token
validation without changing the `require_role` call sites.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db import Base


class Role(StrEnum):
    STORE_MANAGER = "store_manager"
    INVENTORY_MANAGER = "inventory_manager"
    PROCUREMENT_OFFICER = "procurement_officer"
    REGIONAL_MANAGER = "regional_manager"
    ADMIN = "admin"


class UserRoleAssignment(Base):
    """Mapping of user responsibilities and access rights to operational functions."""

    __tablename__ = "user_role_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    role: Mapped[str] = mapped_column(String(32))
    location_scope: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class CurrentUser(BaseModel):
    user_id: str
    role: Role


def get_current_user(request: Request) -> CurrentUser:
    """Resolve the current user from request headers (v1 placeholder for Azure AD auth)."""
    user_id = request.headers.get("X-User-Id")
    role_header = request.headers.get("X-User-Role")
    if not user_id or not role_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id and X-User-Role headers are required",
        )
    try:
        role = Role(role_header)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unknown role: {role_header}"
        ) from exc
    return CurrentUser(user_id=user_id, role=role)


def require_role(*allowed_roles: Role) -> Callable[..., CurrentUser]:
    """FastAPI dependency factory enforcing that the current user has one of `allowed_roles`."""

    def _dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not permitted to perform this action",
            )
        return current_user

    return _dependency
