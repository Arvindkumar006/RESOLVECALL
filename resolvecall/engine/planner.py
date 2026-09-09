from __future__ import annotations

import json
from typing import Dict, Any, List
from resolvecall.core.models import Incident, CallObjective


class RecoveryPlanner:
    """Dynamically parses arbitrary incidents and generates tailored CALL-E recovery plans and objectives."""

    @classmethod
    def create_call_objective(cls, incident: Incident) -> CallObjective:
        """Translates an incident into a dynamic, production-grade CALL-E prompt."""
        # 1. Identify recipient role / department
        contact_str = f"asking for {incident.contact_name}" if incident.contact_name else "asking for dispatch or operations supervisor"

        # 2. Format authorized operational reference details
        auth_items = []
        for k, v in incident.authorization_info.items():
            clean_key = k.lower().replace("token", "reference").replace("pin", "code")
            label = clean_key.replace("_", " ").title()
            auth_items.append(f"{label}: {v}")
        auth_block = "; ".join(auth_items) if auth_items else "Standard operational dispatch clearance"

        # 3. Build the prompt for CALL-E
        prompt_parts: List[str] = [
            f"You are calling {incident.vendor} {contact_str} on behalf of operations regarding shipment/reference '{incident.shipment_id or incident.incident_id}'.",
            f"SITUATION: The status is '{incident.failure_code}' - {incident.failure_description}.",
        ]

        if incident.cargo_information:
            prompt_parts.append(f"CARGO PRIORITY: {incident.cargo_information}.")

        if incident.facility:
            prompt_parts.append(f"DESTINATION FACILITY: {incident.facility}.")

        prompt_parts.extend([
            f"AUTHORIZED RESOLUTION DATA: Provide the following authorized details to resolve the block: {auth_block}.",
            f"MANDATORY GOAL: {incident.required_action}.",
            f"CRITICAL DEADLINE CONSTRAINT: Recovery must be completed before {incident.recovery_deadline}.",
            f"NEGOTIATION RULES: If the representative offers redelivery tomorrow or after {incident.recovery_deadline}, politely but firmly refuse: explain that the operational deadline is {incident.recovery_deadline}, and negotiate an emergency delivery window today before that cutoff.",
            "CONFIRMATION REQUIREMENTS: Once agreed, confirm: (1) The exact delivery/resolution window (start and end times), (2) The representative's name, and (3) Any confirmation or dispatch reference number.",
            "Be professional, articulate, and persist until a definitive agreement or final resolution status is secured."
        ])

        full_prompt = " ".join(prompt_parts)

        return CallObjective(
            incident_id=incident.incident_id,
            target_phone=incident.phone_number,
            recipient_role=incident.contact_name or "Carrier Dispatch",
            prompt=full_prompt,
            deadline=incident.recovery_deadline,
            required_fields=["agreed_window", "representative_name", "authorization_code"],
        )
