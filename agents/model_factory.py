"""
JARVIS Sentinel - Model Provider & Agent Factory
Seamless dual-mode execution:
- LIVE MODE: Amazon Bedrock (Claude 3.5 Sonnet / Claude Sonnet 4) via Strands BedrockModel
- OFFLINE MODE: OfflineStrandsModel inheriting from strands.models.Model,
  providing deterministic tool selection and reasoning without requiring AWS API keys.
"""

import json
import os
import re
from typing import Any, AsyncGenerator, Dict, List, Optional
from strands.models import Model
from strands.models.bedrock import BedrockModel


class OfflineStrandsModel(Model):
    """
    Strands-native Model implementation for high-fidelity offline execution.
    Inspects messages, selects tools from tool_specs, and generates reasoned responses.
    """

    def __init__(self, agent_role: str = "GeneralSecOps"):
        self.agent_role = agent_role
        self.step_counter = 0

    def update_config(self, **kwargs: Any) -> None:
        pass

    def get_config(self) -> Dict[str, Any]:
        return {"agent_role": self.agent_role, "mode": "OFFLINE_SIMULATION"}

    async def structured_output(self, *args, **kwargs) -> AsyncGenerator[dict[str, Any], None]:
        yield {}

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        tool_specs: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        *args,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Yields Bedrock-standard stream events to drive Strands agent loop:
        1. If tools are available and haven't been called yet for this prompt, triggers toolUse.
        2. Once toolResult is returned in conversation history, synthesizes final analysis.
        """
        self.step_counter += 1

        # Check if previous message contained tool results
        last_message = messages[-1] if messages else {}
        content_items = last_message.get("content", [])
        has_tool_result = any("toolResult" in item for item in content_items if isinstance(item, dict))

        available_tool_names = [t.get("name") for t in (tool_specs or [])]

        # Phase 1: Tool Selection (if tools available and no toolResult yet)
        if available_tool_names and not has_tool_result:
            # Extract target host from the latest user prompt
            current_prompt = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    for c in m.get("content", []):
                        if isinstance(c, dict) and "text" in c:
                            current_prompt = c["text"]
                            break
                        elif isinstance(c, str):
                            current_prompt = c
                            break
                if current_prompt:
                    break

            host_match = re.search(r"(FINANCE-PC-07|DEV-BOX-02)", current_prompt)
            target_host = host_match.group(1) if host_match else ("DEV-BOX-02" if "DEV-BOX-02" in current_prompt else "FINANCE-PC-07")
            is_dev = target_host == "DEV-BOX-02"

            # Determine appropriate tool for the agent's role
            tool_to_call = None
            tool_input: Dict[str, Any] = {}

            if "get_host_telemetry" in available_tool_names:
                tool_to_call = "get_host_telemetry"
                tool_input = {"host_id": target_host}
            elif "get_process_tree" in available_tool_names:
                tool_to_call = "get_process_tree"
                tool_input = {"host_id": target_host}
            elif "lookup_ip_reputation" in available_tool_names:
                tool_to_call = "lookup_ip_reputation"
                target_ip = "127.0.0.1" if is_dev else "185.220.101.5"
                tool_input = {"ip": target_ip}
            elif "execute_safe_containment" in available_tool_names:
                tool_to_call = "execute_safe_containment"
                if not is_dev:
                    token_match = re.search(r"(HITL_APPROVED[^\s\"']+)", current_prompt)
                    token = token_match.group(1) if token_match else ""
                    tool_input = {"action": "ISOLATE_ENDPOINT", "host_id": "FINANCE-PC-07", "authorization_token": token}
                else:
                    tool_input = {"action": "AUTO_CLOSE_TICKET", "host_id": "DEV-BOX-02"}

            if tool_to_call:
                tool_call_id = f"call_{tool_to_call}_{self.step_counter}"
                yield {"messageStart": {"role": "assistant"}}
                yield {"contentBlockStart": {"start": {"toolUse": {"toolUseId": tool_call_id, "name": tool_to_call}}}}
                yield {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(tool_input)}}}}
                yield {"contentBlockStop": {}}
                yield {"messageStop": {"stopReason": "tool_use"}}
                return

        # Phase 2: Reasoning Synthesis (After toolResult is in context or standalone)
        response_text = self._generate_reasoned_response(messages, self.agent_role)
        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockStart": {"start": {"text": ""}}}
        yield {"contentBlockDelta": {"delta": {"text": response_text}}}
        yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": "end_turn"}}

    def _generate_reasoned_response(self, messages: List[Dict[str, Any]], role: str) -> str:
        """Synthesizes structured multi-agent reasoning based on agent role."""
        all_text = ""
        for m in messages:
            for c in m.get("content", []):
                if isinstance(c, dict):
                    if "text" in c:
                        all_text += " " + c["text"]
                    elif "toolResult" in c:
                        content = c["toolResult"].get("content", [])
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                all_text += " " + item["text"]
                elif isinstance(c, str):
                    all_text += " " + c

        # Find latest user prompt to determine current incident context
        current_prompt = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                for c in m.get("content", []):
                    if isinstance(c, dict) and "text" in c:
                        current_prompt = c["text"]
                        break
                    elif isinstance(c, str):
                        current_prompt = c
                        break
            if current_prompt:
                break

        is_dev = "DEV-BOX-02" in current_prompt
        is_finance = not is_dev and ("FINANCE-PC-07" in current_prompt or "FINANCE" in current_prompt or "vssadmin" in current_prompt)

        if role == "DetectionAgent":
            if is_finance:
                return (
                    "DETECTION TRIAGE REPORT:\n"
                    "- Anomaly: Multi-stage ransomware execution sequence detected.\n"
                    "- Key Indicators: Macro execution in Excel spawning obfuscated PowerShell, "
                    "vssadmin shadow copy deletion attempt, canary trap breach, and outbound beaconing to 185.220.101.5.\n"
                    "- Host: FINANCE-PC-07\n"
                    "- Initial Severity: CRITICAL"
                )
            else:
                return (
                    "DETECTION TRIAGE REPORT:\n"
                    "- Observation: Developer script 'health_check.py' executed on DEV-BOX-02.\n"
                    "- Metric: Brief CPU spike (91.4%) and local loopback probe to 127.0.0.1:8080.\n"
                    "- Host: DEV-BOX-02\n"
                    "- Initial Severity: LOW (Routine Benign Activity)"
                )

        elif role == "InvestigatorAgent":
            if is_finance:
                return (
                    "INVESTIGATION FINDINGS:\n"
                    "- Target Host: FINANCE-PC-07 (User: claire.finance)\n"
                    "- Process Tree Correlation: explorer.exe (1000) -> excel.exe (4080) -> cmd.exe (4200) -> powershell.exe (4412) -> vssadmin.exe (4890).\n"
                    "- Host Artifacts: Canary file 'canary_trap_01.docx' accessed and mass entropy encryption observed.\n"
                    "- Impact Assessment: Active ransomware detonation attempting to destroy recovery backups."
                )
            else:
                return (
                    "INVESTIGATION FINDINGS:\n"
                    "- Target Host: DEV-BOX-02 (User: alex.dev)\n"
                    "- Process Tree: bash (1) -> python3 (101) running '/home/alex/scripts/health_check.py'.\n"
                    "- Network: Local loopback connection to port 8080 only.\n"
                    "- Impact Assessment: Standard developer baseline service check. Zero malicious persistence or lateral movement."
                )

        elif role == "ThreatIntelAgent":
            if is_finance:
                return (
                    "THREAT INTEL ENRICHMENT:\n"
                    "- Remote Destination: 185.220.101.5 (Port 443)\n"
                    "- Threat Attribution: LockBit Ransomware Group (Confidence: 98.5%)\n"
                    "- MITRE ATT&CK Mapping: T1490 (Inhibit System Recovery), T1059.001 (PowerShell), T1486 (Data Encrypted for Impact).\n"
                    "- Assessment: Verified active Command and Control (C2) node."
                )
            else:
                return (
                    "THREAT INTEL ENRICHMENT:\n"
                    "- Remote Destination: 127.0.0.1 (Localhost)\n"
                    "- Threat Attribution: None (Benign internal system interface)\n"
                    "- File Hash: Clean developer script\n"
                    "- Assessment: No malicious threat feed correlations."
                )

        elif role == "RiskAgent":
            if is_finance:
                return (
                    "RISK ASSESSMENT DECISION:\n"
                    "- Severity: CRITICAL\n"
                    "- Confidence Score: 94%\n"
                    "- Suspected Behavior: Ransomware / Backup Destruction / C2 Beaconing\n"
                    "- Correlated Evidence Count: 17 events\n"
                    "- Recommended Action: ISOLATE_ENDPOINT and DROP C2 IP\n"
                    "- Policy Boundary: HIGH/CRITICAL action requires MANDATORY Human-In-The-Loop approval."
                )
            else:
                return (
                    "RISK ASSESSMENT DECISION:\n"
                    "- Severity: LOW\n"
                    "- Confidence Score: 99%\n"
                    "- Suspected Behavior: Benign Developer Health Check\n"
                    "- Correlated Evidence Count: 3 events\n"
                    "- Recommended Action: AUTO_CLOSE_TICKET\n"
                    "- Policy Boundary: Autonomous resolution permitted per policy POL-001. Zero human interruption required."
                )

        elif role == "RemediationAgent":
            if is_finance:
                return (
                    "REMEDIATION EXECUTION REPORT:\n"
                    "- Host: FINANCE-PC-07\n"
                    "- Action Executed: Host network interface ISOLATED in simulated SDN.\n"
                    "- Perimeter Firewall: Outbound IP 185.220.101.5 BLOCKED.\n"
                    "- Status: CONTAINED.\n"
                    "- Postmortem incident report generated."
                )
            else:
                return (
                    "REMEDIATION EXECUTION REPORT:\n"
                    "- Host: DEV-BOX-02\n"
                    "- Action Executed: Ticket autonomously resolved per POL-001.\n"
                    "- Audit log recorded. Zero operational disruption."
                )

        return f"Autonomous agent analysis completed for {role}."


def get_model(agent_role: str = "GeneralSecOps") -> Model:
    """
    Factory function returning BedrockModel in Live mode or OfflineStrandsModel in Offline mode.
    """
    use_live_bedrock = os.environ.get("USE_BEDROCK", "false").lower() in ("1", "true", "yes")
    has_aws_creds = bool(os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))

    if use_live_bedrock and has_aws_creds:
        model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        return BedrockModel(model_id=model_id)

    return OfflineStrandsModel(agent_role=agent_role)
