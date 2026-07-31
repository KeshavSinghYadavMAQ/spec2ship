"""Contract test: GET /v1/store-priority/profiles and POST /v1/store-priority/rules
(T081, US8, FR-019, FR-020, FR-021)."""

from __future__ import annotations

from src.domain.transfer_balance.priority_models import StorePriorityProfile

_PRIVILEGED_HEADERS = {"X-User-Id": "regional-1", "X-User-Role": "regional_manager"}


def test_list_store_priority_profiles_empty(client):
    response = client.get("/v1/store-priority/profiles")
    assert response.status_code == 200
    assert response.json() == []


def test_list_store_priority_profiles_filters_by_region(client, db_session):
    db_session.add_all(
        [
            StorePriorityProfile(
                id="p1",
                store_id="STORE-1",
                region="north",
                recent_consumption_rate=5.0,
                region_weight=0.5,
                consumption_weight=0.5,
                current_priority_rank=1,
            ),
            StorePriorityProfile(
                id="p2",
                store_id="STORE-2",
                region="south",
                recent_consumption_rate=3.0,
                region_weight=0.5,
                consumption_weight=0.5,
                current_priority_rank=2,
            ),
        ]
    )
    db_session.commit()

    response = client.get("/v1/store-priority/profiles", params={"region": "north"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["store_id"] == "STORE-1"


def test_update_rules_requires_elevated_role(client):
    response = client.post(
        "/v1/store-priority/rules",
        json={"region_weight": 0.7, "consumption_weight": 0.3},
        headers={"X-User-Id": "sm-1", "X-User-Role": "store_manager"},
    )
    assert response.status_code == 403


def test_update_rules_recomputes_rankings(client, db_session):
    db_session.add_all(
        [
            StorePriorityProfile(
                id="p1",
                store_id="STORE-1",
                region="north",
                recent_consumption_rate=10.0,
                region_weight=0.5,
                consumption_weight=0.5,
                current_priority_rank=0,
            ),
            StorePriorityProfile(
                id="p2",
                store_id="STORE-2",
                region="north",
                recent_consumption_rate=1.0,
                region_weight=0.5,
                consumption_weight=0.5,
                current_priority_rank=0,
            ),
        ]
    )
    db_session.commit()

    response = client.post(
        "/v1/store-priority/rules",
        json={"region_weight": 0.0, "consumption_weight": 1.0},
        headers=_PRIVILEGED_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    ranked = {item["store_id"]: item["current_priority_rank"] for item in body}
    assert ranked["STORE-1"] < ranked["STORE-2"], "higher consumption rate should rank first"
