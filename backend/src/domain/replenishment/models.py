"""`ReplenishmentRecommendation` model (T052, US3, FR-004, FR-005).

`rationale` MUST NOT be empty (Constitution: preserve explanation payloads) — enforced in
`engine.py` by always calling the explainer agent before persisting a recommendation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class RecommendationStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    OVERRIDDEN = "overridden"
    DISMISSED = "dismissed"


class ActionabilityRating(StrEnum):
    ACTIONABLE = "actionable"
    NOT_ACTIONABLE = "not_actionable"


class ReplenishmentRecommendation(Base):
    __tablename__ = "replenishment_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    location_id: Mapped[str] = mapped_column(String(64), index=True)
    recommended_quantity: Mapped[int] = mapped_column(Integer)
    recommended_by_date: Mapped[date] = mapped_column(Date)
    policy_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    rationale: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default=RecommendationStatus.PROPOSED)
    override_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    actionability_rating: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReplenishmentRecommendationRead(BaseModel):
    id: str
    sku_id: str
    location_id: str
    recommended_quantity: int
    recommended_by_date: date
    policy_snapshot: dict[str, Any]
    rationale: dict[str, Any]
    status: RecommendationStatus
    override_reason: str | None
    actionability_rating: ActionabilityRating | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplenishmentRecommendationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        sku_id: str,
        location_id: str,
        recommended_quantity: int,
        recommended_by_date: date,
        policy_snapshot: dict[str, Any],
        rationale: dict[str, Any],
    ) -> ReplenishmentRecommendation:
        recommendation = ReplenishmentRecommendation(
            id=str(uuid.uuid4()),
            sku_id=sku_id,
            location_id=location_id,
            recommended_quantity=recommended_quantity,
            recommended_by_date=recommended_by_date,
            policy_snapshot=policy_snapshot,
            rationale=rationale,
            status=RecommendationStatus.PROPOSED.value,
            created_at=datetime.now(UTC),
        )
        self._session.add(recommendation)
        self._session.flush()
        return recommendation

    def get(self, recommendation_id: str) -> ReplenishmentRecommendation | None:
        return self._session.get(ReplenishmentRecommendation, recommendation_id)

    def list(
        self,
        scoped_location_ids: set[str] | None = None,
        all_locations: bool = True,
    ) -> list[ReplenishmentRecommendation]:
        query = self._session.query(ReplenishmentRecommendation)
        if not all_locations:
            scoped_location_ids = scoped_location_ids or set()
            if scoped_location_ids:
                query = query.filter(ReplenishmentRecommendation.location_id.in_(scoped_location_ids))
            else:
                return []
        return query.order_by(ReplenishmentRecommendation.created_at.desc()).all()
