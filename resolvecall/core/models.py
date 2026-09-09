from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    PLANNING = "PLANNING"
    CALLING = "CALLING"
    CONNECTED = "CONNECTED"
    NEGOTIATING = "NEGOTIATING"
    VALIDATING = "VALIDATING"
    RECOVERED = "RECOVERED"
    ESCALATED = "ESCALATED"
    DEADLINE_MISSED = "DEADLINE_MISSED"
    FAILED = "FAILED"


class PolicyDecision(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    AMBIGUOUS = "AMBIGUOUS"


class Incident(BaseModel):
    incident_id: str = Field(..., description="Unique operational incident identifier")
    shipment_id: Optional[str] = Field(None, description="Affected shipment, order, or asset ID")
    failure_code: str = Field(..., description="Standard failure code, e.g. GATE_CODE_MISSING, DOCK_REFUSED")
    failure_description: str = Field(..., description="Human or API explanation of what failed")
    cargo_information: Optional[str] = Field(None, description="Cargo details, e.g. $60,000 temperature-sensitive pharmaceuticals")
    facility: Optional[str] = Field(None, description="Destination facility or facility name")
    vendor: str = Field(..., description="Carrier, vendor, or third-party service provider name")
    contact_name: Optional[str] = Field(None, description="Dispatcher or contact person name if known")
    phone_number: str = Field(..., description="E.164 phone number to dial for recovery")
    recovery_deadline: str = Field(..., description="ISO datetime or HH:MM time before which recovery must occur")
    authorization_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Authorized tokens/codes to provide, e.g. gate_code, po_number, dock_pin"
    )
    required_action: str = Field(..., description="Required operational outcome, e.g. redelivery today within window")
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    calle_call_id: Optional[str] = None
    calle_run_id: Optional[str] = None
    transcript: List[Dict[str, str]] = Field(default_factory=list)
    recovery_summary: Optional[str] = None
    extracted_evidence: Optional[Dict[str, Any]] = None
    policy_evaluation: Optional[Dict[str, Any]] = None


class CallObjective(BaseModel):
    incident_id: str
    target_phone: str
    recipient_role: str
    prompt: str
    deadline: str
    required_fields: List[str]


class StructuredEvidence(BaseModel):
    agreed_window_start: Optional[str] = None
    agreed_window_end: Optional[str] = None
    representative_name: Optional[str] = None
    authorization_code: Optional[str] = None
    resolution_status: str = "PENDING"
    notes: Optional[str] = None
    raw_evidence_quotes: List[str] = Field(default_factory=list)


class PolicyEvaluationResult(BaseModel):
    decision: PolicyDecision
    deadline_evaluated: str
    proposed_window_end: Optional[str] = None
    reason: str
    timestamp: datetime = Field(default_factory=utc_now)


class AuditEvent(BaseModel):
    event_id: str
    incident_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: str
    description: str
    data: Dict[str, Any] = Field(default_factory=dict)
