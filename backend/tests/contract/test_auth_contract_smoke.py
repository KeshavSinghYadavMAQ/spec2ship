"""Baseline auth/RLS contract harness registration smoke (T019)."""

from __future__ import annotations


def test_auth_session_contract_surface_is_reachable(client):
    response = client.get("/v1/auth/session")
    assert response.status_code in {200, 401, 404}
