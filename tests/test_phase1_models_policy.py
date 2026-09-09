"""
Tests for Phase 1: Core Models, Simulated Environment, and Deterministic Policy Engine.
"""

import pytest
from core.models import RiskLevel, EndpointStatus
from core.simulation_state import SimulatedEnvironment
from core.policy_engine import DeterministicPolicyEngine
from core.telemetry import TelemetryGenerator


def test_models_and_telemetry():
    scenario_a = TelemetryGenerator.get_scenario_a_events()
    assert len(scenario_a) == 3
    assert scenario_a[0].host_id == "DEV-BOX-02"

    scenario_b = TelemetryGenerator.get_scenario_b_events()
    assert len(scenario_b) == 17
    assert scenario_b[0].host_id == "FINANCE-PC-07"
    assert any(e.dest_ip == "185.220.101.5" for e in scenario_b)
    assert any(e.process_name == "vssadmin.exe" for e in scenario_b)


def test_simulation_state_isolation_and_safety():
    env = SimulatedEnvironment()
    env._reset_to_default_state()

    host = env.get_host("FINANCE-PC-07")
    assert host is not None
    assert host["status"] == EndpointStatus.CONNECTED.value
    assert host["canary_tripped"] is True

    # Safely isolate endpoint
    result = env.isolate_endpoint("FINANCE-PC-07", actor="TestAgent")
    assert result["success"] is True
    assert result["status"] == EndpointStatus.ISOLATED.value

    # Verify state reflects isolation
    updated_host = env.get_host("FINANCE-PC-07")
    assert updated_host["status"] == EndpointStatus.ISOLATED.value

    # Verify traces are added with real timestamps
    traces = env.get_traces()
    assert len(traces) >= 1
    assert any(t["action_type"] == "REMEDIATION" and "FINANCE-PC-07" in t["message"] for t in traces)


def test_deterministic_policy_boundary():
    # 1. LOW Risk must be autonomous and permitted
    decision_low = DeterministicPolicyEngine.evaluate(
        risk_level=RiskLevel.LOW,
        proposed_action="AUTO_CLOSE_TICKET",
        host_id="DEV-BOX-02",
        evidence_count=3
    )
    assert decision_low.action_permitted is True
    assert decision_low.requires_hitl is False
    assert decision_low.policy_rule_id == "POL-001-AUTONOMOUS-ROUTINE"

    # 2. CRITICAL Risk (such as Ransomware isolation) MUST require HITL and be blocked
    decision_crit = DeterministicPolicyEngine.evaluate(
        risk_level=RiskLevel.CRITICAL,
        proposed_action="ISOLATE_ENDPOINT",
        host_id="FINANCE-PC-07",
        evidence_count=17
    )
    assert decision_crit.action_permitted is False  # Blocked until human approval
    assert decision_crit.requires_hitl is True
    assert decision_crit.policy_rule_id == "POL-004-CRITICAL-CONTAINMENT-HITL"

    # 3. Human override verification
    # Denied or empty approver must fail validation
    assert DeterministicPolicyEngine.validate_human_override(decision_crit, approved=False, approver="SecOpsAnalyst") is False
    assert DeterministicPolicyEngine.validate_human_override(decision_crit, approved=True, approver="") is False
    # Explicit approved human token succeeds
    assert DeterministicPolicyEngine.validate_human_override(decision_crit, approved=True, approver="Senior_Analyst_J_Doe") is True
