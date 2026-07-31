"""Region-based and consumption-based priority scoring service (T084, US8, FR-019,
FR-021).

Computes a composite restoration-priority score per store from an externally supplied
region-priority signal (e.g. regional shortage severity) weighted by `region_weight`,
combined with each store's own `recent_consumption_rate` weighted by
`consumption_weight`. Ranks stores highest-composite-score-first; `US5`'s transfer
engine (T070) reads the resulting `current_priority_rank`.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.agents.store_priority_explainer import StorePriorityExplainerAgent
from src.domain.transfer_balance.priority_models import StorePriorityProfile


class StorePriorityService:
    def __init__(
        self, session: Session, explainer: StorePriorityExplainerAgent | None = None
    ) -> None:
        self._session = session
        self._explainer = explainer or StorePriorityExplainerAgent()

    def list_profiles(self, region: str | None = None) -> list[StorePriorityProfile]:
        query = self._session.query(StorePriorityProfile)
        if region:
            query = query.filter_by(region=region)
        return query.order_by(StorePriorityProfile.current_priority_rank).all()

    def recompute_rankings(
        self,
        *,
        region: str | None = None,
        region_priority_scores: dict[str, float] | None = None,
    ) -> list[StorePriorityProfile]:
        """Missing consumption data defaults to 0.0 rather than raising, so a store with
        no recorded consumption still receives a (low) rank instead of blocking the
        whole recomputation (failure-path edge case)."""
        region_priority_scores = region_priority_scores or {}
        query = self._session.query(StorePriorityProfile)
        if region:
            query = query.filter_by(region=region)
        profiles = query.all()

        scored: list[tuple[float, StorePriorityProfile]] = []
        for profile in profiles:
            region_score = region_priority_scores.get(profile.store_id, 0.0)
            consumption_rate = profile.recent_consumption_rate or 0.0
            composite_score = (
                profile.region_weight * region_score + profile.consumption_weight * consumption_rate
            )
            scored.append((composite_score, profile))

        scored.sort(key=lambda item: item[0], reverse=True)

        for rank, (composite_score, profile) in enumerate(scored, start=1):
            factors = {
                "store_id": profile.store_id,
                "region": profile.region,
                "region_score": region_priority_scores.get(profile.store_id, 0.0),
                "consumption_rate": profile.recent_consumption_rate or 0.0,
                "region_weight": profile.region_weight,
                "consumption_weight": profile.consumption_weight,
                "composite_score": composite_score,
                "current_priority_rank": rank,
            }
            profile.current_priority_rank = rank
            profile.priority_factors = factors
            profile.narration = self._explainer.explain(factors)

        self._session.flush()
        return [profile for _, profile in scored]

    def update_rules(
        self,
        *,
        region_weight: float | None = None,
        consumption_weight: float | None = None,
    ) -> list[StorePriorityProfile]:
        """Applies new global default weights to every store, then recomputes rankings
        so subsequent reads reflect the change immediately (contract: "future
        prioritization recalculations use new weights")."""
        for profile in self._session.query(StorePriorityProfile).all():
            if region_weight is not None:
                profile.region_weight = region_weight
            if consumption_weight is not None:
                profile.consumption_weight = consumption_weight
        self._session.flush()
        return self.recompute_rankings()
