"""
JARVIS Sentinel - Simulated Cyber Environment
Safe in-memory state engine representing endpoints, processes, network connections,
firewall rules, and execution audit history.

GUARANTEE: No real system-level commands or destructive changes are EVER run
on the host machine. All containment and remediation safely operate on this model.
"""

from datetime import datetime, timezone
import threading
from typing import Any, Dict, List, Optional
from core.models import EndpointStatus, ProcessNode, TraceEvent


class SimulatedHost:
    def __init__(self, host_id: str, hostname: str, ip: str, os_type: str, owner: str):
        self.host_id = host_id
        self.hostname = hostname
        self.ip = ip
        self.os_type = os_type
        self.owner = owner
        self.status = EndpointStatus.CONNECTED
        self.processes: Dict[int, ProcessNode] = {}
        self.quarantined_files: List[str] = []
        self.blocked_ips: List[str] = []
        self.canary_tripped: bool = False
        self.status_updated_at: str = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "host_id": self.host_id,
            "hostname": self.hostname,
            "ip": self.ip,
            "os_type": self.os_type,
            "owner": self.owner,
            "status": self.status.value,
            "process_count": len(self.processes),
            "quarantined_files": self.quarantined_files,
            "blocked_ips": self.blocked_ips,
            "canary_tripped": self.canary_tripped,
            "status_updated_at": self.status_updated_at,
        }


