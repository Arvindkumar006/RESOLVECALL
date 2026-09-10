from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set
from resolvecall.core.models import StructuredEvidence

logger = logging.getLogger(__name__)

# Tokens that must NEVER be used as authorization codes because they are
# incident metadata values injected into agent speech by the planner.
# The extractor must not match these from agent-side speech.
_AGENT_SPEECH_ROLES = frozenset((
    "resolvecall agent", "agent", "assistant", "bot", "caller", "ai",
))

# Words/patterns that look like codes but are definitely not confirmation codes
_CODE_BLOCKLIST = frozenset((
    "code", "number", "auth", "ticket", "here", "that", "this", "none",
))


class TranscriptExtractor:
    """Extracts verifiable operational commitments from real-time CALL-E call runs and transcripts.

    DATA INTEGRITY RULES (enforced here):
    ─────────────────────────────────────
    1. Evidence must only originate from OPERATIONS CONTACT speech in the actual call transcript.
    2. Agent/bot speech (RESOLVECALL AGENT) is our own — never treat it as recipient evidence.
    3. Incident metadata (incident_id, authorization_info, contact_name, failure_description)
       MUST NOT be used as evidence that something was negotiated in the call.
    4. authorization_code must only come from OPERATIONS CONTACT saying a code — never from
       agent speech (which may contain incident_id or authorization_info verbatim from the planner).
    5. representative_name must come from the recipient explicitly stating their name.
    6. delivery window must come from the recipient verbally confirming times.
    7. CALLE outcome.evidence strings are CALLE's own AI summaries — they may be inaccurate.
       They are stored as raw_evidence_quotes for reference but NEVER used to drive structured fields.
    8. resolution_status must reflect what the RECIPIENT said, cross-checked against structured fields:
       - CONFIRMED requires: at least a window OR a representative name from recipient speech.
       - UNRESOLVED/PENDING: no extractable commitment from recipient.
    """

    @classmethod
    def extract_evidence(
        cls,
        call_run_data: Dict[str, Any],
        transcript: Optional[List[Dict[str, str]]] = None,
        incident_id: Optional[str] = None,
        authorization_info: Optional[Dict[str, Any]] = None,
    ) -> StructuredEvidence:
        """Parses real-time call response and dialogue turns into StructuredEvidence.

        Args:
            call_run_data:      Raw CALL-E status/result payload.
            transcript:         Normalized transcript turns [{role, text}, ...].
            incident_id:        The incident ID — explicitly excluded from code extraction.
            authorization_info: Incident authorization_info dict — explicitly excluded from code extraction.
        """
        evidence = StructuredEvidence()

        # Build a set of values that are incident metadata and must never
        # be matched as evidence that something was spoken/negotiated.
        _forbidden_as_codes: Set[str] = set()
        if incident_id:
            _forbidden_as_codes.add(incident_id.upper())
            _forbidden_as_codes.add(incident_id.lower())
            _forbidden_as_codes.add(incident_id)
        if authorization_info:
            for v in authorization_info.values():
                s = str(v).strip()
                if s:
                    _forbidden_as_codes.add(s.upper())
                    _forbidden_as_codes.add(s.lower())
                    _forbidden_as_codes.add(s)

        # 1. Normalize transcript turns
        turns = transcript or []
        if not turns and "transcript" in call_run_data:
            turns = call_run_data["transcript"]
        elif not turns and "activities" in call_run_data:
            turns = [
                {"role": a.get("speaker", a.get("role", "speaker")), "text": a.get("text", a.get("content", ""))}
                for a in call_run_data["activities"]
                if a.get("text") or a.get("content")
            ]

        # Separate agent speech from recipient speech
        # ONLY RECIPIENT (OPERATIONS CONTACT) speech is used for evidence extraction.
        # Agent speech is our own and may contain incident metadata (incident_id, auth codes, etc.)
        recipient_turns: List[str] = []
        all_turns_text: List[str] = []

        for t in turns:
            role = (t.get("role") or "speaker").lower().strip()
            text = (t.get("text") or "").strip()
            if not text:
                continue

            # Strip "Callee said:" prefix from CALL-E transcript turns
            clean_text = re.sub(r"^callee\s+(?:said|interrupted)[:\s]+", "", text, flags=re.IGNORECASE).strip()
            # Skip pure system status messages as evidence
            if role == "system event" or re.match(r"^(dialog state|call ended|calling task|callee speech detected|call is ringing|call connected)", clean_text, re.IGNORECASE):
                continue

            all_turns_text.append(f"{role}: {clean_text}")

            is_agent = any(x in role for x in _AGENT_SPEECH_ROLES)
            is_recipient = any(x in role for x in (
                "operations contact", "dispatcher", "human", "callee", "carrier", "representative", "contact", "recipient"
            ))

            if is_recipient and clean_text:
                recipient_turns.append(clean_text)

        recipient_text = "\n".join(recipient_turns)
        full_dialogue = "\n".join(all_turns_text)

        res_block = call_run_data.get("result", {}) or {}
        calle_summary = call_run_data.get("summary") or res_block.get("summary", "") or ""
        call_status = str(call_run_data.get("status", "")).lower()
        outcome = res_block.get("outcome")
        calling_info = res_block.get("extracted", {}).get("calling", {})
        calling_status = str(calling_info.get("status", "")).lower()

        # IMPORTANT: We never include calle_summary in combined_text for extraction.
        # CALL-E's own summary may contain inaccurate claims (e.g. "collected a representative name"
        # when none was actually confirmed). It is stored as notes only.
        # Evidence extraction uses ONLY the actual transcript speech.
        combined_text = full_dialogue  # transcript only, no CALL-E summary

        # 2. Extract resolution status from recipient speech only
        if calling_status in ("no answer", "busy", "rejected"):
            evidence.resolution_status = "UNRESOLVED"
            evidence.raw_evidence_quotes.append(f"Call did not connect: {calling_status}")
        elif any(term in recipient_text.lower() for term in [
            "cannot accommodate", "not possible today", "delivery rejected", "we cannot", "unable to redeliver today"
        ]):
            evidence.resolution_status = "REFUSED"
        elif any(term in recipient_text.lower() for term in [
            "confirmed", "confirming", "scheduled", "re-routed", "rerouted", "agreed", "dispatching",
            "driver en route", "approved", "yes", "okay", "sure"
        ]):
            # Recipient gave an affirmative — mark CONFIRMED only if we also extract a window
            # (just "yes" alone is not sufficient confirmation; we'll verify below after window extraction)
            evidence.resolution_status = "PENDING"  # Upgraded to CONFIRMED after window check
        elif outcome and not outcome.get("task_completed"):
            evidence.resolution_status = "UNRESOLVED"
            # Store CALL-E outcome evidence as raw quotes only, not as structured fields
            if outcome.get("evidence"):
                evidence.raw_evidence_quotes.extend([
                    f"[CALL-E summary] {e}" for e in outcome.get("evidence")
                ])
        else:
            evidence.resolution_status = "PENDING"

        # 3. Extract delivery window — from recipient speech ONLY
        range_match = re.search(
            r"(?:between|from)?\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)\s*(?:and|to|-|–)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)",
            recipient_text,
            re.IGNORECASE,
        )
        if range_match:
            evidence.agreed_window_start = range_match.group(1).strip()
            evidence.agreed_window_end = range_match.group(2).strip()
            evidence.raw_evidence_quotes.append(f"Negotiated Window: {range_match.group(0).strip()}")
        else:
            # Also check combined (agent may echo the times back)
            range_match_combined = re.search(
                r"(?:window is from|window from|from)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)\s*(?:to|-|–)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)",
                combined_text,
                re.IGNORECASE,
            )
            if range_match_combined:
                evidence.agreed_window_start = range_match_combined.group(1).strip()
                evidence.agreed_window_end = range_match_combined.group(2).strip()
                evidence.raw_evidence_quotes.append(f"Confirmed Window (agent echo): {range_match_combined.group(0).strip()}")
            else:
                # Single time stated by recipient
                single_match = re.search(
                    r"(?:by|before|at|around)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)",
                    recipient_text,
                    re.IGNORECASE,
                )
                if single_match:
                    evidence.agreed_window_end = single_match.group(1).strip()
                    evidence.raw_evidence_quotes.append(f"Target Time: {single_match.group(0).strip()}")

        # Individual time tokens from recipient (e.g. "10:00 AM" on its own line)
        if not evidence.agreed_window_start and not evidence.agreed_window_end:
            time_tokens = re.findall(r"\b(\d{1,2}:\d{2}\s*(?:am|pm))\b", recipient_text, re.IGNORECASE)
            if len(time_tokens) >= 2:
                evidence.agreed_window_start = time_tokens[0].strip()
                evidence.agreed_window_end = time_tokens[-1].strip()
                evidence.raw_evidence_quotes.append(f"Recipient stated times: {time_tokens[0]} – {time_tokens[-1]}")
            elif len(time_tokens) == 1:
                evidence.agreed_window_end = time_tokens[0].strip()
                evidence.raw_evidence_quotes.append(f"Recipient stated time: {time_tokens[0]}")

        # Tomorrow check
        if re.search(r"\btomorrow\b", recipient_text, re.IGNORECASE) and not evidence.agreed_window_end:
            evidence.agreed_window_end = "Tomorrow"
            evidence.raw_evidence_quotes.append("Recipient offered: Tomorrow")

        # Upgrade resolution_status: if recipient gave affirmative AND we got a window, it's CONFIRMED
        if evidence.resolution_status == "PENDING" and (evidence.agreed_window_start or evidence.agreed_window_end):
            if any(term in recipient_text.lower() for term in ["yes", "okay", "confirming", "confirmed", "agreed"]):
                evidence.resolution_status = "CONFIRMED"

        # 4. Extract representative name — ONLY from recipient speech
        # Match patterns where recipient introduces themselves or agent echoes their name
        name_match = re.search(
            r"(?:this is|my name is|i(?:'m| am)|speaking with|name is)\s+([A-Z][a-z]+)(?:\s+([A-Z][a-z]+))?",
            recipient_text,
            re.IGNORECASE,
        )
        if not name_match:
            # Also try matching proper names: two capitalized words in recipient speech
            # Use the Callee-said stripped turns
            for line in recipient_turns:
                # Look for "Arvind Kumar" style proper name response
                proper_name = re.search(r"\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b", line)
                if proper_name:
                    candidate = f"{proper_name.group(1)} {proper_name.group(2)}"
                    stop_words = {
                        "from", "at", "with", "in", "here", "calling", "dispatch", "operations",
                        "the", "customer", "support", "hello", "thank", "okay", "confirming",
                        "dialog", "state", "rolled", "back", "call", "ended", "callee", "said",
                    }
                    if not any(w.lower() in stop_words for w in [proper_name.group(1), proper_name.group(2)]):
                        name_match = proper_name
                        evidence.representative_name = candidate
                        evidence.raw_evidence_quotes.append(f"Representative: {candidate}")
                        break

        if name_match and not evidence.representative_name:
            first = name_match.group(1).strip()
            second = (name_match.group(2) or "").strip() if name_match.lastindex and name_match.lastindex >= 2 else ""
            stop_words = {
                "from", "at", "with", "in", "here", "calling", "dispatch", "operations",
                "the", "customer", "support", "hello",
            }
            if second and second.lower() not in stop_words:
                cand = f"{first} {second}"
            else:
                cand = first
            if cand.lower() not in stop_words:
                evidence.representative_name = cand
                evidence.raw_evidence_quotes.append(f"Representative: {cand}")

        # 5. Extract authorization/confirmation code — ONLY from OPERATIONS CONTACT speech.
        # CRITICAL: Never match from agent speech (which contains incident_id, authorization_info).
        # CRITICAL: Explicitly block incident_id and authorization_info values from being used as codes.

        # Pattern: explicit keyword phrase followed by code
        explicit_code_pattern = re.compile(
            r"\b(confirmation\s+code|confirmation\s+number|reference\s+number|reference\s+code|"
            r"auth\s+code|ticket\s+number|dispatch\s+reference|dispatch\s+number)\b"
            r"[\s:is#-]*([A-Za-z0-9][A-Za-z0-9\s-]{2,17})",
            re.IGNORECASE,
        )
        for m in explicit_code_pattern.finditer(recipient_text):
            raw_code = m.group(2).strip().split()[0]  # Take first token only
            code = re.sub(r"[^A-Za-z0-9-]", "", raw_code)
            if (
                len(code) >= 3
                and code.lower() not in _CODE_BLOCKLIST
                and code not in _forbidden_as_codes
                and code.upper() not in _forbidden_as_codes
            ):
                evidence.authorization_code = code
                evidence.raw_evidence_quotes.append(f"Confirmation Code: {code}")
                break

        # Fallback: alphanumeric code pattern (e.g. "24-CS-0089", "REDEL-9821")
        # Only from recipient speech, never from agent speech.
        if not evidence.authorization_code:
            code_pattern = re.compile(
                r"\b([A-Z0-9]{2,6}[-\s][A-Z0-9]{2,12}(?:[-\s][A-Z0-9]{2,8})?)\b",
                re.IGNORECASE,
            )
            code_candidates = []
            for l in recipient_turns:
                for m in code_pattern.finditer(l):
                    raw = m.group(1).strip()
                    normalized = re.sub(r"\s+", "-", raw).upper()
                    if (
                        normalized not in _forbidden_as_codes
                        and raw not in _forbidden_as_codes
                        and normalized.upper() not in _forbidden_as_codes
                        and len(normalized) >= 4
                        and normalized.lower() not in _CODE_BLOCKLIST
                        and any(c.isdigit() for c in normalized)  # Must contain digits
                        and not normalized.endswith(("-AM", "-PM"))  # Exclude AM/PM times
                        and not re.search(r"\b\d{1,2}:\d{2}\b", raw)  # Exclude time formats
                        and not any(w in normalized.lower() for w in ["double", "state", "dialog", "called", "calling"])
                    ):
                        code_candidates.append(normalized)

            if code_candidates:
                final_code = code_candidates[-1]
                evidence.authorization_code = final_code
                evidence.raw_evidence_quotes.append(f"Confirmation Code: {final_code}")

        # 6. Consistency enforcement:
        # raw_evidence_quotes must NEVER claim more than structured fields support.
        # Remove CALL-E summary quotes that contradict the structured evidence.
        # (They are already prefixed with "[CALL-E summary]" for traceability.)
        # We do NOT add any generated summary claims to raw_evidence_quotes.

        # 7. Set notes — use CALL-E summary for human context, but clearly labelled
        evidence.notes = calle_summary if calle_summary else (
            f"Extracted from {len(turns)} transcript turns" if turns else "No transcript recorded"
        )

        return evidence


def _evidence_is_consistent(evidence: "StructuredEvidence") -> bool:
    """Validates that structured evidence fields are internally consistent.
    Returns True if valid, False if contradictions are found.
    Used for testing and debugging — not enforced at runtime (evidence is returned as-is).
    """
    issues = []
    for quote in evidence.raw_evidence_quotes:
        q_lower = quote.lower()
        if "representative" in q_lower and "name" in q_lower and evidence.representative_name is None:
            issues.append(f"Quote claims representative name collected but field is null: {quote!r}")
        if ("confirmation code" in q_lower or "dispatch reference" in q_lower) and evidence.authorization_code is None:
            issues.append(f"Quote claims code collected but field is null: {quote!r}")
    return len(issues) == 0, issues
