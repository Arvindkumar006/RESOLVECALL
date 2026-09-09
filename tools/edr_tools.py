"""
JARVIS Sentinel - EDR and Host Forensics Tools
Decorated with @tool for Strands Agent invocation.
Safely queries the SimulatedEnvironment with zero real command execution.
"""

import json
from strands import tool
from core.simulation_state import SimulatedEnvironment


@tool
def get_host_telemetry(host_id: str) -> str:
    """
    Retrieve current endpoint status, active processes, and security posture for a host.

    Args:
        host_id: Hostname or ID of the endpoint (e.g., 'FINANCE-PC-07', 'DEV-BOX-02')

    Returns:
        JSON string containing host telemetry and running process summary.
    """
    env = SimulatedEnvironment()
    host = env.get_host(host_id)
    if not host:
        return json.dumps({"error": f"Host '{host_id}' not found in endpoint inventory"})

    env.add_trace(
        agent_name="InvestigatorAgent",
        action_type="TOOL_CALL",
        message=f"Queried host telemetry for {host_id}",
        payload={"host_id": host_id, "status": host["status"]}
    )
    return json.dumps(host, indent=2)


@tool
def get_process_tree(host_id: str, root_pid: int = 0) -> str:
    """
    Reconstruct the parent-child process tree and identify suspicious execution chains.

    Args:
        host_id: Target host identifier
        root_pid: Optional specific root PID to trace (0 for all processes)

    Returns:
        JSON string formatted process execution tree with MITRE indicator tags.
    """
    env = SimulatedEnvironment()
    with env._lock:
        host = env.hosts.get(host_id)
        if not host:
            return json.dumps({"error": f"Host '{host_id}' not found"})

        nodes = []
        for pid, p in host.processes.items():
            nodes.append({
                "pid": p.pid,
                "name": p.name,
                "cmdline": p.cmdline,
                "parent_pid": p.parent_pid,
                "is_suspicious": p.is_suspicious,
                "indicators": p.indicators
            })

    env.add_trace(
        agent_name="InvestigatorAgent",
        action_type="TOOL_CALL",
        message=f"Reconstructed process tree for {host_id} ({len(nodes)} processes)",
        payload={"host_id": host_id, "process_count": len(nodes)}
    )
    return json.dumps({"host_id": host_id, "process_tree": nodes}, indent=2)


@tool
def check_canary_integrity(host_id: str) -> str:
    """
    Check ransomware decoy canary files and honeypot traps on the host.

    Args:
        host_id: Target host identifier

    Returns:
        JSON string showing whether canary decoy files were accessed, modified, or encrypted.
    """
    env = SimulatedEnvironment()
    with env._lock:
        host = env.hosts.get(host_id)
        if not host:
            return json.dumps({"error": f"Host '{host_id}' not found"})
        tripped = host.canary_tripped

    env.add_trace(
        agent_name="InvestigatorAgent",
        action_type="TOOL_CALL",
        message=f"Inspected decoy canary files on {host_id}: {'TRIPPED' if tripped else 'INTACT'}",
        payload={"host_id": host_id, "canary_tripped": tripped}
    )
    return json.dumps({
        "host_id": host_id,
        "canary_tripped": tripped,
        "indicator": "MASS_ENCRYPTION_TRAP" if tripped else "NORMAL_BASELINE",
        "description": "Canary trap file C:\\Users\\claire\\Documents\\canary_trap_01.docx modified by untrusted process" if tripped else "All honeypot tokens intact"
    }, indent=2)