class SimulatedEnvironment:
    """Singleton/central simulated enterprise cyber environment."""

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimulatedEnvironment, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.hosts: Dict[str, SimulatedHost] = {}
        self.global_blocked_ips: List[str] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.execution_traces: List[TraceEvent] = []
        self.active_incidents: Dict[str, Any] = {}
        self._reset_to_default_state()
        self._initialized = True

    def _reset_to_default_state(self):
        """Seed simulated hosts and baseline workloads."""
        self.hosts.clear()
        self.global_blocked_ips.clear()
        self.audit_log.clear()
        self.execution_traces.clear()
        self.active_incidents.clear()

        # Host 1: Development machine (Scenario A)
        dev_host = SimulatedHost(
            host_id="DEV-BOX-02",
            hostname="dev-box-02.internal.corp",
            ip="10.0.4.112",
            os_type="Ubuntu 22.04 LTS",
            owner="alex.dev@corp.internal"
        )
        dev_host.processes[101] = ProcessNode(
            pid=101,
            name="python3",
            cmdline="python3 /home/alex/scripts/health_check.py --loop --interval 5",
            parent_pid=1,
            is_suspicious=False,
            indicators=["high_cpu_periodic"]
        )
        self.hosts["DEV-BOX-02"] = dev_host

        # Host 2: Finance workstation (Scenario B)
        fin_host = SimulatedHost(
            host_id="FINANCE-PC-07",
            hostname="finance-pc-07.internal.corp",
            ip="10.0.2.45",
            os_type="Windows 11 Enterprise",
            owner="claire.finance@corp.internal"
        )
        fin_host.processes[4080] = ProcessNode(
            pid=4080,
            name="excel.exe",
            cmdline='"C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE" "Q4_Invoice_Review.xlsm"',
            parent_pid=1000,
            is_suspicious=True,
            indicators=["macro_spawned_powershell"]
        )
        fin_host.processes[4412] = ProcessNode(
            pid=4412,
            name="powershell.exe",
            cmdline="powershell.exe -ExecutionPolicy Bypass -NoProfile -EncodedCommand JABzAHIAYwAgAD0A...",
            parent_pid=4080,
            is_suspicious=True,
            indicators=["encoded_command", "vssadmin_shadow_delete", "c2_connect"]
        )
        fin_host.processes[4890] = ProcessNode(
            pid=4890,
            name="vssadmin.exe",
            cmdline="vssadmin.exe delete shadows /all /quiet",
            parent_pid=4412,
            is_suspicious=True,
            indicators=["shadow_copy_deletion", "ransomware_precursor"]
        )
        fin_host.canary_tripped = True
        self.hosts["FINANCE-PC-07"] = fin_host

    def add_trace(self, agent_name: str, action_type: str, message: str, payload: Optional[Dict[str, Any]] = None) -> TraceEvent:
        """Record an explicit execution trace event with ISO timestamp."""
        trace = TraceEvent(
            trace_id=f"TR-{len(self.execution_traces) + 1:04d}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            action_type=action_type,
            message=message,
            payload=payload or {}
        )
        with self._lock:
            self.execution_traces.append(trace)
        return trace

    def get_traces(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return [t.model_dump() for t in self.execution_traces[-limit:]]

    def record_audit(self, action: str, target: str, actor: str, details: str, permitted_by_policy: bool):
        entry = {
            "audit_id": f"AUDIT-{len(self.audit_log) + 1:05d}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "target": target,
            "actor": actor,
            "details": details,
            "permitted_by_policy": permitted_by_policy
        }
        with self._lock:
            self.audit_log.append(entry)
        return entry

    # --- Simulated Safe Remediation Actions ---

    def isolate_endpoint(self, host_id: str, actor: str = "JARVIS_Sentinel") -> Dict[str, Any]:
        """Safely marks simulated endpoint as ISOLATED in virtual network topology."""
        with self._lock:
            if host_id not in self.hosts:
                return {"success": False, "error": f"Host '{host_id}' not found in simulation"}
            host = self.hosts[host_id]
            previous_status = host.status.value
            host.status = EndpointStatus.ISOLATED
            host.status_updated_at = datetime.now(timezone.utc).isoformat()

            audit_entry = self.record_audit(
                action="ISOLATE_ENDPOINT",
                target=host_id,
                actor=actor,
                details=f"Host network interface isolated in simulated SDN. Previous state: {previous_status}",
                permitted_by_policy=True
            )
            self.add_trace(
                agent_name="RemediationAgent",
                action_type="REMEDIATION",
                message=f"Endpoint '{host_id}' state transitioned to ISOLATED",
                payload={"host_id": host_id, "previous_status": previous_status, "new_status": "ISOLATED"}
            )
            return {"success": True, "host_id": host_id, "status": "ISOLATED", "audit": audit_entry}

    def terminate_simulated_process(self, host_id: str, pid: int, actor: str = "JARVIS_Sentinel") -> Dict[str, Any]:
        """Safely removes a process node from the simulated host process table."""
        with self._lock:
            if host_id not in self.hosts:
                return {"success": False, "error": f"Host '{host_id}' not found"}
            host = self.hosts[host_id]
            if pid not in host.processes:
                return {"success": False, "error": f"PID {pid} not found on host {host_id}"}
            proc = host.processes.pop(pid)

            audit_entry = self.record_audit(
                action="TERMINATE_PROCESS",
                target=f"{host_id}:{pid}:{proc.name}",
                actor=actor,
                details=f"Simulated process {proc.name} (PID: {pid}) removed from process table",
                permitted_by_policy=True
            )
            self.add_trace(
                agent_name="RemediationAgent",
                action_type="REMEDIATION",
                message=f"Terminated simulated process {proc.name} (PID {pid}) on {host_id}",
                payload={"host_id": host_id, "pid": pid, "proc_name": proc.name}
            )
            return {"success": True, "host_id": host_id, "terminated_pid": pid, "name": proc.name}

    def block_simulated_ip(self, ip: str, actor: str = "JARVIS_Sentinel") -> Dict[str, Any]:
        """Safely appends IP to simulated perimeter firewall drop rule."""
        with self._lock:
            if ip not in self.global_blocked_ips:
                self.global_blocked_ips.append(ip)
            audit_entry = self.record_audit(
                action="BLOCK_FIREWALL_IP",
                target=ip,
                actor=actor,
                details=f"Simulated perimeter firewall added DROP rule for external C2 {ip}",
                permitted_by_policy=True
            )
            self.add_trace(
                agent_name="RemediationAgent",
                action_type="REMEDIATION",
                message=f"Blocked C2 IP {ip} in simulated perimeter firewall",
                payload={"blocked_ip": ip}
            )
            return {"success": True, "blocked_ip": ip, "audit": audit_entry}

    def get_host(self, host_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            host = self.hosts.get(host_id)
            return host.to_dict() if host else None

    def get_all_hosts(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [h.to_dict() for h in self.hosts.values()]
