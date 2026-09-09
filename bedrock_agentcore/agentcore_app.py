"""
JARVIS Sentinel - Amazon Bedrock AgentCore Runtime Integration
Deploys JARVIS Sentinel multi-agent pipeline into AWS Bedrock AgentCore runtime.
"""

import os
import json
from typing import Any, Dict
from agents.orchestrator import SentinelOrchestrator
from core.telemetry import TelemetryGenerator

orchestrator = SentinelOrchestrator()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Bedrock AgentCore runtime invocation handler.
    """
    scenario = event.get("scenario", "b").lower()
    action = event.get("action")
    incident_id = event.get("incident_id")

    # Handle HITL action if requested
    if action in ("approve", "deny") and incident_id:
        approver = event.get("approver", "AWS_Bedrock_SecOps_Lead")
        result = orchestrator.handle_hitl_action(incident_id=incident_id, action=action, approver=approver)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }

    # Trigger scenario
    if scenario == "a":
        events = TelemetryGenerator.get_scenario_a_events()
        res = orchestrator.process_incident_stream(events, incident_id="INC-1019")
    else:
        events = TelemetryGenerator.get_scenario_b_events()
        res = orchestrator.process_incident_stream(events, incident_id="INC-1042")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(res)
    }


if __name__ == "__main__":
    # Test local invocation
    resp = lambda_handler({"scenario": "b"}, None)
    print("AgentCore Local Invocation Response:", resp["statusCode"])
