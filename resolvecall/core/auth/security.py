from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, Dict, Any

import jwt
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

from resolvecall.core.config import settings

# Initialize Argon2id password hasher with production-grade OWASP recommended settings
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19456,  # 19 MiB
    parallelism=1,
    hash_len=32,
    type=Type.ID,
)


def hash_password(password: str) -> str:
    """Hashes a password using Argon2id. Never logs or exposes the plaintext password."""
    if not password:
        raise ValueError("Password cannot be empty")
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifies a plaintext password against an Argon2id hash."""
    if not password or not password_hash:
        return False
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False
    except Exception:
        return False


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Enforces enterprise password complexity:
    - Minimum 8 characters
    - At least one letter
    - At least one number or special character
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{}|;':\",.<>?]", password):
        return False, "Password must contain at least one number or special character."
    return True, None


def create_session_jwt(
    user_id: str,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, str, datetime]:
    """
    Creates a signed JWT for backend session tracking.
    Claims strictly contain only identity/session metadata:
      sub, email, role, jti, iat, exp.
    Returns: (jwt_token_string, jti_id, expires_at_datetime)
    """
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expires_at = now + expires_delta
    else:
        expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims = {
        "sub": user_id,
        "email": email.strip().lower(),
        "role": role,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti, expires_at


def decode_session_jwt(token: str) -> Dict[str, Any]:
    """
    Decodes and validates the signature and expiration of a session JWT.
    Raises jwt.PyJWTError on failure.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "email", "role", "jti", "exp", "iat"]},
    )
