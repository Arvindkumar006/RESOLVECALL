"""
Tests for Phase 2: Strands Tools & Safe Simulation State Execution.
"""

import json
import pytest
from core.simulation_state import SimulatedEnvironment
from tools.edr_tools import get_host_telemetry, get_process_tree, check_canary_integrity
from tools.intel_tools import lookup_ip_reputation, lookup_hash_reputation, mitre_attack_lookup
from tools.containment_tools import execute_safe_containment, generate_incident_report


def setup_function():
    from hitl.state_machine import HITLStateMachine
    env = SimulatedEnvironment()
    env._reset_to_default_state()
    HITLStateMachine.reset_tokens()


def test_edr_tools():
    # 1. Host telemetry
    res_str = get_host_telemetry(host_id="FINANCE-PC-07")
    data = json.loads(res_str)
    assert data["host_id"] == "FINANCE-PC-07"
    assert data["status"] == "CONNECTED"
    assert data["canary_tripped"] is True

    # 2. Process tree
    tree_str = get_process_tree(host_id="FINANCE-PC-07")
    tree_data = json.loads(tree_str)
    assert len(tree_data["process_tree"]) >= 3
    cmdlines = [p["cmdline"] for p in tree_data["process_tree"]]
    assert any("vssadmin.exe delete shadows" in cmd for cmd in cmdlines)

    # 3. Canary file integrity
    canary_str = check_canary_integrity(host_id="FINANCE-PC-07")
    canary_data = json.loads(canary_str)
    assert canary_data["canary_tripped"] is True
    assert canary_data["indicator"] == "MASS_ENCRYPTION_TRAP"


def test_threat_intel_tools():
    # 1. IP lookup
    ip_res = json.loads(lookup_ip_reputation(ip="185.220.101.5"))
    assert ip_res["reputation"] == "MALICIOUS"
    assert "LockBit" in ip_res["threat_actor"]
    assert "T1490" in ip_res["mitre_techniques"]

    # 2. Benign IP lookup
    loopback_res = json.loads(lookup_ip_reputation(ip="127.0.0.1"))
    assert loopback_res["reputation"] == "BENIGN"

    # 3. MITRE technique lookup
    mitre_res = json.loads(mitre_attack_lookup(technique_id="T1490"))
    assert mitre_res["name"] == "Inhibit System Recovery"
    assert mitre_res["severity"] == "CRITICAL"


def test_containment_tools_authorization_boundary():
    from hitl.state_machine import HITLStateMachine

    # 1. Attempting isolation without authorization token must be BLOCKED by policy
    blocked_res = json.loads(execute_safe_containment(action="ISOLATE_ENDPOINT", host_id="FINANCE-PC-07", authorization_token=""))
    assert blocked_res["success"] is False
    assert blocked_res["status"] == "BLOCKED_BY_POLICY"

    # Verify endpoint is still CONNECTED
    env = SimulatedEnvironment()
    assert env.get_host("FINANCE-PC-07")["status"] == "CONNECTED"

    # 2. Register valid token bound to FINANCE-PC-07
    HITLStateMachine._valid_tokens["HITL_APPROVED_BY_ANALYST"] = {
        "incident_id": "INC-1042",
        "host_id": "FINANCE-PC-07",
        "action": "ISOLATE_ENDPOINT",
        "approver": "Analyst"
    }

    # Supplying valid approval token successfully isolates endpoint
    success_res = json.loads(execute_safe_containment(
        action="ISOLATE_ENDPOINT",
        host_id="FINANCE-PC-07",
        authorization_token="HITL_APPROVED_BY_ANALYST"
    ))
    assert success_res["success"] is True
    assert success_res["new_network_status"] == "ISOLATED"

    # Verify endpoint is now ISOLATED in simulated state
    assert env.get_host("FINANCE-PC-07")["status"] == "ISOLATED"

    # 3. Attempting to REUSE the same token must fail (single-use protection)
    reused_res = json.loads(execute_safe_containment(
        action="ISOLATE_ENDPOINT",
        host_id="FINANCE-PC-07",
        authorization_token="HITL_APPROVED_BY_ANALYST"
    ))
    assert reused_res["success"] is False
    assert reused_res["status"] == "BLOCKED_BY_POLICY"

    # 3. Auto-close routine dev ticket (requires no token per policy)
    auto_res = json.loads(execute_safe_containment(action="AUTO_CLOSE_TICKET", host_id="DEV-BOX-02"))
    assert auto_res["success"] is True
    assert "autonomously closed" in auto_res["message"]

    # 4. Generate postmortem report
    report = generate_incident_report(
        incident_id="INC-1042",
        host_id="FINANCE-PC-07",
        summary="Ransomware attack neutralized.",
        actions_taken="Endpoint isolated, C2 IP dropped."
    )
    assert "# JARVIS Sentinel - Security Incident Postmortem Report" in report
    assert "INC-1042" in report
    assert "`ISOLATED`" in report
