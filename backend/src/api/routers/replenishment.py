"""Replenishment API router (T055, T105, US3).

`GET /v1/replenishment/recommendations` and
`POST /v1/replenishment/recommendations/{id}/decision` (FR-005). The decision endpoint
also captures an optional operator `actionability_rating` (T105) used to measure SC-004
and writes an audit trail entry (FR-014: "auditable logs for ... recommendations").
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.domain.admin.audit import AuditLogWriter
from src.domain.admin.rbac import CurrentUser, Role, require_role
from src.domain.security.scope_service import ScopeResolutionService
from src.domain.replenishment.models import (
    ActionabilityRating,
    RecommendationStatus,
    ReplenishmentRecommendationRead,
    ReplenishmentRecommendationRepository,
)
from src.infrastructure.db import get_db_session

router = APIRouter(prefix="/replenishment", tags=["replenishment"])


class DecisionRequest(BaseModel):
    decision: RecommendationStatus
    override_reason: str | None = None
    actionability_rating: ActionabilityRating | None = None


@router.get("/recommendations", response_model=list[ReplenishmentRecommendationRead])
async def list_recommendations(
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(*Role)),
) -> list[ReplenishmentRecommendationRead]:
    def _query() -> list[ReplenishmentRecommendationRead]:
        scope = ScopeResolutionService(session).resolve_for_user(current_user.user_id)
        repo = ReplenishmentRecommendationRepository(session)
        return [
            ReplenishmentRecommendationRead.model_validate(r)
            for r in repo.list(
                scoped_location_ids=set(scope.location_ids),
                all_locations=scope.all_locations,
            )
        ]

    return await run_in_threadpool(_query)


@router.post(
    "/recommendations/{recommendation_id}/decision",
    response_model=ReplenishmentRecommendationRead,
)
async def decide_recommendation(
    recommendation_id: str,
    body: DecisionRequest,
    session: Session = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_role(*Role)),
) -> ReplenishmentRecommendationRead:
    def _decide() -> ReplenishmentRecommendationRead:
        scope = ScopeResolutionService(session).resolve_for_user(current_user.user_id)
        repo = ReplenishmentRecommendationRepository(session)
        recommendation = repo.get(recommendation_id)
        if recommendation is None:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        if not scope.all_locations and recommendation.location_id not in scope.location_ids:
            AuditLogWriter(session).record_rls_denied(
                actor_user_id=current_user.user_id,
                resource_type="replenishment_recommendation",
                resource_id=recommendation_id,
                metadata={"location_id": recommendation.location_id},
            )
            raise HTTPException(status_code=404, detail="Recommendation not found")
        if body.decision == RecommendationStatus.OVERRIDDEN and not body.override_reason:
            raise HTTPException(
                status_code=422, detail="override_reason is required when decision is 'overridden'"
            )
        before_status = recommendation.status
        recommendation.status = body.decision.value
        recommendation.override_reason = body.override_reason
        if body.actionability_rating is not None:
            recommendation.actionability_rating = body.actionability_rating.value
        session.flush()

        AuditLogWriter(session).record(
            actor_user_id=current_user.user_id,
            action="replenishment_recommendation_decision",
            entity_type="replenishment_recommendation",
            entity_id=recommendation.id,
            before={"status": before_status},
            after={"status": recommendation.status, "override_reason": recommendation.override_reason},
        )
        return ReplenishmentRecommendationRead.model_validate(recommendation)

    return await run_in_threadpool(_decide)
