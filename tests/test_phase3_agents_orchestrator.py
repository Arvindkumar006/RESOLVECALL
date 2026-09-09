"""
Tests for Phase 3: Multi-Agent Architecture, Policy Boundary, and HITL State Machine.
"""

import pytest
from core.simulation_state import SimulatedEnvironment
from core.telemetry import TelemetryGenerator
from agents.orchestrator import SentinelOrchestrator
from hitl.state_machine import HITLState


def setup_function():
    env = SimulatedEnvironment()
    env._reset_to_default_state()


def test_scenario_a_autonomous_resolution():
    """
    Scenario A: DEV-BOX-02 -> investigation -> LOW -> policy authorization -> autonomous remediation -> RESOLVED.
    Zero human intervention.
    """
    orchestrator = SentinelOrchestrator()
    events = TelemetryGenerator.get_scenario_a_events()

    result = orchestrator.process_incident_stream(events, incident_id="INC-1019")

    assert result["success"] is True
    assert result["incident_id"] == "INC-1019"
    assert result["host_id"] == "DEV-BOX-02"
    assert result["status"] == "RESOLVED"
    assert result["requires_hitl"] is False
    assert result["hitl_state"] == HITLState.COMPLETED

    brief = result["incident_brief"]
    assert brief["risk_level"] == "LOW"
    assert brief["requires_hitl"] is False
    assert "POL-001" in brief["policy_decision"]["policy_rule_id"]

    # Verify audit trail and traces exist
    env = SimulatedEnvironment()
    traces = env.get_traces()
    assert any("DetectionAgent" in t["agent_name"] for t in traces)
    assert any("InvestigatorAgent" in t["agent_name"] for t in traces)
    assert any("ThreatIntelAgent" in t["agent_name"] for t in traces)
    assert any("RiskAgent" in t["agent_name"] for t in traces)
    assert any("DeterministicPolicyEngine" in t["agent_name"] for t in traces)
    assert any("RemediationAgent" in t["agent_name"] for t in traces)

    # Host remains connected since it's a routine benign dev activity
    assert env.get_host("DEV-BOX-02")["status"] == "CONNECTED"


def test_scenario_b_hitl_halt_and_approval():
    """
    Scenario B: FINANCE-PC-07 -> 17 correlated events -> ransomware detection -> CRITICAL ->
    HITL REQUIRED -> execution blocked -> Incident Brief -> APPROVE -> isolate simulated endpoint -> CONTAINED.
    """
    orchestrator = SentinelOrchestrator()
    events = TelemetryGenerator.get_scenario_b_events()

    # Step 1: Ingest and investigate 17 events
    result = orchestrator.process_incident_stream(events, incident_id="INC-1042")

    assert result["success"] is True
    assert result["incident_id"] == "INC-1042"
    assert result["host_id"] == "FINANCE-PC-07"
    assert result["status"] == "AWAITING_APPROVAL"
    assert result["requires_hitl"] is True
    assert result["hitl_state"] == HITLState.AWAITING_APPROVAL

    brief = result["incident_brief"]
    assert brief["risk_level"] == "CRITICAL"
    assert brief["confidence"] >= 0.90
    assert brief["evidence_count"] == 17
    assert brief["recommended_action"] == "ISOLATE_ENDPOINT"

    # MANDATORY CONSTRAINT: Host MUST remain CONNECTED prior to human approval
    env = SimulatedEnvironment()
    assert env.get_host("FINANCE-PC-07")["status"] == "CONNECTED"

    # Step 2: Human clicks APPROVE
    approval_res = orchestrator.handle_hitl_action(
        incident_id="INC-1042",
        action="approve",
        approver="Senior_SecOps_Alex"
    )

    assert approval_res["success"] is True
    assert approval_res["action"] == "APPROVED"
    assert approval_res["new_endpoint_status"] == "ISOLATED"
    assert "report_markdown" in approval_res

    # MANDATORY CONSTRAINT: After approval, simulated endpoint MUST be ISOLATED
    assert env.get_host("FINANCE-PC-07")["status"] == "ISOLATED"

    # Verify perimeter firewall blocked C2 IP
    assert "185.220.101.5" in env.global_blocked_ips

    # Verify audit log records the approved action
    assert any(a["action"] == "HITL_APPROVE" and a["actor"] == "Senior_SecOps_Alex" for a in env.audit_log)
    assert any(a["action"] == "ISOLATE_ENDPOINT" for a in env.audit_log)


def test_scenario_b_hitl_deny_flow():
    """
    Scenario B with DENY: Operator rejects containment.
    Endpoint remains CONNECTED, remediation is aborted, audit records denial.
    """
    orchestrator = SentinelOrchestrator()
    events = TelemetryGenerator.get_scenario_b_events()

    result = orchestrator.process_incident_stream(events, incident_id="INC-1043")
    assert result["status"] == "AWAITING_APPROVAL"

    deny_res = orchestrator.handle_hitl_action(
        incident_id="INC-1043",
        action="deny",
        approver="Analyst_Bob",
        reason="Scheduled red team penetration test simulation"
    )

    assert deny_res["success"] is True
    assert deny_res["action"] == "DENIED"

    # Host MUST remain CONNECTED
    env = SimulatedEnvironment()
    assert env.get_host("FINANCE-PC-07")["status"] == "CONNECTED"
    assert any(a["action"] == "HITL_DENY" and a["actor"] == "Analyst_Bob" for a in env.audit_log)
