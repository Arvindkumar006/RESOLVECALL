"""
Shared utility helpers for ResolveCall.

These helpers are used across modules to ensure consistent,
safe handling of sensitive data in logs and audit events.
"""
from __future__ import annotations

import re


def mask_phone(phone_number: str) -> str:
    """Mask a phone number for safe logging and audit output.

    Keeps the country code prefix and the final two digits; masks
    all digits in between with bullet characters.

    Examples:
        +18005550100  ->  +1••••••••00
        +4412345678   ->  +44•••••••78
        <E.164-number>  ->  +CC••••••XX  (CC=country-code, XX=last-2-digits)
        not-a-phone   ->  [REDACTED]
    """
    if not phone_number or not isinstance(phone_number, str):
        return "[REDACTED]"

    cleaned = phone_number.strip()

    # Must be an E.164-style number: + followed by digits
    if not re.match(r"^\+\d{7,15}$", cleaned):
        return "[REDACTED]"

    # Determine country code length (1–3 digits after +)
    # Heuristic: country codes are 1–3 digits.  Keep them + last 2 digits.
    digits_after_plus = cleaned[1:]  # all digits

    if len(digits_after_plus) <= 4:
        # Too short to meaningfully mask — redact entirely
        return "[REDACTED]"

    # Keep country-code prefix (1 char = '+' itself, we keep at minimum 1 digit)
    # Simple approach: keep '+' + first 2 chars (handles +1, +44, +91 etc.)
    # and always keep last 2 digits.
    keep_prefix = 2  # digits to keep at start (after +)
    keep_suffix = 2  # digits to keep at end

    if len(digits_after_plus) <= keep_prefix + keep_suffix:
        # Edge: number is very short — keep prefix only
        return "+" + digits_after_plus[:keep_prefix] + "•" * (len(digits_after_plus) - keep_prefix)

    masked_middle = "•" * (len(digits_after_plus) - keep_prefix - keep_suffix)
    result = "+" + digits_after_plus[:keep_prefix] + masked_middle + digits_after_plus[-keep_suffix:]
    return result
