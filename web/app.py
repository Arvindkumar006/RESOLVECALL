"""
JARVIS Sentinel - Real-Time SOC Command Center Backend
FastAPI web application exposing live agent state, telemetry triggers,
real execution traces, and HITL approval endpoints.
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from core.simulation_state import SimulatedEnvironment
from core.telemetry import TelemetryGenerator
from agents.orchestrator import SentinelOrchestrator

app = FastAPI(title="JARVIS Sentinel SOC Command Center")

# Global singleton orchestrator
orchestrator = SentinelOrchestrator()
env = SimulatedEnvironment()

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class HITLActionRequest(BaseModel):
    approver: str = "SecOps_Analyst"
    reason: Optional[str] = ""


@app.get("/")
def serve_index():
    """Serves the primary SOC Command Center Dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Dashboard index.html not found")
    return FileResponse(index_file)


@app.get("/api/state")
def get_state():
    """Returns actual backend simulation state."""
    with env._lock:
        incidents = {
            inc_id: brief.model_dump() if hasattr(brief, "model_dump") else brief
            for inc_id, brief in env.active_incidents.items()
        }
        return {
            "hosts": env.get_all_hosts(),
            "global_blocked_ips": env.global_blocked_ips,
            "active_incidents": incidents,
            "hitl_states": orchestrator.hitl_machine.incident_states
        }


@app.get("/api/traces")
def get_traces():
    """Returns actual timestamped agent execution traces."""
    return {"traces": env.get_traces(limit=200)}


@app.get("/api/audit")
def get_audit():
    """Returns the immutable security audit log."""
    with env._lock:
        return {"audit_log": list(env.audit_log)}


@app.post("/api/trigger/scenario-a")
def trigger_scenario_a():
    """Triggers Scenario A: Routine Dev Diagnostic (Autonomous Bounded Resolution)."""
    events = TelemetryGenerator.get_scenario_a_events()
    result = orchestrator.process_incident_stream(events, incident_id="INC-1019")
    return JSONResponse(result)


@app.post("/api/trigger/scenario-b")
def trigger_scenario_b():
    """Triggers Scenario B: Critical Ransomware (Mandatory HITL Escalation)."""
    events = TelemetryGenerator.get_scenario_b_events()
    result = orchestrator.process_incident_stream(events, incident_id="INC-1042")
    return JSONResponse(result)


@app.post("/api/incidents/{incident_id}/approve")
def approve_incident(incident_id: str, req: HITLActionRequest = HITLActionRequest()):
    """Analyst approves containment. State transitions and containment executes."""
    result = orchestrator.handle_hitl_action(
        incident_id=incident_id,
        action="approve",
        approver=req.approver or "Senior_SecOps_Alex"
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Approval failed"))
    return JSONResponse(result)


@app.post("/api/incidents/{incident_id}/deny")
def deny_incident(incident_id: str, req: HITLActionRequest = HITLActionRequest()):
    """Analyst denies containment. Containment is aborted and host remains connected."""
    result = orchestrator.handle_hitl_action(
        incident_id=incident_id,
        action="deny",
        approver=req.approver or "Senior_SecOps_Alex",
        reason=req.reason or "False positive / operator override"
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Denial failed"))
    return JSONResponse(result)


@app.post("/api/reset")
def reset_environment():
    """Resets simulated environment and active incidents back to initial baseline."""
    from hitl.state_machine import HITLStateMachine
    env._reset_to_default_state()
    orchestrator.hitl_machine.pending_incidents.clear()
    orchestrator.hitl_machine.incident_states.clear()
    orchestrator.hitl_machine.incident_tokens.clear()
    HITLStateMachine.reset_tokens()
    return {"success": True, "message": "Simulated environment reset to clean baseline."}
