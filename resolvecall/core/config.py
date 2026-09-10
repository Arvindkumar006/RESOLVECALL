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
    
    # Telephony Security: Comma-separated authorized phone numbers or E.164 patterns
    # In production, phone calls are strictly verified against authorization policy.
    AUTHORIZED_PHONE_WHITELIST: str = os.getenv("AUTHORIZED_PHONE_WHITELIST", "*")
    DEFAULT_CALL_TIMEOUT_SECONDS: int = int(os.getenv("DEFAULT_CALL_TIMEOUT_SECONDS", "300"))
    
    # Path to calle CLI if not in standard PATH
    CALLE_CLI_PATH: str = os.getenv("CALLE_CLI_PATH", "calle")

    def is_phone_authorized(self, phone: str) -> bool:
        if not phone:
            return False
        # Clean phone
        cleaned = re.sub(r"[^\d+]", "", phone)
        if not (cleaned.startswith("+") and len(cleaned) >= 8):
            return False
            
        if self.AUTHORIZED_PHONE_WHITELIST.strip() == "*":
            return True
            
        allowed = [p.strip() for p in self.AUTHORIZED_PHONE_WHITELIST.split(",") if p.strip()]
        allowed_cleaned = [re.sub(r"[^\d+]", "", p) for p in allowed]
        return cleaned in allowed or phone in allowed or cleaned in allowed_cleaned


settings = Settings()


