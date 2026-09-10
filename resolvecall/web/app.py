from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from resolvecall.core.config import settings
from resolvecall.core.models import Incident, IncidentStatus
from resolvecall.engine.orchestrator import RecoveryOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("resolvecall.web")

app = FastAPI(
    title="ResolveCall API",
    description="Production Autonomous Incident Recovery Telephony Agent",
    version="1.0.0",
)

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = RecoveryOrchestrator()
app.state.orchestrator = orchestrator

# Mount static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ResolveCall Dashboard Loading...</h1>")


@app.post("/api/incidents/ingest", response_model=Dict[str, Any])
async def ingest_incident(payload: Dict[str, Any]):
    """Ingests any valid operational incident JSON."""
    try:
        incident = orchestrator.ingest_incident(payload)
        return {"ok": True, "incident": incident.dict()}
    except Exception as e:
        logger.error(f"Failed to ingest incident: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/incidents", response_model=List[Dict[str, Any]])
async def list_incidents():
    """Lists all ingested incidents."""
    return [inc.dict() for inc in orchestrator.incidents.values()]


@app.get("/api/incidents/{incident_id}", response_model=Dict[str, Any])
async def get_incident(incident_id: str):
    """Retrieves current state, transcript, extracted evidence, and policy decisions for an incident."""
    incident = orchestrator.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.dict()


@app.post("/api/incidents/{incident_id}/recover")
async def trigger_recovery(
    incident_id: str,
    background_tasks: BackgroundTasks,
):
    """Triggers the real-time autonomous recovery workflow with strict telephony authorization boundaries."""
    incident = orchestrator.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Telephony Authorization: Verify destination phone against E.164 authorized whitelist
    if not settings.is_phone_authorized(incident.phone_number):
        orchestrator.record_auth_audit_event(
            "PERMISSION_DENIED",
            f"Recovery call blocked: phone {incident.phone_number} is not in authorized whitelist.",
            {"target_phone": incident.phone_number},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PHONE_DESTINATION_UNAUTHORIZED",
        )

    if incident.status in (IncidentStatus.CALLING, IncidentStatus.NEGOTIATING, IncidentStatus.PLANNING):
        return {"ok": False, "message": f"Recovery already in progress (Status: {incident.status})"}

    orchestrator.record_auth_audit_event(
        "RECOVERY_AUTHORIZED",
        f"Autonomous recovery initiated for {incident_id}.",
        {"incident_id": incident_id},
    )

    background_tasks.add_task(orchestrator.execute_recovery, incident_id)
    return {"ok": True, "message": f"Autonomous recovery initiated for incident {incident_id}."}



@app.get("/api/incidents/{incident_id}/stream")
async def stream_incident_events(incident_id: str, request: Request):
    """Server-Sent Events (SSE) live stream for real-time dashboard updates."""
    queue = asyncio.Queue()
    orchestrator.register_subscriber(queue)

    async def event_generator():
        try:
            # Yield initial state
            if incident_id in orchestrator.incidents:
                yield {
                    "event": "init",
                    "data": json.dumps(orchestrator.incidents[incident_id].dict(), default=str),
                }

            while True:
                if await request.is_disconnected():
                    break
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": "update",
                        "data": json.dumps(event_data, default=str),
                    }
                except asyncio.TimeoutError:
                    # Heartbeat
                    yield {"event": "ping", "data": "{}"}
        finally:
            orchestrator.unregister_subscriber(queue)

    return EventSourceResponse(event_generator())


@app.get("/api/audit", response_model=List[Dict[str, Any]])
async def get_audit_trail(incident_id: Optional[str] = None):
    """Returns immutable operational audit log events."""
    if incident_id:
        return [e.dict() for e in orchestrator.audit_log if e.incident_id == incident_id]
    return [e.dict() for e in orchestrator.audit_log]


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "active_incidents": len(orchestrator.incidents),
    }


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa(full_path: str):
    """Fallback handler to serve the Single Page Application for frontend client-side routes."""
    if full_path.startswith("api") or full_path.startswith("static"):
        raise HTTPException(status_code=404, detail="Not found")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ResolveCall Dashboard Loading...</h1>")

