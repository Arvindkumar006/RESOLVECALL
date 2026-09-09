import pytest
from resolvecall.core.models import (
    Incident,
    IncidentStatus,
    PolicyDecision,
    StructuredEvidence,
)
from resolvecall.engine.policy_engine import PolicyEngine


@pytest.fixture
def sample_incident():
    return Incident(
        incident_id="INC-TEST-1",
        shipment_id="SHP-TEST-1",
        failure_code="GATE_LOCKED",
        failure_description="Carrier driver cannot access gate",
        vendor="Test Carrier",
        phone_number="+18005550100",
        recovery_deadline="11:30",
        required_action="Deliver before 11:30",
    )


def test_policy_engine_valid_proposal(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_start="10:45 AM",
        agreed_window_end="11:15 AM",
        representative_name="Marcus",
        authorization_code="REDEL-4491",
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.VALID
    assert "satisfies operational deadline" in result.reason


def test_policy_engine_exact_boundary(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_start="11:00 AM",
        agreed_window_end="11:30 AM",
        representative_name="Sarah",
        authorization_code="OK-123",
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.VALID


def test_policy_engine_violates_deadline(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_start="11:45 AM",
        agreed_window_end="12:15 PM",
        representative_name="Dave",
        authorization_code="REF-889",
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.INVALID
    assert "violates operational deadline" in result.reason


def test_policy_engine_rejects_tomorrow_offer(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_start=None,
        agreed_window_end="Tomorrow morning",
        notes="Dispatcher stated driver can only reschedule for tomorrow",
        raw_evidence_quotes=["We can only do tomorrow"],
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.INVALID
    assert "tomorrow" in result.reason.lower()


def test_policy_engine_refusal(sample_incident):
    evidence = StructuredEvidence(
        resolution_status="REFUSED",
        notes="Driver route full, cannot redeliver",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.INVALID


def test_policy_engine_arbitrary_24h_deadline():
    inc = Incident(
        incident_id="INC-24H",
        failure_code="DOCK_BLOCK",
        failure_description="Dock blocked",
        vendor="Global Trans",
        phone_number="+18005550100",
        recovery_deadline="14:00",
        required_action="Deliver before 14:00",
    )
    ev_good = StructuredEvidence(
        agreed_window_start="13:00",
        agreed_window_end="13:30",
        resolution_status="CONFIRMED",
    )
    res_good = PolicyEngine.evaluate(inc, ev_good)
    assert res_good.decision == PolicyDecision.VALID

    ev_bad = StructuredEvidence(
        agreed_window_start="14:15",
        agreed_window_end="14:45",
        resolution_status="CONFIRMED",
    )
    res_bad = PolicyEngine.evaluate(inc, ev_bad)
    assert res_bad.decision == PolicyDecision.INVALID
