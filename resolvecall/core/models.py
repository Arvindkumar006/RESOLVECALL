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
    cargo_information: Optional[str] = Field(None, description="Cargo or item details")
    facility: Optional[str] = Field(None, description="Destination facility or facility name")
    vendor: str = Field(default="Carrier / Service Provider", description="Carrier, vendor, or third-party name")
    contact_name: Optional[str] = Field(None, description="Contact person or department name")
    phone_number: str = Field(..., description="E.164 phone number to dial for recovery")
    recovery_deadline: str = Field(..., description="ISO datetime or HH:MM time before which recovery must occur")
    authorization_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Authorized tokens/codes/constraints"
    )
    required_action: str = Field(..., description="Required operational outcome")

    @classmethod
    def parse_payload(cls, data: Dict[str, Any]) -> "Incident":
        """Normalizes arbitrary runtime operational incident payloads."""
        d = dict(data)
        # Map aliases
        if "contact_phone" in d and "phone_number" not in d:
            d["phone_number"] = d["contact_phone"]
        if "deadline" in d and "recovery_deadline" not in d:
            d["recovery_deadline"] = d["deadline"]
        if "constraints" in d and "authorization_info" not in d:
            d["authorization_info"] = d["constraints"]
        if "vendor" not in d:
            d["vendor"] = d.get("carrier") or d.get("service_provider") or "Operational Contact"
        return cls(**d)
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
