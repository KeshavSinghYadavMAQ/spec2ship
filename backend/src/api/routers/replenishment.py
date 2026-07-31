"""Replenishment API router (T055, T105, US3).

`GET /v1/replenishment/recommendations` and
`POST /v1/replenishment/recommendations/{id}/decision` (FR-005). The decision endpoint
also captures an optional operator `actionability_rating` (T105) used to measure SC-004.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

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
) -> list[ReplenishmentRecommendationRead]:
    def _query() -> list[ReplenishmentRecommendationRead]:
        repo = ReplenishmentRecommendationRepository(session)
        return [ReplenishmentRecommendationRead.model_validate(r) for r in repo.list()]

    return await run_in_threadpool(_query)


@router.post(
    "/recommendations/{recommendation_id}/decision",
    response_model=ReplenishmentRecommendationRead,
)
async def decide_recommendation(
    recommendation_id: str,
    body: DecisionRequest,
    session: Session = Depends(get_db_session),
) -> ReplenishmentRecommendationRead:
    def _decide() -> ReplenishmentRecommendationRead:
        repo = ReplenishmentRecommendationRepository(session)
        recommendation = repo.get(recommendation_id)
        if recommendation is None:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        if body.decision == RecommendationStatus.OVERRIDDEN and not body.override_reason:
            raise HTTPException(
                status_code=422, detail="override_reason is required when decision is 'overridden'"
            )
        recommendation.status = body.decision.value
        recommendation.override_reason = body.override_reason
        if body.actionability_rating is not None:
            recommendation.actionability_rating = body.actionability_rating.value
        session.flush()
        return ReplenishmentRecommendationRead.model_validate(recommendation)

    return await run_in_threadpool(_decide)
