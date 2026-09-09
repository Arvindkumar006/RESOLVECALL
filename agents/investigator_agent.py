"""
JARVIS Sentinel - Investigator Agent
Built with Strands Agents SDK.
Reconstructs process execution trees, queries endpoint telemetry, and inspects canary traps.
"""

from strands import Agent
from core.simulation_state import SimulatedEnvironment
from tools.edr_tools import get_host_telemetry, get_process_tree, check_canary_integrity
from agents.model_factory import get_model


class InvestigatorAgent:
    def __init__(self):
        self.agent = Agent(
            model=get_model(agent_role="InvestigatorAgent"),
            tools=[get_host_telemetry, get_process_tree, check_canary_integrity],
            system_prompt=(
                "You are the Investigator Agent in JARVIS Sentinel. "
                "Your objective is to conduct deep endpoint forensics: query process trees, "
                "verify decoy canary file integrity, correlate execution ancestry, and determine blast radius."
            )
        )

    def investigate(self, host_id: str, detection_summary: str) -> str:
        env = SimulatedEnvironment()
        env.add_trace(
            agent_name="InvestigatorAgent",
            action_type="DISPATCH",
            message=f"Beginning deep forensic investigation on host {host_id}",
            payload={"host_id": host_id}
        )

        prompt = (
            f"Conduct in-depth forensic analysis on host: {host_id}.\n"
            f"Context from Detection Agent: {detection_summary}\n"
            f"Use your tools to query the process tree and check canary file integrity on {host_id}."
        )

        result = self.agent(prompt)
        findings = str(result.message.get("content", [{}])[0].get("text", ""))

        env.add_trace(
            agent_name="InvestigatorAgent",
            action_type="ANALYSIS_COMPLETE",
            message=f"Forensic investigation completed for {host_id}",
            payload={"host_id": host_id, "summary_snippet": findings[:100]}
        )
        return findings
