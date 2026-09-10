"""
Regression tests for the state machine, policy engine, and evidence extractor.

These tests verify the 8 key scenarios identified during the real CALL-E call incident:
  1. Connected + interrupted call → RECOVERY_UNCONFIRMED (NOT DEADLINE_MISSED)
  2. Connected + interrupted call → policy is AMBIGUOUS (NOT INVALID)
  3. Connected + interrupted → policy reason mentions "connected but interrupted"
  4. Call did NOT connect → policy reason mentions "did not reach"
  5. Transcript: CALL-E speech → role "RESOLVECALL AGENT"
  6. Transcript: Recipient speech → role "OPERATIONS CONTACT"
  7. Auth code "authorized" keyword → does NOT extract "orized" as code
  8. DEADLINE_MISSED only when actual deadline has passed

Additional tests for the policy engine core logic (no regressions).
"""

import pytest
from datetime import date, timedelta, datetime, time

from resolvecall.core.models import (
    Incident,
    IncidentStatus,
    PolicyDecision,
    StructuredEvidence,
)
from resolvecall.engine.policy_engine import PolicyEngine
from resolvecall.engine.orchestrator import _normalize_transcript_turns
from resolvecall.extraction.extractor import TranscriptExtractor


# ────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────

@pytest.fixture
def sample_incident():
    return Incident(
        incident_id="INC-REG-001",
        failure_code="GATE_CODE_MISSING",
        failure_description="Driver cannot access gate",
        vendor="FastFreight Inc.",
        phone_number="+18005550100",
        recovery_deadline="11:30",
        required_action="Deliver before 11:30 AM",
    )


@pytest.fixture
def future_deadline_incident():
    """Incident whose deadline is 10 hours in the future — cannot be DEADLINE_MISSED yet."""
    future_time = (datetime.now() + timedelta(hours=10)).strftime("%H:%M")
    return Incident(
        incident_id="INC-FUTURE",
        failure_code="DOCK_BLOCK",
        failure_description="Dock blocked",
        vendor="SlowShip Co.",
        phone_number="+18005550100",
        recovery_deadline=future_time,
        required_action="Resolve before end of shift",
    )


# ────────────────────────────────────────────────────────────
# 1. CALL-E connected + interrupted → policy = AMBIGUOUS
# ────────────────────────────────────────────────────────────

def test_call_connected_interrupted_gives_ambiguous(sample_incident):
    """Regression: call that connects but gets interrupted must NOT produce INVALID policy."""
    evidence = StructuredEvidence(
        resolution_status="UNRESOLVED",
        notes="Call connected; conversation interrupted before commitment obtained",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence, call_connected=True)
    assert result.decision == PolicyDecision.AMBIGUOUS, (
        f"Expected AMBIGUOUS for connected+interrupted call, got {result.decision}"
    )


# ────────────────────────────────────────────────────────────
# 2. Connected+interrupted → reason says "connected but interrupted"
# ────────────────────────────────────────────────────────────

