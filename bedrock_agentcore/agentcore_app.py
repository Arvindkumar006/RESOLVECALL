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
    Supports both native Bedrock Agent Action Group schemas and direct API events.
    """
    # 1. Detect Bedrock Action Group invocation format
    # Bedrock Agent action group requests supply 'actionGroup', 'apiPath', 'httpMethod', and 'requestBody'
    if "actionGroup" in event:
        action_group = event.get("actionGroup")
        api_path = event.get("apiPath", "/investigate")
        http_method = event.get("httpMethod", "POST")
        request_body = event.get("requestBody", {}).get("content", {}).get("application/json", {}).get("properties", [])
        
        # Parse parameters from action group format
        params = {prop["name"]: prop["value"] for prop in request_body} if isinstance(request_body, list) else {}
        scenario = params.get("scenario", "b").lower()
        action = params.get("action")
        incident_id = params.get("incident_id")
        approver = params.get("approver", "AWS_Bedrock_SecOps_Lead")

        if action in ("approve", "deny") and incident_id:
            result = orchestrator.handle_hitl_action(incident_id=incident_id, action=action, approver=approver)
        elif scenario == "a":
            events = TelemetryGenerator.get_scenario_a_events()
            result = orchestrator.process_incident_stream(events, incident_id="INC-1019")
        else:
            events = TelemetryGenerator.get_scenario_b_events()
            result = orchestrator.process_incident_stream(events, incident_id="INC-1042")

        # Bedrock Agent Action Group expected return schema
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "apiPath": api_path,
                "httpMethod": http_method,
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(result)
                    }
                }
            }
        }

    # 2. Direct Invocation / Standard Lambda Event
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
