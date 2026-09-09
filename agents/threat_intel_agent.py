"""
JARVIS Sentinel - Threat Intelligence Agent
Built with Strands Agents SDK.
Enriches indicators of compromise (IOCs) with threat feeds, actor attribution, and MITRE tactics.
"""

from strands import Agent
from core.simulation_state import SimulatedEnvironment
from tools.intel_tools import lookup_ip_reputation, lookup_hash_reputation, mitre_attack_lookup
from agents.model_factory import get_model


class ThreatIntelAgent:
    def __init__(self):
        self.agent = Agent(
            model=get_model(agent_role="ThreatIntelAgent"),
            tools=[lookup_ip_reputation, lookup_hash_reputation, mitre_attack_lookup],
            system_prompt=(
                "You are the Threat Intelligence Agent in JARVIS Sentinel. "
                "Enrich indicators of compromise (IPs, hashes, domains) with commercial threat feeds, "
                "identify threat actor attribution, and map behaviors to MITRE ATT&CK techniques."
            )
        )

    def enrich(self, host_id: str, investigation_summary: str) -> str:
        env = SimulatedEnvironment()
        env.add_trace(
            agent_name="ThreatIntelAgent",
            action_type="DISPATCH",
            message=f"Enriching threat intelligence for {host_id}",
            payload={"host_id": host_id}
        )

        prompt = (
            f"Analyze and enrich IOCs for target host {host_id}.\n"
            f"Forensic Context: {investigation_summary}\n"
            f"Query reputation for observed network destinations and map observed techniques to MITRE ATT&CK."
        )

        result = self.agent(prompt)
        findings = str(result.message.get("content", [{}])[0].get("text", ""))

        env.add_trace(
            agent_name="ThreatIntelAgent",
            action_type="ANALYSIS_COMPLETE",
            message=f"Threat intelligence enrichment completed for {host_id}",
            payload={"host_id": host_id, "summary_snippet": findings[:100]}
        )
        return findings
