"""`TransferSuggestion` model (T069, US5, FR-008, FR-009, FR-020).

Source→destination stock rebalancing suggestion between two locations for the same SKU,
constrained by feasibility (never proposes a transfer that would breach the source's own
minimum threshold) and ranked by the destination's restoration priority (US8).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.infrastructure.db import Base


class FeasibilityStatus(StrEnum):
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"


class TransferStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    REJECTED = "rejected"


class TransferSuggestion(Base):
    __tablename__ = "transfer_suggestions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    source_location_id: Mapped[str] = mapped_column(String(64), index=True)
    destination_location_id: Mapped[str] = mapped_column(String(64), index=True)
    suggested_quantity: Mapped[int] = mapped_column(Integer)
    feasibility_status: Mapped[str] = mapped_column(String(32))
    feasibility_reason: Mapped[str] = mapped_column(String(256))
    priority_rank: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default=TransferStatus.PROPOSED)
    factors: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TransferSuggestionRead(BaseModel):
    id: str
    sku_id: str
    source_location_id: str
    destination_location_id: str
    suggested_quantity: int
    feasibility_status: FeasibilityStatus
    feasibility_reason: str
    priority_rank: int
    status: TransferStatus
    factors: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class TransferSuggestionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        sku_id: str,
        source_location_id: str,
        destination_location_id: str,
        suggested_quantity: int,
        feasibility_status: FeasibilityStatus,
        feasibility_reason: str,
        priority_rank: int,
        factors: dict[str, Any],
    ) -> TransferSuggestion:
        suggestion = TransferSuggestion(
            id=str(uuid.uuid4()),
            sku_id=sku_id,
            source_location_id=source_location_id,
            destination_location_id=destination_location_id,
            suggested_quantity=suggested_quantity,
            feasibility_status=feasibility_status.value,
            feasibility_reason=feasibility_reason,
            priority_rank=priority_rank,
            status=TransferStatus.PROPOSED.value,
            factors=factors,
            created_at=datetime.now(UTC),
        )
        self._session.add(suggestion)
        self._session.flush()
        return suggestion

    def get(self, suggestion_id: str) -> TransferSuggestion | None:
        return self._session.get(TransferSuggestion, suggestion_id)

    def list(
        self,
        scoped_location_ids: set[str] | None = None,
        all_locations: bool = True,
    ) -> list[TransferSuggestion]:
        query = self._session.query(TransferSuggestion)
        if not all_locations:
            scoped_location_ids = scoped_location_ids or set()
            if scoped_location_ids:
                query = query.filter(
                    TransferSuggestion.source_location_id.in_(scoped_location_ids)
                    | TransferSuggestion.destination_location_id.in_(scoped_location_ids)
                )
            else:
                return []
        return query.order_by(TransferSuggestion.priority_rank.desc(), TransferSuggestion.created_at.desc()).all()
