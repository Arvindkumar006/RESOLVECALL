"""
Red-Team Attack Suite: Adversarial Authorization Boundary & API Security Tests.
Tests Section 4 and Section 5:
- No token
- Invalid token
- Expired/forged token
- Token for another incident
- Token for another host
- Token for another action
- Reuse of an already-consumed token
- Duplicate containment execution
- Malformed API requests
- Non-existent incident approvals
- Bypassing approval state
"""

import json
import pytest
from fastapi.testclient import TestClient
from core.simulation_state import SimulatedEnvironment
from core.models import EndpointStatus
from hitl.state_machine import HITLStateMachine, HITLState
from tools.containment_tools import execute_safe_containment
from agents.orchestrator import SentinelOrchestrator
from web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def setup_function():
    env = SimulatedEnvironment()
    env._reset_to_default_state()
    HITLStateMachine.reset_tokens()


# =========================================================================
# ATTACK SUITE 1: DIRECT CONTAINMENT TOOL AUTHORIZATION BYPASS ATTEMPTS
# =========================================================================

def test_attack_containment_no_token():
    """Attack: Attacker invokes ISOLATE_ENDPOINT with no token."""
    res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=""))
    assert res["success"] is False
    assert res["status"] == "BLOCKED_BY_POLICY"
    assert "rejected by policy engine" in res["reason"]
    assert SimulatedEnvironment().get_host("FINANCE-PC-07")["status"] == EndpointStatus.CONNECTED.value


def test_attack_containment_invalid_forged_token():
    """Attack: Attacker manufactures an un-minted forged token string."""
    forged = "HITL_APPROVED.eyJzdWIiOiJoYWNrZXIifQ.fake_signature"
    res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=forged))
    assert res["success"] is False
    assert res["status"] == "BLOCKED_BY_POLICY"
    assert SimulatedEnvironment().get_host("FINANCE-PC-07")["status"] == EndpointStatus.CONNECTED.value


def test_attack_containment_token_tampered_payload():
    """Attack: Attacker tampers with the payload of a valid token without knowing the secret."""
    from core.security import mint_authorization_token
    token = mint_authorization_token("INC-1042", "FINANCE-PC-07", "ISOLATE_ENDPOINT", "Analyst")
    parts = token.split(".")
    # Tamper with middle part (payload)
    tampered_token = f"{parts[0]}.eyJoYWNrZWQiOiB0cnVlfQ.{parts[2]}"
    res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=tampered_token))
    assert res["success"] is False
    assert res["status"] == "BLOCKED_BY_POLICY"


def test_attack_containment_token_expired():
    """Attack: Attacker attempts to use an expired token (negative TTL)."""
    from core.security import mint_authorization_token
    expired_token = mint_authorization_token("INC-1042", "FINANCE-PC-07", "ISOLATE_ENDPOINT", "Analyst", ttl_seconds=-10)
    res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=expired_token))
    assert res["success"] is False
    assert res["status"] == "BLOCKED_BY_POLICY"


def test_attack_containment_token_for_another_host():
    """Attack: Token minted for DEV-BOX-02 is used to attempt isolation of FINANCE-PC-07."""
    from core.security import mint_authorization_token
    token_dev = mint_authorization_token("INC-1019", "DEV-BOX-02", "ISOLATE_ENDPOINT", "SecOps")

    res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=token_dev))
    assert res["success"] is False
    assert res["status"] == "BLOCKED_BY_POLICY"
    assert SimulatedEnvironment().get_host("FINANCE-PC-07")["status"] == EndpointStatus.CONNECTED.value


def test_attack_containment_token_for_another_action():
    """Attack: Token minted for TERMINATE_SUSPICIOUS_PROCESSES is used for ISOLATE_ENDPOINT."""
    from core.security import mint_authorization_token
    token_proc = mint_authorization_token("INC-1042", "FINANCE-PC-07", "TERMINATE_SUSPICIOUS_PROCESSES", "SecOps")

    res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=token_proc))
    assert res["success"] is False
    assert res["status"] == "BLOCKED_BY_POLICY"
    assert SimulatedEnvironment().get_host("FINANCE-PC-07")["status"] == EndpointStatus.CONNECTED.value


def test_attack_containment_token_replay_reuse():
    """Attack: Reusing a valid token after its nonce was already burned in previous containment."""
    from core.security import mint_authorization_token
    valid_token = mint_authorization_token("INC-1042", "FINANCE-PC-07", "ISOLATE_ENDPOINT", "SecOps")

    # First legitimate execution consumes token
    res1 = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=valid_token))
    assert res1["success"] is True
    assert SimulatedEnvironment().get_host("FINANCE-PC-07")["status"] == EndpointStatus.ISOLATED.value

    # Reset host back to CONNECTED to test replay attempt
    SimulatedEnvironment().hosts["FINANCE-PC-07"].status = EndpointStatus.CONNECTED

    # Second execution using identical token MUST FAIL because nonce was consumed
    res2 = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=valid_token))
    assert res2["success"] is False
    assert res2["status"] == "BLOCKED_BY_POLICY"
    assert SimulatedEnvironment().get_host("FINANCE-PC-07")["status"] == EndpointStatus.CONNECTED.value


# =========================================================================
# ATTACK SUITE 2: API LEVEL AUTHORIZATION & VALIDATION ATTACKS
# =========================================================================

def test_attack_api_approve_nonexistent_incident(client):
    """Attack: Attacker tries to approve an incident ID that does not exist."""
    res = client.post("/api/incidents/INC-FAKE-9999/approve", json={"approver": "Attacker"})
    assert res.status_code == 400
    assert "not found" in res.json()["detail"].lower()


def test_attack_api_deny_nonexistent_incident(client):
    """Attack: Attacker tries to deny an incident ID that does not exist."""
    res = client.post("/api/incidents/INC-FAKE-9999/deny", json={"approver": "Attacker"})
    assert res.status_code == 400
    assert "not found" in res.json()["detail"].lower()


def test_attack_api_double_approval(client):
    """Attack: Approving an incident a second time after it was already completed."""
    # Trigger Scenario B
    client.post("/api/trigger/scenario-b")
    # First approval succeeds
    res1 = client.post("/api/incidents/INC-1042/approve", json={"approver": "Analyst1"})
    assert res1.status_code == 200
    assert res1.json()["success"] is True

    # Second approval on already completed incident must fail
    res2 = client.post("/api/incidents/INC-1042/approve", json={"approver": "Analyst2"})
    assert res2.status_code == 400
    assert "cannot approve" in res2.json()["detail"].lower()


def test_attack_api_approve_after_denial(client):
    """Attack: Attempting to approve an incident that was already explicitly denied."""
    client.post("/api/trigger/scenario-b")
    # First deny
    res_deny = client.post("/api/incidents/INC-1042/deny", json={"approver": "Analyst1", "reason": "Testing"})
    assert res_deny.status_code == 200

    # Subsequent approve must fail
    res_app = client.post("/api/incidents/INC-1042/approve", json={"approver": "Analyst2"})
    assert res_app.status_code == 400
    assert "cannot approve" in res_app.json()["detail"].lower()
