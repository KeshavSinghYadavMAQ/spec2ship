"""`StorePriorityProfile` model (T022, FR-019).

Shared read dependency for US5 (transfer engine consults priority rank when constrained).
Full scoring/ranking logic (US8) is implemented in `priority_service.py` in a later phase.
"""

from __future__ import annotations

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db import Base


class StorePriorityProfile(Base):
    __tablename__ = "store_priority_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    region: Mapped[str] = mapped_column(String(64))
    recent_consumption_rate: Mapped[float] = mapped_column(Float, default=0.0)
    region_weight: Mapped[float] = mapped_column(Float, default=0.5)
    consumption_weight: Mapped[float] = mapped_column(Float, default=0.5)
    current_priority_rank: Mapped[int] = mapped_column(Integer, default=0)
    priority_factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
