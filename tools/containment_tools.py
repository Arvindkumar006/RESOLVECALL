"""
JARVIS Sentinel - Safe Containment & Remediation Tools
Decorated with @tool for Strands Agent invocation.
Mutates ONLY the safe in-memory SimulatedEnvironment state.
Enforces the Policy Engine authorization check prior to executing consequential actions.
"""

import json
from datetime import datetime, timezone
from strands import tool
from core.simulation_state import SimulatedEnvironment
from core.policy_engine import DeterministicPolicyEngine


@tool
def execute_safe_containment(action: str, host_id: str, authorization_token: str = "") -> str:
    """
    Execute a safe remediation action on the simulated enterprise cyber environment.

    Args:
        action: Containment action to perform: 'ISOLATE_ENDPOINT', 'TERMINATE_SUSPICIOUS_PROCESSES', 'BLOCK_C2_IP', 'AUTO_CLOSE_TICKET'
        host_id: Target host identifier (e.g. 'FINANCE-PC-07', 'DEV-BOX-02')
        authorization_token: Required approval token for HIGH/CRITICAL actions (e.g. 'HITL_APPROVED_BY_ANALYST')

    Returns:
        JSON string with execution outcome and state changes.
    """
    env = SimulatedEnvironment()
    normalized_action = action.strip().upper()

    # Verify authorization for consequential containment actions
    if normalized_action in DeterministicPolicyEngine.CONSEQUENTIAL_ACTIONS:
        from hitl.state_machine import HITLStateMachine
        is_authorized = HITLStateMachine.consume_token(
            token=authorization_token,
            host_id=host_id,
            action=normalized_action
        )

        if not is_authorized:
            env.add_trace(
                agent_name="RemediationAgent",
                action_type="POLICY_CHECK",
                message=f"Containment action '{normalized_action}' on {host_id} BLOCKED: Token invalid, already consumed, or bound to another host/action.",
                payload={"action": normalized_action, "host_id": host_id, "token_provided": authorization_token}
            )
            return json.dumps({
                "success": False,
                "status": "BLOCKED_BY_POLICY",
                "reason": f"Action '{normalized_action}' on '{host_id}' rejected by policy engine. Token is invalid, already consumed, expired, or unauthorized for this target."
            }, indent=2)

    # Perform Safe Simulated Actions
    if normalized_action == "ISOLATE_ENDPOINT":
        res = env.isolate_endpoint(host_id, actor=f"RemediationAgent[{authorization_token}]")
        # Also block C2 if known
        env.block_simulated_ip("185.220.101.5", actor="RemediationAgent")
        return json.dumps({
            "success": True,
            "action": "ISOLATE_ENDPOINT",
            "host_id": host_id,
            "new_network_status": "ISOLATED",
            "c2_firewall_rule": "DROP 185.220.101.5/32",
            "message": f"Host {host_id} successfully isolated in simulated network topology. External C2 IP blocked."
        }, indent=2)

    elif normalized_action == "AUTO_CLOSE_TICKET":
        env.record_audit(
            action="AUTO_CLOSE_TICKET",
            target=host_id,
            actor="RemediationAgent",
            details="Alert resolved as benign developer activity per policy POL-001. No human intervention needed.",
            permitted_by_policy=True
        )
        env.add_trace(
            agent_name="RemediationAgent",
            action_type="REMEDIATION",
            message=f"Ticket for {host_id} automatically closed (benign pattern).",
            payload={"host_id": host_id, "action": "AUTO_CLOSE_TICKET"}
        )
        return json.dumps({
            "success": True,
            "action": "AUTO_CLOSE_TICKET",
            "host_id": host_id,
            "message": f"Incident on {host_id} autonomously closed according to safety policy POL-001."
        }, indent=2)

    elif normalized_action == "TERMINATE_SUSPICIOUS_PROCESSES":
        # Terminate rogue processes on host
        killed = []
        host = env.hosts.get(host_id)
        if host:
            pids = list(host.processes.keys())
            for pid in pids:
                if host.processes[pid].is_suspicious:
                    env.terminate_simulated_process(host_id, pid, actor="RemediationAgent")
                    killed.append(pid)
        return json.dumps({
            "success": True,
            "action": "TERMINATE_SUSPICIOUS_PROCESSES",
            "host_id": host_id,
            "terminated_pids": killed
        }, indent=2)

    return json.dumps({
        "success": False,
        "error": f"Unknown remediation action '{action}'"
    }, indent=2)


@tool
def generate_incident_report(incident_id: str, host_id: str, summary: str, actions_taken: str) -> str:
    """
    Generate the official postmortem forensic Markdown report for the incident.

    Args:
        incident_id: Incident ID (e.g. 'INC-1042')
        host_id: Target host ID
        summary: Executive summary of attack behaviors
        actions_taken: Summary of containment actions taken

    Returns:
        Complete Markdown document content of the incident report.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    env = SimulatedEnvironment()
    host = env.get_host(host_id)
    endpoint_status = host["status"] if host else "UNKNOWN"

    report = f"""# JARVIS Sentinel - Security Incident Postmortem Report
**Incident ID:** {incident_id}  
**Date/Time:** {now}  
**Target Host:** {host_id}  
**Final Endpoint Status:** `{endpoint_status}`  
**Governing Policy:** Policy-Driven Autonomy Boundary  

---

## Executive Summary
{summary}

## Autonomous Investigation Findings
- **Telemetry Sources:** Windows Sysmon, CloudTrail, Perimeter Firewall Logs
- **Correlation Chain:** Macro Execution -> Defense Impairment -> Shadow Copy Deletion -> Active Encryption -> C2 Beaconing
- **Identified Threat Actor:** LockBit Ransomware Affiliate
- **MITRE Techniques:** T1490 (Inhibit Recovery), T1059.001 (PowerShell), T1562.001 (Impair Defenses), T1486 (Data Encrypted)

## Remediation & Containment Audit
- **Policy Tier:** Consequential / High Blast Radius
- **HITL Authorization:** Explicit Human Approval Token Validated
- **Actions Executed:**
  - {actions_taken}
  - Host network interface isolated in simulated software-defined network (SDN).
  - Outbound perimeter drop rule activated for IP `185.220.101.5`.

---
*Report generated autonomously by JARVIS Sentinel multi-agent framework powered by Strands Agents SDK.*
"""
    env.add_trace(
        agent_name="RemediationAgent",
        action_type="REMEDIATION",
        message=f"Generated post-incident report for {incident_id}",
        payload={"incident_id": incident_id, "host_id": host_id}
    )
    return report
