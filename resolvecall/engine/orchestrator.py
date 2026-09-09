from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set

from resolvecall.core.config import settings
from resolvecall.core.models import (
    AuditEvent,
    Incident,
    IncidentStatus,
    PolicyDecision,
    PolicyEvaluationResult,
    StructuredEvidence,
)
from resolvecall.engine.planner import RecoveryPlanner
from resolvecall.engine.policy_engine import PolicyEngine
from resolvecall.extraction.extractor import TranscriptExtractor
from resolvecall.telephony.calle_client import CalleClient, CalleError

logger = logging.getLogger(__name__)


class RecoveryOrchestrator:
    """Production orchestrator managing the real-time autonomous recovery lifecycle."""

    def __init__(self, calle_client: Optional[CalleClient] = None):
        self.calle = calle_client or CalleClient()
        self.incidents: Dict[str, Incident] = {}
        self.audit_log: List[AuditEvent] = []
        self._subscribers: List[asyncio.Queue] = []

    def register_subscriber(self, queue: asyncio.Queue):
        self._subscribers.append(queue)

    def unregister_subscriber(self, queue: asyncio.Queue):
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def _emit_event(self, incident_id: str, event_type: str, description: str, data: Optional[Dict[str, Any]] = None):
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            event_type=event_type,
            description=description,
            data=data or {},
        )
        self.audit_log.append(event)
        logger.info(f"AUDIT [{incident_id}] {event_type}: {description}")

        # Update timestamp of incident
        if incident_id in self.incidents:
            self.incidents[incident_id].updated_at = datetime.now(timezone.utc)

        # Push to all SSE listeners
        payload = {
            "type": "audit_event",
            "event": event.dict(),
            "incident": self.incidents.get(incident_id).dict() if incident_id in self.incidents else None,
        }
        for q in list(self._subscribers):
            try:
                await q.put(payload)
            except Exception:
                pass

    def ingest_incident(self, payload: Dict[str, Any]) -> Incident:
        """Ingests arbitrary operational incident payload."""
        incident = Incident.parse_payload(payload)
        self.incidents[incident.incident_id] = incident
        
        # Synchronously record initial audit event
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            event_type="INCIDENT_RECEIVED",
            description=f"Operational incident received for {incident.vendor} shipment '{incident.shipment_id or incident.incident_id}'. Reason: {incident.failure_code}",
            data={
                "vendor": incident.vendor,
                "deadline": incident.recovery_deadline,
                "phone": incident.phone_number,
                "failure_code": incident.failure_code,
            },
        )
        self.audit_log.append(event)
        return incident

    async def execute_recovery(self, incident_id: str) -> Incident:
        """Executes the full real-time recovery workflow against CALL-E telephony."""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found.")

        # 1. State: PLANNING
        incident.status = IncidentStatus.PLANNING
        await self._emit_event(
            incident_id,
            "RECOVERY_PLANNING",
            f"Autonomous recovery planner analyzing operational constraints and failure '{incident.failure_code}'.",
        )

        call_obj = RecoveryPlanner.create_call_objective(incident)
        await self._emit_event(
            incident_id,
            "PLAN_GENERATED",
            f"Generated recovery objective and strict negotiation rules for {incident.vendor}.",
            {"prompt_summary": call_obj.prompt[:120] + "..."},
        )

        # 2. Security validation
        if not settings.is_phone_authorized(incident.phone_number):
            incident.status = IncidentStatus.FAILED
            await self._emit_event(
                incident_id,
                "SECURITY_REJECTED",
                f"Telephony destination {incident.phone_number} is not in the authorized whitelist.",
            )
            return incident

        # 3. Call Planning via CALL-E
        try:
            plan_res = await asyncio.to_thread(
                self.calle.plan_call,
                to_phone=incident.phone_number,
                goal=call_obj.prompt,
            )
        except Exception as e:
            incident.status = IncidentStatus.FAILED
            await self._emit_event(
                incident_id,
                "PLAN_FAILED",
                f"CALL-E planning failed: {str(e)}",
            )
            return incident

        plan_id = plan_res.get("plan_id")
        confirm_token = plan_res.get("confirm_token")
        ready_to_run = plan_res.get("ready_to_run", True)
        incident.calle_call_id = plan_id

        if not confirm_token or not ready_to_run:
            blocker = plan_res.get("confirm_summary") or plan_res.get("next_step") or "CALL-E requires clarification before execution."
            incident.status = IncidentStatus.FAILED
            await self._emit_event(
                incident_id,
                "PLAN_BLOCKED",
                f"CALL-E call planning blocked: {blocker}",
                {"plan_res": plan_res},
            )
            return incident

        await self._emit_event(
            incident_id,
            "CALL_PLANNED",
            f"CALL-E call planned successfully (Plan ID: {plan_id}).",
            {"plan_id": plan_id},
        )

        # 4. State: CALLING - Trigger real phone call
        incident.status = IncidentStatus.CALLING
        await self._emit_event(
            incident_id,
            "CALL_INITIATED",
            f"Initiating real-time PSTN phone call to {incident.phone_number} via CALL-E.",
            {"to_phone": incident.phone_number},
        )

        try:
            run_res = await asyncio.to_thread(
                self.calle.run_call,
                plan_id=plan_id,
                confirm_token=confirm_token,
            )
        except Exception as e:
            incident.status = IncidentStatus.FAILED
            await self._emit_event(
                incident_id,
                "CALL_FAILED",
                f"CALL-E call execution failed: {str(e)}",
            )
            return incident

        run_id = run_res.get("run_id")
        incident.calle_run_id = run_id
        await self._emit_event(
            incident_id,
            "CALL_RUNNING",
            f"Call run active with CALL-E network (Run ID: {run_id}).",
            {"run_id": run_id},
        )

        # 5. Monitor real-time status & conversation turns
        max_polls = 60
        poll_interval = 4.0
        final_call_data: Dict[str, Any] = {}

        for _ in range(max_polls):
            await asyncio.sleep(poll_interval)
            try:
                status_res = await asyncio.to_thread(self.calle.get_call_status, run_id=run_id)
            except Exception as e:
                logger.warning(f"Error checking CALL-E status: {e}")
                continue

            final_call_data = status_res
            cur_status = str(status_res.get("status", "")).lower()
            res_block = status_res.get("result", {}) or {}
            calling_info = res_block.get("extracted", {}).get("calling", {})
            calling_status = str(calling_info.get("status", "")).lower()
            outcome = res_block.get("outcome")
            next_step_action = status_res.get("next_step", {}).get("action", "")

            # Inspect transcript/activities if available
            raw_activities = status_res.get("activity") or status_res.get("activities") or res_block.get("transcript") or []
            if raw_activities:
                formatted_turns = []
                for a in raw_activities:
                    speaker = a.get("speaker") or a.get("role") or a.get("kind") or "system"
                    text = a.get("text") or a.get("content") or a.get("message") or ""
                    if text:
                        formatted_turns.append({"role": speaker, "text": text})
                incident.transcript = formatted_turns

            # Handle live ringing / calling
            if calling_status in ("calling", "pending") or "ringing" in str(raw_activities).lower():
                if incident.status != IncidentStatus.CALLING:
                    incident.status = IncidentStatus.CALLING

            # Handle active connected call
            if calling_status in ("connected", "in-progress", "active"):
                if incident.status != IncidentStatus.NEGOTIATING:
                    incident.status = IncidentStatus.NEGOTIATING
                    await self._emit_event(
                        incident_id,
                        "CALL_CONNECTED",
                        f"PSTN line connected to {incident.vendor}. Dynamic agent negotiation active.",
                    )

            # Check for terminal call states (completed, ended, no answer, busy, failed)
            is_terminal = (
                cur_status in ("completed", "ended", "success", "failed", "busy", "no-answer")
                or calling_status in ("no answer", "completed", "ended", "failed", "busy", "rejected")
                or outcome is not None
                or next_step_action == "ask_user_for_retry_confirmation"
            )

            if is_terminal:
                terminal_reason = calling_status or cur_status or "Call Concluded"
                await self._emit_event(
                    incident_id,
                    "CALL_COMPLETED",
                    f"Telephony call concluded with status: {terminal_reason.upper()}.",
                    {"status": terminal_reason, "summary": res_block.get("summary")},
                )
                break

        # 6. State: VALIDATING - Evidence Extraction & Policy Check
        incident.status = IncidentStatus.VALIDATING
        await self._emit_event(
            incident_id,
            "EXTRACTION_STARTED",
            "Retrieving real conversation transcript and extracting structured verification evidence.",
        )

        evidence = TranscriptExtractor.extract_evidence(final_call_data, incident.transcript)
        incident.extracted_evidence = evidence.dict()

        await self._emit_event(
            incident_id,
            "EVIDENCE_EXTRACTED",
            f"Extracted recovery commitment: Window: {evidence.agreed_window_start or ''} - {evidence.agreed_window_end or 'N/A'}, Representative: {evidence.representative_name or 'N/A'}, Auth Code: {evidence.authorization_code or 'N/A'}",
            evidence.dict(),
        )

        # 7. Deterministic Policy Evaluation
        policy_eval = PolicyEngine.evaluate(incident, evidence)
        incident.policy_evaluation = policy_eval.dict()

        if policy_eval.decision == PolicyDecision.VALID:
            incident.status = IncidentStatus.RECOVERED
            win_str = f"{evidence.agreed_window_start} – {evidence.agreed_window_end}" if evidence.agreed_window_start else evidence.agreed_window_end
            incident.recovery_summary = f"EMERGENCY REDELIVERY CONFIRMED — {win_str}"
            await self._emit_event(
                incident_id,
                "INCIDENT_RECOVERED",
                f"Incident successfully recovered! Confirmed window '{win_str}' meets cutoff {incident.recovery_deadline}. {policy_eval.reason}",
                policy_eval.dict(),
            )
        elif policy_eval.decision == PolicyDecision.INVALID:
            incident.status = IncidentStatus.DEADLINE_MISSED
            incident.recovery_summary = f"RECOVERY FAILED — Negotiated time exceeds deadline ({policy_eval.reason})"
            await self._emit_event(
                incident_id,
                "DEADLINE_MISSED",
                f"Recovery rejected by policy engine: {policy_eval.reason}",
                policy_eval.dict(),
            )
        else:
            incident.status = IncidentStatus.ESCALATED
            incident.recovery_summary = "ESCALATED — Ambiguous resolution requires human supervisor intervention"
            await self._emit_event(
                incident_id,
                "INCIDENT_ESCALATED",
                f"Incident escalated to operations queue: {policy_eval.reason}",
                policy_eval.dict(),
            )

        return incident
