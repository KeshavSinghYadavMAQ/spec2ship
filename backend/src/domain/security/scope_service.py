"""Authoritative per-request scope resolution service (T014)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from src.domain.admin.rbac import Role, UserRoleAssignment


@dataclass(frozen=True)
class ScopeContext:
    user_id: str
    role: Role
    location_ids: frozenset[str]
    all_locations: bool


class ScopeResolutionService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def resolve_for_user(self, user_id: str) -> ScopeContext:
        assignment = (
            self._session.query(UserRoleAssignment)
            .filter(UserRoleAssignment.user_id == user_id)
            .order_by(UserRoleAssignment.id.asc())
            .first()
        )
        if assignment is None:
            context = ScopeContext(user_id=user_id, role=Role.STORE_MANAGER, location_ids=frozenset(), all_locations=False)
            return context

        role = Role(assignment.role)
        all_locations = role == Role.ADMIN
        location_ids = _extract_location_ids(assignment.location_scope)
        context = ScopeContext(
            user_id=user_id,
            role=role,
            location_ids=frozenset(location_ids),
            all_locations=all_locations,
        )
        return context

    def invalidate_user(self, user_id: str) -> None:
        del user_id

    @staticmethod
    def _cache_key(user_id: str) -> str:
        return f"scope:v1:{user_id}"


def _extract_location_ids(location_scope: dict[str, Any] | None) -> set[str]:
    if not location_scope:
        return set()
    raw = location_scope.get("location_ids") or location_scope.get("locations")
    if not isinstance(raw, list):
        return set()
    return {str(value) for value in raw if str(value).strip()}
