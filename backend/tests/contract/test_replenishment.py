"""Contract test: GET /v1/replenishment/recommendations and
POST /v1/replenishment/recommendations/{id}/decision (T049, US3, FR-004, FR-005)."""

from __future__ import annotations

from datetime import date

from src.domain.replenishment.models import ReplenishmentRecommendationRepository


def test_list_recommendations_empty(client):
    response = client.get("/v1/replenishment/recommendations")
    assert response.status_code == 200
    assert response.json() == []


def test_decision_records_actionability_rating(client, db_session):
    repo = ReplenishmentRecommendationRepository(db_session)
    recommendation = repo.create(
        sku_id="SKU-1",
        location_id="STORE-1",
        recommended_quantity=15,
        recommended_by_date=date.today(),
        policy_snapshot={"reorder_point": 20},
        rationale={"factors": {}, "narration": "test"},
    )
    db_session.commit()

    response = client.post(
        f"/v1/replenishment/recommendations/{recommendation.id}/decision",
        json={"decision": "accepted", "actionability_rating": "actionable"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["actionability_rating"] == "actionable"


def test_decision_override_requires_reason(client, db_session):
    repo = ReplenishmentRecommendationRepository(db_session)
    recommendation = repo.create(
        sku_id="SKU-2",
        location_id="STORE-1",
        recommended_quantity=15,
        recommended_by_date=date.today(),
        policy_snapshot={"reorder_point": 20},
        rationale={"factors": {}, "narration": "test"},
    )
    db_session.commit()

    response = client.post(
        f"/v1/replenishment/recommendations/{recommendation.id}/decision",
        json={"decision": "overridden"},
    )
    assert response.status_code == 422
