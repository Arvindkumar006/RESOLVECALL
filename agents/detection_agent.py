"""
JARVIS Sentinel - Detection Agent
Built with Strands Agents SDK.
Monitors security event telemetry and filters initial anomalies.
"""

from typing import List
from strands import Agent
from core.models import SecurityEvent
from core.simulation_state import SimulatedEnvironment
from tools.edr_tools import get_host_telemetry
from agents.model_factory import get_model


class DetectionAgent:
    def __init__(self):
        self.agent = Agent(
            model=get_model(agent_role="DetectionAgent"),
            tools=[get_host_telemetry],
            system_prompt=(
                "You are the Detection Agent in JARVIS Sentinel. "
                "Analyze incoming security event streams, query host telemetry when needed, "
                "and identify initial anomalies, host targets, and severity indicators."
            )
        )

    def analyze_events(self, events: List[SecurityEvent]) -> str:
        env = SimulatedEnvironment()
        host_id = events[0].host_id if events else "UNKNOWN"

        env.add_trace(
            agent_name="DetectionAgent",
            action_type="DISPATCH",
            message=f"Ingesting {len(events)} security telemetry events for {host_id}",
            payload={"host_id": host_id, "event_count": len(events)}
        )

        event_descriptions = "\n".join([
            f"- [{e.timestamp}] {e.event_type} on {e.host_id} (User: {e.user}): {e.process_name or ''} {e.command_line or ''} {e.dest_ip or ''}"
            for e in events[:8]
        ])

        prompt = (
            f"Analyze the following security event telemetry on host {host_id}:\n"
            f"Total events: {len(events)}\n"
            f"{event_descriptions}\n"
            f"Identify if suspicious behavior is present and summarize initial findings."
        )

        result = self.agent(prompt)
        findings = str(result.message.get("content", [{}])[0].get("text", ""))

        env.add_trace(
            agent_name="DetectionAgent",
            action_type="ANALYSIS_COMPLETE",
            message=f"Detection triage completed for {host_id}",
            payload={"host_id": host_id, "summary_snippet": findings[:100]}
        )
        return findings
