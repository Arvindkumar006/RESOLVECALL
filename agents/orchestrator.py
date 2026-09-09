"""
JARVIS Sentinel - Multi-Agent SOC Orchestrator
Coordinates the full multi-agent pipeline:
Telemetry Ingestion -> Detection -> Investigation -> Threat Intel -> Risk Assessment ->
Deterministic Policy Gate -> (Autonomous Resolution OR HITL Escalation Gate).
"""

from typing import Any, Dict, List, Optional
from core.models import (
    IncidentBrief,
    IncidentStatus,
    RiskLevel,
    SecurityEvent,
    PolicyDecision
)
from core.simulation_state import SimulatedEnvironment
from core.policy_engine import DeterministicPolicyEngine
from hitl.state_machine import HITLStateMachine, HITLState
from agents.detection_agent import DetectionAgent
from agents.investigator_agent import InvestigatorAgent
from agents.threat_intel_agent import ThreatIntelAgent
from agents.risk_agent import RiskAgent
from agents.remediation_agent import RemediationAgent


class SentinelOrchestrator:
    """Master multi-agent orchestrator for Autonomous SOC operations."""

    def __init__(self):
        self.detection_agent = DetectionAgent()
        self.investigator_agent = InvestigatorAgent()
        self.threat_intel_agent = ThreatIntelAgent()
        self.risk_agent = RiskAgent()
        self.remediation_agent = RemediationAgent()
        self.hitl_machine = HITLStateMachine()
        self.env = SimulatedEnvironment()

    def process_incident_stream(self, events: List[SecurityEvent], incident_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End-to-end multi-agent processing pipeline.
        Enforces: "Autonomous where safe. Human-controlled where consequential."
        """
        if not events:
            return {"success": False, "error": "No security events provided"}

        # Fresh agent instances for each isolated incident stream investigation
        self.detection_agent = DetectionAgent()
        self.investigator_agent = InvestigatorAgent()
        self.threat_intel_agent = ThreatIntelAgent()
        self.risk_agent = RiskAgent()
        self.remediation_agent = RemediationAgent()

        host_id = events[0].host_id
        inc_id = incident_id or f"INC-{'1042' if 'FINANCE' in host_id else '1019'}"

        self.env.add_trace(
            agent_name="SentinelOrchestrator",
            action_type="PIPELINE_START",
            message=f"Starting multi-agent investigation pipeline for incident {inc_id} on {host_id}",
            payload={"incident_id": inc_id, "host_id": host_id, "event_count": len(events)}
        )

        # Stage 1: Detection Agent
        detection_summary = self.detection_agent.analyze_events(events)

        # Stage 2: Investigator Agent
        investigation_summary = self.investigator_agent.investigate(host_id, detection_summary)

        # Stage 3: Threat Intelligence Agent
        intel_summary = self.threat_intel_agent.enrich(host_id, investigation_summary)

        # Stage 4: Risk Decision Agent
        risk_assessment = self.risk_agent.evaluate_risk(
            host_id=host_id,
            detection_summary=detection_summary,
            investigation_summary=investigation_summary,
            intel_summary=intel_summary,
            evidence_count=len(events)
        )

        # Stage 5: Deterministic Policy Engine Gate (Final Authority)
        policy_decision = DeterministicPolicyEngine.evaluate(
            risk_level=risk_assessment.severity,
            proposed_action=risk_assessment.recommended_action,
            host_id=host_id,
            evidence_count=len(events)
        )

        self.env.add_trace(
            agent_name="DeterministicPolicyEngine",
            action_type="POLICY_GATE",
            message=f"Policy decision for {inc_id}: HITL Required = {policy_decision.requires_hitl} ({policy_decision.policy_rule_id})",
            payload={"rule_id": policy_decision.policy_rule_id, "requires_hitl": policy_decision.requires_hitl}
        )

        # Construct Incident Brief
        brief = IncidentBrief(
            incident_id=inc_id,
            affected_host=host_id,
            confidence=risk_assessment.confidence,
            evidence_count=len(events),
            suspected_behavior=risk_assessment.suspected_behavior,
            recommended_action=risk_assessment.recommended_action,
            potential_impact=risk_assessment.potential_impact,
            status=IncidentStatus.INVESTIGATING,
            risk_level=risk_assessment.severity,
            requires_hitl=policy_decision.requires_hitl,
            investigation_summary=(
                f"DETECTION: {detection_summary}\n\n"
                f"FORENSICS: {investigation_summary}\n\n"
                f"THREAT INTEL: {intel_summary}\n\n"
                f"REASONING: {risk_assessment.reasoning}"
            ),
            policy_decision=policy_decision,
            timeline=[
                f"[{events[0].timestamp}] Initial telemetry anomaly ingested ({len(events)} events)",
                f"Detection: {detection_summary[:90]}...",
                f"Forensics: {investigation_summary[:90]}...",
                f"Intel: {intel_summary[:90]}...",
                f"Policy Decision: {policy_decision.policy_rule_id} (Requires HITL: {policy_decision.requires_hitl})"
            ]
        )

        # Stage 6: Branching based on Policy Gate
        if policy_decision.requires_hitl:
            # Consequential / High Risk -> Register in HITL state machine and HALT execution
            hitl_state = self.hitl_machine.register_incident(brief)
            return {
                "success": True,
                "incident_id": inc_id,
                "host_id": host_id,
                "status": IncidentStatus.AWAITING_APPROVAL.value,
                "hitl_state": hitl_state,
                "requires_hitl": True,
                "incident_brief": brief.model_dump(),
                "message": f"Incident {inc_id} escalated to HITL. Containment BLOCKED pending analyst approval."
            }
        else:
            # Autonomous Bounded Resolution (Zero Human Interruption)
            brief.status = IncidentStatus.REMEDIATING
            self.hitl_machine.register_incident(brief)
            remediation_res = self.remediation_agent.execute_containment(brief, authorization_token="")
            brief.status = IncidentStatus.RESOLVED

            return {
                "success": True,
                "incident_id": inc_id,
                "host_id": host_id,
                "status": IncidentStatus.RESOLVED.value,
                "hitl_state": HITLState.COMPLETED,
                "requires_hitl": False,
                "incident_brief": brief.model_dump(),
                "remediation": remediation_res,
                "message": f"Incident {inc_id} autonomously resolved and closed according to safety policy."
            }

    def handle_hitl_action(self, incident_id: str, action: str, approver: str = "SecOps_Analyst", reason: str = "") -> Dict[str, Any]:
        """
        Processes an explicit human action (/approve or /deny) on an awaiting incident.
        """
        clean_action = action.strip().lower()

        if clean_action == "approve":
            approval_res = self.hitl_machine.approve(incident_id=incident_id, approver=approver)
            if not approval_res["success"]:
                return approval_res

            token = approval_res["token"]
            brief = self.hitl_machine.get_brief(incident_id)
            if not brief:
                return {"success": False, "error": "Incident brief lost"}

            # Execute authorized containment
            remediation_res = self.remediation_agent.execute_containment(brief, authorization_token=token)
            brief.status = IncidentStatus.RESOLVED
            self.hitl_machine.incident_states[incident_id] = HITLState.COMPLETED

            return {
                "success": True,
                "action": "APPROVED",
                "incident_id": incident_id,
                "host_id": brief.affected_host,
                "new_endpoint_status": remediation_res["host_status"],
                "report_markdown": remediation_res["report_markdown"],
                "message": f"Containment APPROVED and executed. Host {brief.affected_host} status is now {remediation_res['host_status']}."
            }

        elif clean_action == "deny":
            deny_res = self.hitl_machine.deny(incident_id=incident_id, reason=reason or "Operator denied containment", actor=approver)
            if not deny_res.get("success"):
                return deny_res

            brief = self.hitl_machine.get_brief(incident_id)
            host_status = self.env.get_host(brief.affected_host)["status"] if brief else "CONNECTED"
            return {
                "success": True,
                "action": "DENIED",
                "incident_id": incident_id,
                "host_id": brief.affected_host if brief else "UNKNOWN",
                "endpoint_status": host_status,
                "message": f"Remediation DENIED by operator. Host remains {host_status}. Containment prevented."
            }

        return {"success": False, "error": f"Invalid action '{action}'. Must be 'approve' or 'deny'."}
