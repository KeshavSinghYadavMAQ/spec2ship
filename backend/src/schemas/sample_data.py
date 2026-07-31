"""`SeedRunSummary`/`ClearRunSummary` Pydantic schemas (T009, US1).

Mirrors `contracts/sample-data.yaml` in
specs/002-seed-data-responsive-ui/contracts/sample-data.yaml.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SeedRunStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"


class SeedRunSummary(BaseModel):
    seed_batch_id: str
    status: SeedRunStatus
    counts_by_entity_type: dict[str, int] = Field(default_factory=dict)
    started_at: datetime
    completed_at: datetime | None = None


class ClearRunSummary(BaseModel):
    removed_counts_by_entity_type: dict[str, int] = Field(default_factory=dict)
    cleared_at: datetime
