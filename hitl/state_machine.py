"""
JARVIS Sentinel - Human-in-the-Loop (HITL) State Machine
Enforces strict state blocking on high/critical incidents until explicit analyst authorization.

States:
  IDLE -> DETECTED -> INVESTIGATING -> AWAITING_APPROVAL -> (APPROVED -> EXECUTING -> COMPLETED)
                                                         -> (DENIED -> ABORTED)
"""

from datetime import datetime, timezone
import threading
from typing import Any, Dict, Optional
from core.models import IncidentBrief, IncidentStatus, RiskLevel
from core.simulation_state import SimulatedEnvironment
from core.policy_engine import DeterministicPolicyEngine


class HITLState:
    IDLE = "IDLE"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    COMPLETED = "COMPLETED"


class HITLStateMachine:
    """Thread-safe state machine managing consequential incident gates."""

    _lock = threading.RLock()
    _valid_tokens: Dict[str, Dict[str, Any]] = {}
    _consumed_tokens: set = set()

    def __init__(self):
        self.pending_incidents: Dict[str, IncidentBrief] = {}
        self.incident_states: Dict[str, str] = {}
        self.incident_approvers: Dict[str, str] = {}
        self.incident_tokens: Dict[str, str] = {}

    @classmethod
    def get_all_valid_tokens(cls) -> Dict[str, Dict[str, Any]]:
        with cls._lock:
            return dict(cls._valid_tokens)

    @classmethod
    def consume_token(cls, token: str, host_id: str, action: str) -> bool:
        """Validates and consumes an authorization token for a specific host and action."""
        with cls._lock:
            if not token or token not in cls._valid_tokens:
                return False
            if token in cls._consumed_tokens:
                return False
            token_meta = cls._valid_tokens[token]
            if token_meta.get("host_id") and token_meta["host_id"] != host_id:
                return False
            if token_meta.get("action") and token_meta["action"] != action:
                return False
            cls._consumed_tokens.add(token)
            return True

    @classmethod
    def reset_tokens(cls):
        with cls._lock:
            cls._valid_tokens.clear()
            cls._consumed_tokens.clear()

    def register_incident(self, brief: IncidentBrief) -> str:
        """Register an incident brief into the HITL pipeline."""
        with self._lock:
            self.pending_incidents[brief.incident_id] = brief
            env = SimulatedEnvironment()

            if brief.requires_hitl:
                self.incident_states[brief.incident_id] = HITLState.AWAITING_APPROVAL
                brief.status = IncidentStatus.AWAITING_APPROVAL
                env.add_trace(
                    agent_name="HITLStateMachine",
                    action_type="HITL_GATE",
                    message=f"Incident {brief.incident_id} entered state AWAITING_APPROVAL. Execution BLOCKED pending analyst input.",
                    payload={"incident_id": brief.incident_id, "host": brief.affected_host, "risk": brief.risk_level.value}
                )
            else:
                self.incident_states[brief.incident_id] = HITLState.APPROVED
                brief.status = IncidentStatus.REMEDIATING

            env.active_incidents[brief.incident_id] = brief
            return self.incident_states[brief.incident_id]

    def approve(self, incident_id: str, approver: str = "SecOps_Analyst") -> Dict[str, Any]:
        """
        Explicit analyst approval action. Transitions state to APPROVED and issues authorization token.
        """
        with self._lock:
            if incident_id not in self.pending_incidents:
                return {"success": False, "error": f"Incident {incident_id} not found"}

            current_state = self.incident_states.get(incident_id)
            if current_state != HITLState.AWAITING_APPROVAL:
                return {"success": False, "error": f"Cannot approve incident in state '{current_state}'"}

            clean_approver = approver.strip() or "SecOps_Analyst"
            token = f"HITL_APPROVED_BY_{clean_approver.upper()}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

            self.incident_states[incident_id] = HITLState.APPROVED
            self.incident_approvers[incident_id] = clean_approver
            self.incident_tokens[incident_id] = token

            brief = self.pending_incidents[incident_id]
            brief.status = IncidentStatus.REMEDIATING

            # Register token in class registry with bound metadata
            self._valid_tokens[token] = {
                "incident_id": incident_id,
                "host_id": brief.affected_host,
                "action": brief.recommended_action,
                "approver": clean_approver,
                "issued_at": datetime.now(timezone.utc).isoformat()
            }

            env = SimulatedEnvironment()
            env.record_audit(
                action="HITL_APPROVE",
                target=f"{brief.incident_id}:{brief.affected_host}",
                actor=clean_approver,
                details=f"Analyst approved containment for {brief.suspected_behavior}",
                permitted_by_policy=True
            )
            env.add_trace(
                agent_name="HITLStateMachine",
                action_type="HITL_GATE",
                message=f"Incident {incident_id} APPROVED by {clean_approver}. Authorization token issued.",
                payload={"incident_id": incident_id, "approver": clean_approver, "token": token}
            )
            return {
                "success": True,
                "incident_id": incident_id,
                "status": HITLState.APPROVED,
                "approver": clean_approver,
                "token": token
            }

    def deny(self, incident_id: str, reason: str = "False positive / intentional test", actor: str = "SecOps_Analyst") -> Dict[str, Any]:
        """
        Explicit analyst denial action. Aborts containment and marks incident DENIED.
        """
        with self._lock:
            if incident_id not in self.pending_incidents:
                return {"success": False, "error": f"Incident {incident_id} not found"}

            self.incident_states[incident_id] = HITLState.DENIED
            brief = self.pending_incidents[incident_id]
            brief.status = IncidentStatus.DENIED

            env = SimulatedEnvironment()
            env.record_audit(
                action="HITL_DENY",
                target=f"{brief.incident_id}:{brief.affected_host}",
                actor=actor,
                details=f"Analyst DENIED remediation: {reason}",
                permitted_by_policy=False
            )
            env.add_trace(
                agent_name="HITLStateMachine",
                action_type="HITL_GATE",
                message=f"Incident {incident_id} DENIED by {actor}. Containment PREVENTED.",
                payload={"incident_id": incident_id, "reason": reason}
            )
            return {
                "success": True,
                "incident_id": incident_id,
                "status": HITLState.DENIED,
                "reason": reason
            }

    def get_state(self, incident_id: str) -> Optional[str]:
        with self._lock:
            return self.incident_states.get(incident_id)

    def get_brief(self, incident_id: str) -> Optional[IncidentBrief]:
        with self._lock:
            return self.pending_incidents.get(incident_id)
