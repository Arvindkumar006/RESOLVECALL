from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Optional, Tuple

from resolvecall.core.models import (
    Incident,
    PolicyDecision,
    PolicyEvaluationResult,
    StructuredEvidence,
)


class PolicyEngine:
    """Generic, deterministic policy evaluation engine.
    Calculates the exact mathematical relationship between the actual proposed time/window
    and the actual operational recovery deadline.
    """

    @classmethod
    def evaluate(cls, incident: Incident, evidence: StructuredEvidence) -> PolicyEvaluationResult:
        """Evaluates extracted evidence against the incident's constraints using deterministic temporal math."""
        # 1. Check if the recipient explicitly refused or failed to commit
        if evidence.resolution_status in ("REFUSED", "FAILED", "UNRESOLVED"):
            return PolicyEvaluationResult(
                decision=PolicyDecision.INVALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=evidence.agreed_window_end,
                reason=f"Recovery commitment was refused or could not be established: {evidence.notes or 'No agreement reached'}.",
            )

        # 2. Check if a time or window was extracted
        target_end_str = evidence.agreed_window_end or evidence.agreed_window_start
        if not target_end_str:
            return PolicyEvaluationResult(
                decision=PolicyDecision.AMBIGUOUS,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=None,
                reason="No concrete resolution or redelivery time could be extracted from conversation evidence.",
            )

        # 3. Calculate actual mathematical relationship between proposed time and deadline
        calc_result = cls._calculate_temporal_relationship(target_end_str, incident.recovery_deadline)

        if calc_result is None:
            return PolicyEvaluationResult(
                decision=PolicyDecision.AMBIGUOUS,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=target_end_str,
                reason=f"Could not parse temporal values to compare '{target_end_str}' against deadline '{incident.recovery_deadline}'.",
            )

        is_within_deadline, delta_minutes = calc_result

        if is_within_deadline:
            return PolicyEvaluationResult(
                decision=PolicyDecision.VALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=target_end_str,
                reason=f"Calculated completion '{target_end_str}' satisfies operational deadline '{incident.recovery_deadline}' (margin: +{delta_minutes:.1f} minutes).",
            )
        else:
            return PolicyEvaluationResult(
                decision=PolicyDecision.INVALID,
                deadline_evaluated=incident.recovery_deadline,
                proposed_window_end=target_end_str,
                reason=f"Calculated completion '{target_end_str}' violates operational deadline '{incident.recovery_deadline}' (exceeded by {abs(delta_minutes):.1f} minutes).",
            )

    @classmethod
    def _calculate_temporal_relationship(
        cls, proposed_str: str, deadline_str: str
    ) -> Optional[Tuple[bool, float]]:
        """Mathematically calculates: (deadline_timestamp - proposed_timestamp).
        Returns (is_valid, delta_minutes) where delta_minutes >= 0 means within deadline.
        """
        base_today = date.today()

        # Parse deadline into canonical datetime
        dt_deadline = cls._parse_to_datetime(deadline_str, base_date=base_today)
        if not dt_deadline:
            return None

        # Determine if proposed specifies an offset (e.g. tomorrow)
        prop_base_date = base_today
        if re.search(r"\btomorrow\b", proposed_str, re.IGNORECASE):
            prop_base_date = base_today + timedelta(days=1)
        elif re.search(r"\bin\s+(\d+)\s+days?\b", proposed_str, re.IGNORECASE):
            m = re.search(r"\bin\s+(\d+)\s+days?\b", proposed_str, re.IGNORECASE)
            days = int(m.group(1))
            prop_base_date = base_today + timedelta(days=days)

        dt_proposed = cls._parse_to_datetime(proposed_str, base_date=prop_base_date)
        if not dt_proposed:
            # If date offset was recognized (like tomorrow) without specific hour, assume morning (09:00)
            if prop_base_date > base_today:
                dt_proposed = datetime.combine(prop_base_date, time(9, 0))
            else:
                return None

        # Mathematical delta in minutes
        delta_seconds = (dt_deadline - dt_proposed).total_seconds()
        delta_minutes = delta_seconds / 60.0
        is_valid = delta_minutes >= 0.0

        return is_valid, delta_minutes

    @classmethod
    def _parse_to_datetime(cls, text: str, base_date: date) -> Optional[datetime]:
        """Parses ISO string, 24-hour time, or 12-hour AM/PM string into datetime."""
        if not text:
            return None
        t_str = text.strip()

        # 1. Direct ISO datetime
        try:
            return datetime.fromisoformat(t_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            pass

        # 2. 12-hour or 24-hour time format: HH:MM[:SS] [am/pm]
        match_time = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm)?", t_str, re.IGNORECASE)
        if match_time:
            hr = int(match_time.group(1))
            mn = int(match_time.group(2))
            ampm = match_time.group(4)
            if ampm:
                ampm = ampm.lower()
                if ampm == "pm" and hr < 12:
                    hr += 12
                elif ampm == "am" and hr == 12:
                    hr = 0
            if 0 <= hr <= 23 and 0 <= mn <= 59:
                return datetime.combine(base_date, time(hr, mn))

        # 3. Simple hour with AM/PM (e.g. "2 PM", "11am")
        match_hr = re.search(r"\b(\d{1,2})\s*(am|pm)\b", t_str, re.IGNORECASE)
        if match_hr:
            hr = int(match_hr.group(1))
            ampm = match_hr.group(2).lower()
            if ampm == "pm" and hr < 12:
                hr += 12
            elif ampm == "am" and hr == 12:
                hr = 0
            if 0 <= hr <= 23:
                return datetime.combine(base_date, time(hr, 0))

        return None