def test_call_connected_interrupted_reason_text(sample_incident):
    """Policy reason must correctly indicate the call connected but conversation was interrupted."""
    evidence = StructuredEvidence(
        resolution_status="UNRESOLVED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence, call_connected=True)
    reason = result.reason.lower()
    assert "connected" in reason, f"Reason should mention 'connected'. Got: {result.reason}"
    assert "interrupt" in reason, f"Reason should mention 'interrupted'. Got: {result.reason}"


# ────────────────────────────────────────────────────────────
# 3. Call did NOT connect → reason says "did not reach"
# ────────────────────────────────────────────────────────────

def test_call_not_connected_reason_text(sample_incident):
    """Policy reason must correctly state the call did NOT reach a live representative."""
    evidence = StructuredEvidence(
        resolution_status="UNRESOLVED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence, call_connected=False)
    reason = result.reason.lower()
    # Should NOT say "connected and interrupted" — it never connected
    assert "did not reach" in reason or "not reach" in reason or "live representative" in reason, (
        f"Reason should indicate no live representative reached. Got: {result.reason}"
    )


# ────────────────────────────────────────────────────────────
# 4. REFUSED resolution → AMBIGUOUS (not INVALID, carrier refused)
# ────────────────────────────────────────────────────────────

def test_refused_evidence_gives_ambiguous(sample_incident):
    """Explicit refusal should produce AMBIGUOUS — carrier said no, not a deadline violation."""
    evidence = StructuredEvidence(
        resolution_status="REFUSED",
        notes="Dispatcher stated: no redeliveries today",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence, call_connected=True)
    assert result.decision == PolicyDecision.AMBIGUOUS, (
        f"Explicit refusal should be AMBIGUOUS (needs retry/escalation), got {result.decision}"
    )


# ────────────────────────────────────────────────────────────
# 5. Valid window within deadline → VALID (no regression)
# ────────────────────────────────────────────────────────────

def test_valid_window_within_deadline(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_start="10:45 AM",
        agreed_window_end="11:15 AM",
        representative_name="Marcus",
        authorization_code="REDEL-4491",
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.VALID
    assert "satisfies" in result.reason.lower()


# ────────────────────────────────────────────────────────────
# 6. Window EXCEEDS deadline → INVALID (no regression)
# ────────────────────────────────────────────────────────────

def test_window_exceeds_deadline_gives_invalid(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_start="12:00 PM",
        agreed_window_end="12:30 PM",
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.INVALID
    assert "violates" in result.reason.lower()


# ────────────────────────────────────────────────────────────
# 7. DEADLINE_MISSED never triggered by policy for future deadline
# ────────────────────────────────────────────────────────────

def test_policy_never_emits_deadline_missed(future_deadline_incident):
    """PolicyEngine should never return INVALID/deadline_missed for an UNRESOLVED call
    when the deadline is still in the future."""
    evidence = StructuredEvidence(
        resolution_status="UNRESOLVED",
        notes="Call interrupted before completion",
    )
    result = PolicyEngine.evaluate(future_deadline_incident, evidence, call_connected=True)
    # Policy output must be AMBIGUOUS
    assert result.decision == PolicyDecision.AMBIGUOUS
    assert result.decision != PolicyDecision.INVALID


# ────────────────────────────────────────────────────────────
# 8. _normalize_transcript_turns: CALL-E agent → "RESOLVECALL AGENT"
# ────────────────────────────────────────────────────────────

def test_transcript_agent_role_normalization():
    """Bot/agent turns must be labeled 'RESOLVECALL AGENT'."""
    raw = [
        {"speaker": "bot", "text": "Hello, this is ResolveCall. I'm calling about shipment 9941."},
        {"speaker": "agent", "text": "Can you confirm the gate code was received?"},
        {"speaker": "assistant", "text": "We need redelivery before 11:30 AM."},
    ]
    turns = _normalize_transcript_turns(raw)
    for turn in turns:
        assert turn["role"] == "RESOLVECALL AGENT", (
            f"Expected 'RESOLVECALL AGENT', got '{turn['role']}' for text: {turn['text']}"
        )


# ────────────────────────────────────────────────────────────
# 9. _normalize_transcript_turns: recipient → "OPERATIONS CONTACT"
# ────────────────────────────────────────────────────────────

def test_transcript_human_role_normalization():
    """Dispatcher/human/callee turns must be labeled 'OPERATIONS CONTACT'."""
    raw = [
        {"speaker": "human", "text": "Yes, I received the gate code."},
        {"role": "dispatcher", "text": "I can have the driver back by 11:15."},
        {"speaker": "callee", "text": "The confirmation code is REDEL-5591."},
    ]
    turns = _normalize_transcript_turns(raw)
    for turn in turns:
        assert turn["role"] == "OPERATIONS CONTACT", (
            f"Expected 'OPERATIONS CONTACT', got '{turn['role']}' for text: {turn['text']}"
        )


# ────────────────────────────────────────────────────────────
# 10. _normalize_transcript_turns: "Bot is speaking:" prefix stripped
# ────────────────────────────────────────────────────────────

def test_transcript_bot_prefix_stripped():
    """'Bot is speaking:' prefix in CALL-E output must be stripped from displayed text."""
    raw = [
        {"speaker": "bot", "text": "Bot is speaking: Good morning, I'm calling about the delayed shipment."},
    ]
    turns = _normalize_transcript_turns(raw)
    assert len(turns) == 1
    assert turns[0]["role"] == "RESOLVECALL AGENT"
    assert not turns[0]["text"].lower().startswith("bot is speaking")
    assert "Good morning" in turns[0]["text"] or "good morning" in turns[0]["text"].lower()


# ────────────────────────────────────────────────────────────
# 11. Extractor: "authorized" keyword does NOT produce "orized" as auth code
# ────────────────────────────────────────────────────────────

def test_extractor_no_partial_auth_code_from_authorized():
    """'authorized' in text must NOT be extracted as an authorization code."""
    dialogue = [
        {"role": "RESOLVECALL AGENT", "text": "I am authorized to negotiate a redelivery."},
        {"role": "OPERATIONS CONTACT", "text": "The driver will be there by 10:45 AM."},
    ]
    call_data = {"status": "completed", "summary": "Call authorized but interrupted."}
    evidence = TranscriptExtractor.extract_evidence(call_data, dialogue)
    
    # "orized" must not appear as authorization_code
    if evidence.authorization_code:
        assert evidence.authorization_code.lower() != "orized", (
            f"Extractor incorrectly parsed 'authorized' → '{evidence.authorization_code}'"
        )
        assert len(evidence.authorization_code) >= 4


# ────────────────────────────────────────────────────────────
# 12. Extractor: real REDEL-XXXX code extracted correctly
# ────────────────────────────────────────────────────────────

def test_extractor_real_code_extracted():
    dialogue = [
        {"role": "RESOLVECALL AGENT", "text": "Can you provide a confirmation code?"},
        {"role": "OPERATIONS CONTACT", "text": "Your redelivery confirmation code is REDEL-9821."},
    ]
    call_data = {
        "status": "completed",
        "summary": "Driver re-routed. Delivery confirmed for 10:45 to 11:15 AM.",
    }
    evidence = TranscriptExtractor.extract_evidence(call_data, dialogue)
    assert evidence.authorization_code == "REDEL-9821", (
        f"Expected 'REDEL-9821', got '{evidence.authorization_code}'"
    )


# ────────────────────────────────────────────────────────────
# 13. Extractor: full happy path (window + name + code)
# ────────────────────────────────────────────────────────────

def test_extractor_full_happy_path():
    dialogue = [
        {"role": "RESOLVECALL AGENT", "text": "Hello, I'm calling about shipment 9941. We need delivery before 11:30 AM."},
        {"role": "OPERATIONS CONTACT", "text": "This is Marcus from dispatch. I see the note about the gate code."},
        {"role": "RESOLVECALL AGENT", "text": "Can the driver redeliver between 10:45 and 11:15 AM?"},
        {"role": "OPERATIONS CONTACT", "text": "Yes, the driver will be back between 10:45 and 11:15 AM."},
        {"role": "RESOLVECALL AGENT", "text": "Please provide a confirmation code."},
        {"role": "OPERATIONS CONTACT", "text": "Your redelivery confirmation code is REDEL-9821."},
    ]
    call_data = {
        "status": "completed",
        "summary": "Driver re-routed with gate code. Delivery confirmed 10:45–11:15 AM.",
    }
    evidence = TranscriptExtractor.extract_evidence(call_data, dialogue)
    assert evidence.resolution_status == "CONFIRMED"
    assert evidence.agreed_window_start is not None and "10:45" in evidence.agreed_window_start
    assert evidence.agreed_window_end is not None and "11:15" in evidence.agreed_window_end
    assert evidence.representative_name == "Marcus"
    assert evidence.authorization_code == "REDEL-9821"


# ────────────────────────────────────────────────────────────
# 14. Policy engine: arbitrary deadlines (no regression)
# ────────────────────────────────────────────────────────────

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


# ────────────────────────────────────────────────────────────
# 15. Policy engine: tomorrow offer → INVALID (exceeds today deadline)
# ────────────────────────────────────────────────────────────

def test_policy_engine_rejects_tomorrow_offer(sample_incident):
    evidence = StructuredEvidence(
        agreed_window_end="Tomorrow morning",
        notes="Only tomorrow available",
        resolution_status="CONFIRMED",
    )
    result = PolicyEngine.evaluate(sample_incident, evidence)
    assert result.decision == PolicyDecision.INVALID
    assert "tomorrow" in result.reason.lower()
