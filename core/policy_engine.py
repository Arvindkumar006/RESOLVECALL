"""
JARVIS Sentinel - Deterministic Policy Engine
Enforces the Policy-Driven Autonomy Boundary:
- LOW / MEDIUM: Autonomous bounded resolution & enrichment (Zero Human Interruption)
- HIGH / CRITICAL: Mandatory Human-in-the-Loop (HITL) authorization gate

Principle: "Autonomous where safe. Human-controlled where consequential."
The LLM may recommend actions, but this Python engine is the FINAL authorization layer.
"""

from typing import List, Optional
from core.models import PolicyDecision, RiskLevel


class DeterministicPolicyEngine:
    """Enterprise policy engine governing multi-agent autonomy boundaries."""

    # Pre-approved non-destructive actions for low/medium risk
    SAFE_AUTONOMOUS_ACTIONS = {
        "AUTO_CLOSE_TICKET",
        "TAG_BENIGN_ALERT",
        "RESET_DIAGNOSTIC_STATE",
        "RECORD_AUDIT_LOG",
        "NOTIFY_CHANNEL_ASYNC"
    }

    # Destructive or high-blast-radius containment actions requiring human sign-off
    CONSEQUENTIAL_ACTIONS = {
        "ISOLATE_ENDPOINT",
        "TERMINATE_CRITICAL_PROCESS",
        "BLOCK_FIREWALL_IP",
        "REVOKE_USER_CREDENTIALS",
        "WIPE_COMPROMISED_HOST"
    }

    @classmethod
    def evaluate(cls, risk_level: RiskLevel, proposed_action: str, host_id: str, evidence_count: int) -> PolicyDecision:
        """
        Evaluates proposed action against deterministic safety rules.
        Returns a binding PolicyDecision object.
        """
        normalized_action = proposed_action.strip().upper()

        # Rule 1: LOW RISK - Autonomous Resolution
        if risk_level == RiskLevel.LOW:
            return PolicyDecision(
                risk_level=RiskLevel.LOW,
                action_permitted=True,
                requires_hitl=False,
                policy_rule_id="POL-001-AUTONOMOUS-ROUTINE",
                explanation=f"Low-risk pattern detected on {host_id}. Action '{normalized_action}' is classified as safe, reversible, and within autonomous bounds. Zero human interruption required.",
                allowed_remediation_actions=["AUTO_CLOSE_TICKET", "TAG_BENIGN_ALERT", "RECORD_AUDIT_LOG"]
            )

        # Rule 2: MEDIUM RISK - Autonomous Investigation & Tagging
        if risk_level == RiskLevel.MEDIUM:
            # Medium risk allows non-destructive triage autonomously
            if normalized_action in cls.SAFE_AUTONOMOUS_ACTIONS or "INVESTIGATE" in normalized_action:
                return PolicyDecision(
                    risk_level=RiskLevel.MEDIUM,
                    action_permitted=True,
                    requires_hitl=False,
                    policy_rule_id="POL-002-AUTONOMOUS-INVESTIGATION",
                    explanation=f"Medium-risk activity on {host_id}. Correlating evidence ({evidence_count} events). Non-destructive logging and triage permitted autonomously.",
                    allowed_remediation_actions=["ENRICH_TICKET", "NOTIFY_CHANNEL_ASYNC", "RECORD_AUDIT_LOG"]
                )
            else:
                return PolicyDecision(
                    risk_level=RiskLevel.MEDIUM,
                    action_permitted=False,
                    requires_hitl=True,
                    policy_rule_id="POL-002B-MEDIUM-CONSEQUENTIAL-GATE",
                    explanation=f"Medium-risk event on {host_id} requested disruptive action '{normalized_action}'. Policy requires human review.",
                    allowed_remediation_actions=[]
                )

        # Rule 3: HIGH RISK - Consequential Impact Gate
        if risk_level == RiskLevel.HIGH:
            return PolicyDecision(
                risk_level=RiskLevel.HIGH,
                action_permitted=False,
                requires_hitl=True,
                policy_rule_id="POL-003-HIGH-RISK-HITL-MANDATORY",
                explanation=f"High-risk security anomaly on {host_id}. Action '{normalized_action}' carries significant operational risk. HITL authorization mandatory.",
                allowed_remediation_actions=["DRAFT_INCIDENT_BRIEF", "REQUEST_HUMAN_APPROVAL"]
            )

        # Rule 4: CRITICAL RISK - High Blast Radius / Containment (Ransomware, Active C2)
        if risk_level == RiskLevel.CRITICAL:
            return PolicyDecision(
                risk_level=RiskLevel.CRITICAL,
                action_permitted=False,  # Blocked until explicit human approval
                requires_hitl=True,
                policy_rule_id="POL-004-CRITICAL-CONTAINMENT-HITL",
                explanation=(
                    f"CRITICAL threat detected on {host_id} with {evidence_count} correlated forensic events. "
                    f"Proposed action '{normalized_action}' (such as network isolation) is consequential and "
                    f"BLOCKED pending analyst authorization in Incident Brief."
                ),
                allowed_remediation_actions=["GENERATE_INCIDENT_BRIEF", "PAUSE_FOR_HITL_APPROVAL"]
            )

        # Fallback default: Strict Deny
        return PolicyDecision(
            risk_level=risk_level,
            action_permitted=False,
            requires_hitl=True,
            policy_rule_id="POL-999-STRICT-DENY-DEFAULT",
            explanation="Unrecognized risk tier or action. Strict deny enforced.",
            allowed_remediation_actions=[]
        )

    @classmethod
    def validate_human_override(cls, decision: PolicyDecision, approved: bool, approver: str) -> bool:
        """
        Validates an explicit human authorization token against an awaiting decision.
        """
        if not decision.requires_hitl:
            return True  # Already autonomous
        return approved and bool(approver.strip())
