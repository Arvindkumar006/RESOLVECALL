import os
import re
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "ResolveCall"
    APP_ENV: str = os.getenv("APP_ENV", "production")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # API Authentication
    # Operational /api/* endpoints require this key.
    # If unset or empty the server starts but all protected endpoints
    # return HTTP 401 — authentication is NEVER silently disabled.
    RESOLVECALL_API_KEY: str = os.getenv("RESOLVECALL_API_KEY", "")

    # Telephony Security: Comma-separated authorized E.164 phone numbers.
    # Wildcard "*" is explicitly rejected — every destination must be named.
    # Default is empty (no destinations authorized until explicitly configured).
    AUTHORIZED_PHONE_WHITELIST: str = os.getenv("AUTHORIZED_PHONE_WHITELIST", "")
    DEFAULT_CALL_TIMEOUT_SECONDS: int = int(os.getenv("DEFAULT_CALL_TIMEOUT_SECONDS", "300"))

    # Path to calle CLI if not in standard PATH
    CALLE_CLI_PATH: str = os.getenv("CALLE_CLI_PATH", "calle")

    def is_phone_authorized(self, phone: str) -> bool:
        """Return True only if the phone number is explicitly listed in the whitelist.

        Wildcard (*), empty list, and malformed numbers are all rejected.
        """
        if not phone:
            return False

        # Reject wildcard — never allow unrestricted dialing
        if self.AUTHORIZED_PHONE_WHITELIST.strip() == "*":
            return False

        # Reject empty whitelist
        allowed_raw = [p.strip() for p in self.AUTHORIZED_PHONE_WHITELIST.split(",") if p.strip()]
        if not allowed_raw:
            return False

        # Validate and clean the supplied phone number (must be E.164)
        cleaned = re.sub(r"[^\d+]", "", phone)
        if not (cleaned.startswith("+") and len(cleaned) >= 8):
            return False

        # Validate and clean each whitelist entry
        allowed_cleaned = []
        for p in allowed_raw:
            c = re.sub(r"[^\d+]", "", p)
            if c.startswith("+") and len(c) >= 8:
                allowed_cleaned.append(c)

        return cleaned in allowed_cleaned


settings = Settings()
