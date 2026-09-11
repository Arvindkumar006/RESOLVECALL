from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
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
    description="Autonomous Incident Recovery Telephony Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = RecoveryOrchestrator()

# Mount static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ─────────────────────────────────────────────────────────────────────────────
# API Key Authentication
# ─────────────────────────────────────────────────────────────────────────────

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_key_from_request(
    api_key_header: Optional[str],
    bearer: Optional[HTTPAuthorizationCredentials],
) -> Optional[str]:
    """Extract the supplied key from either X-API-Key header or Bearer token."""
    if api_key_header:
        return api_key_header
    if bearer and bearer.credentials:
        return bearer.credentials
    return None


async def require_api_key(
    api_key_header: Optional[str] = Security(_api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme),
) -> None:
    """FastAPI dependency that enforces API key authentication.

    FAIL CLOSED: if RESOLVECALL_API_KEY is not configured, all protected
    endpoints return 401 — authentication is never silently disabled.
    """
    configured_key = settings.RESOLVECALL_API_KEY.strip()

    # Fail closed — no configured key means no access
    if not configured_key:
        raise HTTPException(
            status_code=401,
            detail="API authentication is not configured on this server. Set RESOLVECALL_API_KEY.",
        )

    supplied_key = _resolve_key_from_request(api_key_header, bearer)

    if not supplied_key or supplied_key != configured_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Supply via X-API-Key header or Authorization: Bearer.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ResolveCall Dashboard Loading...</h1>")


@app.post("/api/incidents/ingest", response_model=Dict[str, Any], dependencies=[Depends(require_api_key)])
async def ingest_incident(payload: Dict[str, Any]):
    """Ingests any valid operational incident JSON."""
    try:
        incident = orchestrator.ingest_incident(payload)
        return {"ok": True, "incident": incident.dict()}
    except Exception as e:
        logger.error(f"Failed to ingest incident: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/incidents", response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key)])
async def list_incidents():
    """Lists all ingested incidents."""
    return [inc.dict() for inc in orchestrator.incidents.values()]


@app.get("/api/incidents/{incident_id}", response_model=Dict[str, Any], dependencies=[Depends(require_api_key)])
async def get_incident(incident_id: str):
    """Retrieves current state, transcript, extracted evidence, and policy decisions for an incident."""
    incident = orchestrator.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.dict()


@app.post("/api/incidents/{incident_id}/recover", dependencies=[Depends(require_api_key)])
async def trigger_recovery(incident_id: str, background_tasks: BackgroundTasks):
    """Triggers the real-time autonomous recovery workflow."""
    incident = orchestrator.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status in (IncidentStatus.CALLING, IncidentStatus.NEGOTIATING, IncidentStatus.PLANNING):
        return {"ok": False, "message": f"Recovery already in progress (Status: {incident.status})"}

    background_tasks.add_task(orchestrator.execute_recovery, incident_id)
    return {"ok": True, "message": f"Autonomous recovery initiated for incident {incident_id}."}


@app.get("/api/incidents/{incident_id}/stream", dependencies=[Depends(require_api_key)])
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


@app.get("/api/audit", response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key)])
async def get_audit_trail(incident_id: Optional[str] = None):
    """Returns structured operational audit log events."""
    if incident_id:
        return [e.dict() for e in orchestrator.audit_log if e.incident_id == incident_id]
    return [e.dict() for e in orchestrator.audit_log]


@app.get("/api/health")
async def health_check():
    """Public health endpoint — no authentication required."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "active_incidents": len(orchestrator.incidents),
    }


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not Found")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ResolveCall Loading...</h1>")
