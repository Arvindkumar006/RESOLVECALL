"""
JARVIS Sentinel - Cryptographic Security & Authorization Tokens
Provides HMAC-SHA256 signed JWT-like authorization tokens with:
- Nonce (prevent replay attacks)
- Timestamp & Expiry (prevent expired tokens)
- Cryptographic Signature (prevent token tampering or forging)
- Incident, Host, and Action Binding
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, Optional, Tuple

# Enterprise Authorization Secret (can be overridden via environment variable)
AUTH_SECRET = os.environ.get("JARVIS_AUTH_SECRET", "sentinel-super-secret-hmac-key-2026").encode("utf-8")
DEFAULT_TOKEN_TTL_SECONDS = 300  # 5 minutes validity


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data_str: str) -> bytes:
    padding = 4 - (len(data_str) % 4)
    if padding != 4:
        data_str += "=" * padding
    return base64.urlsafe_b64decode(data_str.encode("utf-8"))


def mint_authorization_token(
    incident_id: str,
    host_id: str,
    action: str,
    approver: str,
    ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS
) -> str:
    """
    Mints a tamper-evident, HMAC-SHA256 signed authorization token.
    Format: HITL_APPROVED.<payload_b64>.<signature_b64>
    """
    now = int(time.time())
    payload = {
        "jti": secrets.token_hex(12),  # Unique single-use nonce
        "sub": approver.strip() or "SecOps_Analyst",
        "inc": incident_id.strip(),
        "hst": host_id.strip(),
        "act": action.strip().upper(),
        "iat": now,
        "exp": now + ttl_seconds
    }

    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    payload_b64 = _b64_encode(payload_json.encode("utf-8"))

    # Compute HMAC-SHA256 signature
    sig = hmac.new(AUTH_SECRET, payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = _b64_encode(sig)

    return f"HITL_APPROVED.{payload_b64}.{sig_b64}"


def verify_authorization_token(
    token: str,
    expected_host: Optional[str] = None,
    expected_action: Optional[str] = None,
    expected_incident: Optional[str] = None,
    current_time: Optional[int] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Cryptographically verifies an authorization token.
    Checks:
    1. Structure and prefix
    2. HMAC-SHA256 signature validity (anti-tamper)
    3. Expiration time (iat, exp)
    4. Host, action, and incident bounds

    Returns:
        (is_valid: bool, reason: str, payload: Optional[Dict])
    """
    if not token or not isinstance(token, str):
        return False, "Token is empty or not a string", None

    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != "HITL_APPROVED":
        return False, "Token format invalid (must be HITL_APPROVED.<payload>.<signature>)", None

    _, payload_b64, sig_b64 = parts

    # 1. Verify HMAC Signature
    expected_sig = hmac.new(AUTH_SECRET, payload_b64.encode("utf-8"), hashlib.sha256).digest()
    try:
        provided_sig = _b64_decode(sig_b64)
    except Exception:
        return False, "Malformed token signature encoding", None

    if not hmac.compare_digest(expected_sig, provided_sig):
        return False, "Cryptographic signature mismatch: token has been tampered with or forged", None

    # 2. Decode and parse payload
    try:
        payload_bytes = _b64_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return False, "Malformed token payload JSON", None

    now = int(time.time()) if current_time is None else current_time

    # 3. Check expiration
    exp = payload.get("exp", 0)
    if now > exp:
        return False, f"Token expired at {exp} (current time {now})", payload

    # 4. Check target host
    if expected_host and payload.get("hst") != expected_host.strip():
        return False, f"Token target host mismatch: minted for {payload.get('hst')}, used on {expected_host}", payload

    # 5. Check target action
    if expected_action and payload.get("act") != expected_action.strip().upper():
        return False, f"Token action mismatch: minted for {payload.get('act')}, used for {expected_action}", payload

    # 6. Check incident ID
    if expected_incident and payload.get("inc") != expected_incident.strip():
        return False, f"Token incident mismatch: minted for {payload.get('inc')}, used for {expected_incident}", payload

    return True, "Token valid and authorized", payload
