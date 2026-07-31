"""`DemandForecast` model (T061, US4, FR-006, FR-007).

Persists per-SKU/location demand forecasts with the trend/seasonality/promotion factors
that produced them plus a data-quality `error_indicator` so planners can see when a
forecast is based on thin history (FR-007: forecast confidence/error indicators).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class ForecastErrorIndicator(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    INSUFFICIENT_HISTORY = "insufficient_history"


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    location_id: Mapped[str] = mapped_column(String(64), index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    forecast_quantity: Mapped[float] = mapped_column(Float)
    trend_factor: Mapped[float] = mapped_column(Float, default=1.0)
    seasonality_factor: Mapped[float] = mapped_column(Float, default=1.0)
    promotion_factor: Mapped[float] = mapped_column(Float, default=1.0)
    history_points_used: Mapped[int] = mapped_column(Integer, default=0)
    error_indicator: Mapped[str] = mapped_column(String(32), default=ForecastErrorIndicator.MEDIUM)
    factors: Mapped[dict[str, Any]] = mapped_column(JSON)
    narration: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DemandForecastRead(BaseModel):
    id: str
    sku_id: str
    location_id: str
    period_start: date
    period_end: date
    forecast_quantity: float
    trend_factor: float
    seasonality_factor: float
    promotion_factor: float
    history_points_used: int
    error_indicator: ForecastErrorIndicator
    factors: dict[str, Any]
    narration: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DemandForecastRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        sku_id: str,
        location_id: str,
        period_start: date,
        period_end: date,
        forecast_quantity: float,
        trend_factor: float,
        seasonality_factor: float,
        promotion_factor: float,
        history_points_used: int,
        error_indicator: ForecastErrorIndicator,
        factors: dict[str, Any],
        narration: str | None,
    ) -> DemandForecast:
        forecast = DemandForecast(
            id=str(uuid.uuid4()),
            sku_id=sku_id,
            location_id=location_id,
            period_start=period_start,
            period_end=period_end,
            forecast_quantity=forecast_quantity,
            trend_factor=trend_factor,
            seasonality_factor=seasonality_factor,
            promotion_factor=promotion_factor,
            history_points_used=history_points_used,
            error_indicator=error_indicator.value,
            factors=factors,
            narration=narration,
            created_at=datetime.now(UTC),
        )
        self._session.add(forecast)
        self._session.flush()
        return forecast

    def list(
        self,
        sku_id: str | None = None,
        location_id: str | None = None,
        scoped_location_ids: set[str] | None = None,
        all_locations: bool = True,
    ) -> list[DemandForecast]:
        query = self._session.query(DemandForecast)
        if sku_id:
            query = query.filter_by(sku_id=sku_id)
        if location_id:
            query = query.filter_by(location_id=location_id)
        if not all_locations:
            scoped_location_ids = scoped_location_ids or set()
            if scoped_location_ids:
                query = query.filter(DemandForecast.location_id.in_(scoped_location_ids))
            else:
                return []
        return query.order_by(DemandForecast.created_at.desc()).all()
