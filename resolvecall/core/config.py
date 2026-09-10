import os
import re
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "ResolveCall"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    
    # Telephony Security: Comma-separated authorized phone numbers or E.164 patterns
    # In production, phone calls are strictly verified against authorization policy.
    AUTHORIZED_PHONE_WHITELIST: str = os.getenv("AUTHORIZED_PHONE_WHITELIST", "*")
    DEFAULT_CALL_TIMEOUT_SECONDS: int = int(os.getenv("DEFAULT_CALL_TIMEOUT_SECONDS", "300"))
    
    # Path to calle CLI if not in standard PATH
    CALLE_CLI_PATH: str = os.getenv("CALLE_CLI_PATH", "calle")

    # Persistent Auth Storage
    AUTH_DB_PATH: str = os.getenv("AUTH_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resolvecall_auth.db"))

    # JWT & Session Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev_secret_key_change_in_prod_resolvecall_sec_key_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Secure Session Cookie
    SESSION_COOKIE_NAME: str = "resolvecall_session"
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
    COOKIE_SAME_SITE: str = "lax"
    
    # OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")
    
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")

    def validate_security(self):
        if self.APP_ENV == "production" and (not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY.startswith("dev_secret_key")):
            raise RuntimeError("CRITICAL SECURITY ERROR: JWT_SECRET_KEY must be securely configured in environment for production.")

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


