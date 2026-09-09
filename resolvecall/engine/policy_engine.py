from __future__ import annotations

import re
from datetime import datetime, time, timedelta
from typing import Any, Dict, Optional, Tuple

from resolvecall.core.models import (
    Incident,
    PolicyDecision,
    PolicyEvaluationResult,
    StructuredEvidence,
)


class PolicyEngine:
    """Generic, deterministic policy evaluation engine.
    Calculates whether an actual negotiated recovery proposal meets the incident's operational constraints.
    """

    @classmethod
    def evaluate(cls, incident: Incident, evidence: StructuredEvidence) -> PolicyEvaluationResult:
        """Evaluates extracted evidence against the incident's constraints."""
        # 1. Check if the recipient refused or couldn't commit
        if evidence.resolution_status in ("REFUSED", "FAILED", "UNRESOLVED"):
            return PolicyEvaluationResult(
                decision=PolicyDecision.INVALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=evidence.agreed_window_end,
                reason=f"Recovery commitment was refused or could not be established: {evidence.notes or 'No agreement reached'}.",
            )

        # 2. Check if the window is completely missing
        if not evidence.agreed_window_end and not evidence.agreed_window_start:
            return PolicyEvaluationResult(
                decision=PolicyDecision.AMBIGUOUS,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=None,
                reason="No concrete redelivery or resolution window could be verified from conversation evidence.",
            )

        # 3. Check for explicit next-day or multi-day postponements
        notes_and_quotes = f"{evidence.notes or ''} {' '.join(evidence.raw_evidence_quotes)}".lower()
        if any(term in notes_and_quotes for term in ["tomorrow", "next day", "in 2 days", "next week", "later this week"]):
            # If incident recovery deadline is today, this violates policy
            return PolicyEvaluationResult(
                decision=PolicyDecision.INVALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=evidence.agreed_window_end or "tomorrow",
                reason=f"Recipient offered postponement ('tomorrow' / multi-day) which violates the required deadline ({incident.recovery_deadline}).",
            )

        # 4. Compare proposed time against deadline
        target_end_str = evidence.agreed_window_end or evidence.agreed_window_start
        comparison_res = cls._compare_times(target_end_str, incident.recovery_deadline)

        if comparison_res is None:
            return PolicyEvaluationResult(
                decision=PolicyDecision.AMBIGUOUS,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=target_end_str,
                reason=f"Could not deterministically parse or compare proposed time '{target_end_str}' against deadline '{incident.recovery_deadline}'.",
            )

        is_within_deadline, delta_minutes = comparison_res
        if is_within_deadline:
            reason = (
                f"Proposed completion '{target_end_str}' is within the operational deadline "
                f"'{incident.recovery_deadline}' (margin: {delta_minutes} min)."
            )
            # Check if reference/authorization was also required and obtained
            if not evidence.representative_name and not evidence.authorization_code:
                reason += " Note: Proceeding without explicit dispatcher confirmation ID."
            return PolicyEvaluationResult(
                decision=PolicyDecision.VALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=target_end_str,
                reason=reason,
            )
        else:
            return PolicyEvaluationResult(
                decision=PolicyDecision.INVALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=target_end_str,
                reason=(
                    f"Proposed completion '{target_end_str}' exceeds the required operational deadline "
                    f"'{incident.recovery_deadline}' by {-delta_minutes} min."
                ),
            )

    @classmethod
    def _parse_time_spec(cls, text: str) -> Optional[time]:
        """Parses arbitrary 24h, 12h, or ISO string to standard datetime.time."""
        if not text:
            return None
        t_str = text.strip()

        # Check ISO datetime
        try:
            dt = datetime.fromisoformat(t_str.replace("Z", "+00:00"))
            return dt.time()
        except Exception:
            pass

        # Match 12-hour time like 11:30 AM, 1:15pm, 10:45 am
        match_12 = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm)?", t_str, re.IGNORECASE)
        if match_12:
            hr = int(match_12.group(1))
            mn = int(match_12.group(2))
            ampm = match_12.group(4)
            if ampm:
                ampm = ampm.lower()
                if ampm == "pm" and hr < 12:
                    hr += 12
                elif ampm == "am" and hr == 12:
                    hr = 0
            if 0 <= hr <= 23 and 0 <= mn <= 59:
                return time(hour=hr, minute=mn)

        # Match hour only with am/pm (e.g. 2 PM)
        match_hr_ampm = re.search(r"\b(\d{1,2})\s*(am|pm)\b", t_str, re.IGNORECASE)
        if match_hr_ampm:
            hr = int(match_hr_ampm.group(1))
            ampm = match_hr_ampm.group(2).lower()
            if ampm == "pm" and hr < 12:
                hr += 12
            elif ampm == "am" and hr == 12:
                hr = 0
            if 0 <= hr <= 23:
                return time(hour=hr, minute=0)

        return None

    @classmethod
    def _compare_times(cls, proposed_str: str, deadline_str: str) -> Optional[Tuple[bool, int]]:
        """Returns (is_within_deadline, delta_minutes) or None if unparseable.
        delta_minutes is positive if proposed is earlier than or equal to deadline.
        """
        prop_t = cls._parse_time_spec(proposed_str)
        dead_t = cls._parse_time_spec(deadline_str)

        if not prop_t or not dead_t:
            return None

        # Calculate minute difference on same day
        prop_mins = prop_t.hour * 60 + prop_t.minute
        dead_mins = dead_t.hour * 60 + dead_t.minute

        delta = dead_mins - prop_mins
        is_valid = delta >= 0
        return is_valid, delta
