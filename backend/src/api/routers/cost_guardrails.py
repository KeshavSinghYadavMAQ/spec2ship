"""Cost guardrail dashboard API router (T104, SC-008, FR-015, Constitution VI).

Read-only surface exposing the estimated ingestion cost against the pilot's
$15,000/month ceiling and $0.00005/event assumption from `cost_guardrails.py`, so the
analytics dashboard can render a live guardrail indicator alongside operational KPIs.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from src.infrastructure.cost_guardrails import cost_guardrails

router = APIRouter(prefix="/admin/cost-guardrails", tags=["admin"])


class CostGuardrailView(BaseModel):
    ingested_event_count: int
    estimated_ingestion_cost_usd: float
    monthly_cost_ceiling_usd: float
    per_event_cost_assumption_usd: float
    within_ceiling: bool


@router.get("", response_model=CostGuardrailView)
async def get_cost_guardrails() -> CostGuardrailView:
    snapshot = cost_guardrails.get_cost_snapshot()
    return CostGuardrailView(
        ingested_event_count=snapshot.ingested_event_count,
        estimated_ingestion_cost_usd=snapshot.estimated_ingestion_cost_usd,
        monthly_cost_ceiling_usd=snapshot.monthly_cost_ceiling_usd,
        per_event_cost_assumption_usd=snapshot.per_event_cost_assumption_usd,
        within_ceiling=snapshot.within_ceiling,
    )
