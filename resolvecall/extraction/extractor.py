from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
from resolvecall.core.models import StructuredEvidence

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    """Extracts verifiable operational commitments from real-time CALL-E call runs and transcripts."""

    @classmethod
    def extract_evidence(
        cls,
        call_run_data: Dict[str, Any],
        transcript: Optional[List[Dict[str, str]]] = None,
    ) -> StructuredEvidence:
        """Parses the real-time call response and dialogue turns into StructuredEvidence."""
        evidence = StructuredEvidence()
        
        # 1. Normalize transcript text
        turns = transcript or []
        if not turns and "transcript" in call_run_data:
            turns = call_run_data["transcript"]
        elif not turns and "activities" in call_run_data:
            turns = [
                {"role": a.get("speaker", a.get("role", "speaker")), "text": a.get("text", a.get("content", ""))}
                for a in call_run_data["activities"]
                if a.get("text") or a.get("content")
            ]

        # Aggregate text
        dialogue_lines: List[str] = []
        for t in turns:
            role = t.get("role", "speaker")
            text = t.get("text", "")
            if text:
                dialogue_lines.append(f"{role}: {text}")
        
        full_dialogue = "\n".join(dialogue_lines)
        res_block = call_run_data.get("result", {}) or {}
        summary = call_run_data.get("summary") or res_block.get("summary", "")
        call_status = str(call_run_data.get("status", "")).lower()
        outcome = res_block.get("outcome")
        calling_info = res_block.get("extracted", {}).get("calling", {})
        calling_status = str(calling_info.get("status", "")).lower()

        combined_text = f"{summary}\n{full_dialogue}"

        # 2. Extract resolution status
        if calling_status in ("no answer", "busy", "rejected") or (outcome and not outcome.get("task_completed")):
            evidence.resolution_status = "UNRESOLVED"
            if outcome and outcome.get("evidence"):
                evidence.raw_evidence_quotes.extend(outcome.get("evidence"))
        elif any(term in combined_text.lower() for term in ["cannot accommodate", "refused", "unable to deliver today", "not possible", "delivery rejected"]):
            evidence.resolution_status = "REFUSED"
        elif any(term in combined_text.lower() for term in ["confirmed", "scheduled", "re-routed", "rerouted", "agreed", "dispatching", "driver en route", "approved"]):
            evidence.resolution_status = "CONFIRMED"
        elif call_status in ("completed", "success") and outcome and outcome.get("task_completed"):
            evidence.resolution_status = "CONFIRMED"
        else:
            evidence.resolution_status = "PENDING"

        # 3. Extract time window
        # Pattern 1: "between 10:45 and 11:15 AM" or "from 10:45 to 11:15 AM"
        range_match = re.search(
            r"(?:between|from)?\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)\s*(?:and|to|-|–)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)",
            combined_text,
            re.IGNORECASE,
        )
        if range_match:
            evidence.agreed_window_start = range_match.group(1).strip()
            evidence.agreed_window_end = range_match.group(2).strip()
            evidence.raw_evidence_quotes.append(f"Negotiated Window: {range_match.group(0).strip()}")
        else:
            # Pattern 2: single cutoff or target time "by 11:30 AM" or "at 11:00 AM"
            single_match = re.search(r"(?:by|before|at|around)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)", combined_text, re.IGNORECASE)
            if single_match:
                evidence.agreed_window_end = single_match.group(1).strip()
                evidence.raw_evidence_quotes.append(f"Target Time: {single_match.group(0).strip()}")

        # Check for explicit "tomorrow"
        if re.search(r"\btomorrow\b", combined_text, re.IGNORECASE) and not evidence.agreed_window_end:
            evidence.agreed_window_end = "Tomorrow"
            evidence.raw_evidence_quotes.append("Offered: Tomorrow")

        # 4. Extract representative name
        name_match = re.search(
            r"(?:this is|my name is|speaking with|representative|dispatcher)\s+([A-Za-z]+)(?:\s+([A-Za-z]+))?",
            combined_text,
            re.IGNORECASE,
        )
        if name_match:
            first = name_match.group(1).strip()
            second = (name_match.group(2) or "").strip()
            stop_words = {"from", "at", "with", "in", "here", "calling", "dispatch", "operations", "the", "customer", "support"}
            if second and second.lower() not in stop_words:
                cand = f"{first} {second}"
            else:
                cand = first
            if cand.lower() not in stop_words:
                evidence.representative_name = cand
                evidence.raw_evidence_quotes.append(f"Representative: {cand}")

        # 5. Extract confirmation or authorization code
        for auth_match in re.finditer(
            r"(?:confirmation\s+code|confirmation\s+number|reference\s+number|reference\s+code|auth\s+code|ticket\s+number|confirmation|reference|ticket|auth|code)(?:\s*(?:is|#|:|-))?\s*([A-Za-z0-9-]{4,18})",
            combined_text,
            re.IGNORECASE,
        ):
            code = auth_match.group(1).strip()
            if code.lower() not in ["code", "number", "auth", "ticket", "here", "that", "this"] and (not code.isdigit() or len(code) >= 3):
                evidence.authorization_code = code
                evidence.raw_evidence_quotes.append(f"Confirmation Code: {code}")
                break

        # 6. Set notes
        evidence.notes = summary or (f"Extracted from {len(turns)} dialogue turns" if turns else "No dialogue recorded")

        return evidence
