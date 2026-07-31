"""Non-production + admin-role guard for sample-data endpoints (T007, US1, FR-004, FR-011).

Extends the existing `require_role(Role.ADMIN)` RBAC dependency with a `Settings.environment`
check so seeding/clearing sample data can never run against a production deployment, even
if an admin-role caller attempts it.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.infrastructure.config import Settings, get_settings

PRODUCTION_ENVIRONMENT_NAMES = {"production", "prod"}


def require_non_production_admin(
    current_user: CurrentUser = Depends(require_role(Role.ADMIN)),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    """FastAPI dependency: caller must be `admin` AND the deployment must not be production.

    Both the role check and the environment check return the same generic 403 so error
    responses never leak which precondition failed (T053 security hardening).
    """
    if settings.environment.lower() in PRODUCTION_ENVIRONMENT_NAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sample-data actions are not permitted in this environment",
        )
    return current_user
