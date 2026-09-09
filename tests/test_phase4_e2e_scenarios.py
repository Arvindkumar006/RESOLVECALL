"""
Tests for Phase 4: End-to-End API and Web Dashboard Integration.
Verifies all HTTP endpoints, state persistence, HITL approval, and denial flows.
"""

import pytest
from fastapi.testclient import TestClient
from web.app import app
from core.simulation_state import SimulatedEnvironment


@pytest.fixture
def client():
    return TestClient(app)


def test_dashboard_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "JARVIS SENTINEL" in res.text
    assert "Autonomous where safe. Human-controlled where consequential." in res.text


def test_api_state_and_reset(client):
    # Reset
    res_reset = client.post("/api/reset")
    assert res_reset.status_code == 200

    # Get state
    res_state = client.get("/api/state")
    assert res_state.status_code == 200
    data = res_state.json()
    assert "hosts" in data
    assert len(data["hosts"]) >= 2
    fin_host = next(h for h in data["hosts"] if h["host_id"] == "FINANCE-PC-07")
    assert fin_host["status"] == "CONNECTED"


def test_scenario_a_api_autonomous_flow(client):
    client.post("/api/reset")

    res = client.post("/api/trigger/scenario-a")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["incident_id"] == "INC-1019"
    assert data["status"] == "RESOLVED"
    assert data["requires_hitl"] is False

    # Verify state reflects autonomous resolution
    state = client.get("/api/state").json()
    dev_host = next(h for h in state["hosts"] if h["host_id"] == "DEV-BOX-02")
    assert dev_host["status"] == "CONNECTED"

    # Verify audit log contains entry
    audit = client.get("/api/audit").json()
    assert any("DEV-BOX-02" in a["target"] for a in audit["audit_log"])


def test_scenario_b_api_hitl_approval_flow(client):
    client.post("/api/reset")

    # 1. Trigger Scenario B
    res = client.post("/api/trigger/scenario-b")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["incident_id"] == "INC-1042"
    assert data["status"] == "AWAITING_APPROVAL"
    assert data["requires_hitl"] is True

    # 2. Before approval, FINANCE-PC-07 MUST remain CONNECTED
    state_before = client.get("/api/state").json()
    fin_before = next(h for h in state_before["hosts"] if h["host_id"] == "FINANCE-PC-07")
    assert fin_before["status"] == "CONNECTED"

    # 3. Approve via API
    res_approve = client.post("/api/incidents/INC-1042/approve", json={"approver": "SecOps_Lead_Dana"})
    assert res_approve.status_code == 200
    app_data = res_approve.json()
    assert app_data["success"] is True
    assert app_data["action"] == "APPROVED"
    assert app_data["new_endpoint_status"] == "ISOLATED"
    assert "report_markdown" in app_data

    # 4. After approval, FINANCE-PC-07 MUST be ISOLATED
    state_after = client.get("/api/state").json()
    fin_after = next(h for h in state_after["hosts"] if h["host_id"] == "FINANCE-PC-07")
    assert fin_after["status"] == "ISOLATED"
    assert "185.220.101.5" in state_after["global_blocked_ips"]


def test_scenario_b_api_hitl_deny_flow(client):
    client.post("/api/reset")

    # 1. Trigger Scenario B
    client.post("/api/trigger/scenario-b")

    # 2. Deny via API
    res_deny = client.post(
        "/api/incidents/INC-1042/deny",
        json={"approver": "SecOps_Lead_Dana", "reason": "Operator verification"}
    )
    assert res_deny.status_code == 200
    deny_data = res_deny.json()
    assert deny_data["success"] is True
    assert deny_data["action"] == "DENIED"

    # 3. Host MUST remain CONNECTED
    state = client.get("/api/state").json()
    fin = next(h for h in state["hosts"] if h["host_id"] == "FINANCE-PC-07")
    assert fin["status"] == "CONNECTED"
