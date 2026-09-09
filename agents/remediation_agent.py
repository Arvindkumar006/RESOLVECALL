"""
JARVIS Sentinel - Remediation & Reporting Agent
Built with Strands Agents SDK.
Executes policy-authorized containment actions in the SimulatedEnvironment
and produces formal forensic incident documentation.
"""

from typing import Any, Dict
from strands import Agent
from core.models import IncidentBrief, IncidentStatus
from core.simulation_state import SimulatedEnvironment
from tools.containment_tools import execute_safe_containment, generate_incident_report
from agents.model_factory import get_model


class RemediationAgent:
    def __init__(self):
        self.agent = Agent(
            model=get_model(agent_role="RemediationAgent"),
            tools=[execute_safe_containment, generate_incident_report],
            system_prompt=(
                "You are the Remediation Agent in JARVIS Sentinel. "
                "Execute authorized containment actions on simulated hosts, block C2 firewall rules, "
                "and generate comprehensive post-incident postmortem reports."
            )
        )

    def execute_containment(self, brief: IncidentBrief, authorization_token: str = "") -> Dict[str, Any]:
        env = SimulatedEnvironment()
        host_id = brief.affected_host

        env.add_trace(
            agent_name="RemediationAgent",
            action_type="DISPATCH",
            message=f"Executing remediation for incident {brief.incident_id} on {host_id} (Token: '{authorization_token or 'AUTONOMOUS'}')",
            payload={"incident_id": brief.incident_id, "host_id": host_id, "action": brief.recommended_action}
        )

        prompt = (
            f"Execute containment for incident {brief.incident_id} on host {host_id}.\n"
            f"Action: {brief.recommended_action}\n"
            f"Authorization Token: '{authorization_token}'\n"
            f"Call execute_safe_containment and generate_incident_report."
        )

        result = self.agent(prompt)
        content_text = str(result.message.get("content", [{}])[0].get("text", ""))

        # Verify final simulated host status
        host_status = env.get_host(host_id)
        current_network_status = host_status["status"] if host_status else "UNKNOWN"

        report_md = generate_incident_report(
            incident_id=brief.incident_id,
            host_id=host_id,
            summary=brief.suspected_behavior,
            actions_taken=f"Remediation '{brief.recommended_action}' completed with authorization token: {authorization_token or 'NONE_REQUIRED_AUTONOMOUS'}"
        )

        brief.status = IncidentStatus.RESOLVED
        brief.remediation_result = f"Remediation completed. Host {host_id} status: {current_network_status}. Output: {content_text[:200]}"

        return {
            "success": True,
            "incident_id": brief.incident_id,
            "host_id": host_id,
            "host_status": current_network_status,
            "report_markdown": report_md,
            "summary": content_text
        }
