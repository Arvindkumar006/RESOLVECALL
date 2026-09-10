from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field

from resolvecall.core.config import settings
from resolvecall.core.storage.auth_db import AuthRepository, UserRecord, get_auth_repo
from resolvecall.core.auth.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_session_jwt,
    decode_session_jwt,
)
from resolvecall.core.auth.oauth import (
    get_oauth_adapter,
    is_provider_configured,
    get_configured_providers,
    OAuthError,
)

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic Schemas
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SafeUserResponse(BaseModel):
    id: str
    email: str
    name: str
    provider: str
    role: str
    is_active: bool
    created_at: str


# Session extraction & dependency injection
async def get_current_user(
    request: Request,
    repo: AuthRepository = Depends(get_auth_repo),
) -> UserRecord:
    """
    Extracts the authenticated session.
    Prioritizes HttpOnly session cookie (browser frontend),
    with fallback to Authorization: Bearer header (for API test clients).
    """
    token: Optional[str] = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHENTICATED",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_session_jwt(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SESSION_EXPIRED",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_SESSION",
        )

    session = repo.get_session_by_jti(jti)
    if not session or not session.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SESSION_REVOKED",
        )

    user = repo.get_user_by_id(session.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="USER_INACTIVE",
        )

    # Touch session last_seen
    repo.touch_session(jti)
    # Attach current jti to request state for logout
    request.state.jti = jti
    return user


def require_role(allowed_roles: List[str]):
    async def role_checker(user: UserRecord = Depends(get_current_user)) -> UserRecord:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="INSUFFICIENT_PERMISSION",
            )
        return user
    return role_checker


require_recovery_permission = require_role(["admin", "operator"])


# Helper for setting secure cookie
def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAME_SITE,
        path="/",
    )


# API Endpoints
@auth_router.post("/register")
async def register(
    payload: RegisterRequest,
    response: Response,
    request: Request,
    repo: AuthRepository = Depends(get_auth_repo),
):
    """Registers a real local user with Argon2id password hashing and persistent SQLite storage."""
    # Validate password complexity
    valid_pw, pw_err = validate_password_strength(payload.password)
    if not valid_pw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pw_err)

    normalized_email = payload.email.strip().lower()
    existing = repo.get_user_by_email(normalized_email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ACCOUNT_ALREADY_EXISTS")

    # Hash with Argon2id
    pw_hash = hash_password(payload.password)
    user = repo.create_user(
        name=payload.name,
        email=normalized_email,
        password_hash=pw_hash,
        provider="local",
        role="operator",
    )

    # Establish session
    token, jti, exp = create_session_jwt(user.id, user.email, user.role)
    user_agent = request.headers.get("User-Agent")
    ip_addr = request.client.host if request.client else None
    repo.create_session(user.id, jti, exp, user_agent=user_agent, ip_address=ip_addr)

    # Set secure HttpOnly cookie (no JWT sent in body to browser)
    _set_auth_cookie(response, token)

    # Record audit event if orchestrator is available
    _record_audit(request, "USER_REGISTERED", f"User {user.email} registered locally.")

    return {"ok": True, "user": user.to_safe_dict()}


@auth_router.post("/login")
async def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    repo: AuthRepository = Depends(get_auth_repo),
):
    """Authenticates credentials against Argon2id hash and establishes an HttpOnly session."""
    normalized_email = payload.email.strip().lower()
    user = repo.get_user_by_email(normalized_email)

    if not user or not user.is_active or not user.password_hash or not verify_password(payload.password, user.password_hash):
        _record_audit(request, "AUTHENTICATION_FAILED", f"Failed login attempt for {normalized_email}.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CREDENTIALS")

    # Establish session
    token, jti, exp = create_session_jwt(user.id, user.email, user.role)
    user_agent = request.headers.get("User-Agent")
    ip_addr = request.client.host if request.client else None
    repo.create_session(user.id, jti, exp, user_agent=user_agent, ip_address=ip_addr)

    # Set secure HttpOnly cookie
    _set_auth_cookie(response, token)

    _record_audit(request, "USER_LOGIN", f"User {user.email} logged in successfully.")

    return {"ok": True, "user": user.to_safe_dict()}


@auth_router.get("/me")
async def get_me(user: UserRecord = Depends(get_current_user)):
    """Returns the authenticated operator profile."""
    return {"ok": True, "user": user.to_safe_dict()}


@auth_router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: UserRecord = Depends(get_current_user),
    repo: AuthRepository = Depends(get_auth_repo),
):
    """Server-side session revocation: marks session as revoked in SQLite and clears cookie."""
    jti = getattr(request.state, "jti", None)
    if jti:
        repo.revoke_session(jti)

    # Clear HttpOnly cookie
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAME_SITE,
    )

    _record_audit(request, "USER_LOGOUT", f"User {user.email} logged out; session {jti} revoked.")
    return {"ok": True, "message": "Successfully logged out."}


@auth_router.get("/providers")
async def get_providers():
    """Returns configuration status of OAuth providers."""
    return {"ok": True, "providers": get_configured_providers()}


@auth_router.get("/oauth/{provider}/authorize")
async def oauth_authorize(
    provider: str,
    request: Request,
    repo: AuthRepository = Depends(get_auth_repo),
):
    """Generates cryptographic state token and redirects to the provider's OAuth authorization endpoint."""
    adapter = get_oauth_adapter(provider)
    if not adapter:
        raise HTTPException(status_code=400, detail="UNKNOWN_PROVIDER")

    if not adapter.is_configured():
        raise HTTPException(
            status_code=400,
            detail="OAUTH_CONFIGURATION_MISSING",
        )

    # Generate cryptographically secure state with 10-minute expiry
    state = repo.create_oauth_state(provider.lower(), expires_in_seconds=600)
    redirect_uri = f"{settings.APP_BASE_URL.rstrip('/')}/api/auth/oauth/{provider.lower()}/callback"
    auth_url = adapter.get_authorization_url(state, redirect_uri)

    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@auth_router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    repo: AuthRepository = Depends(get_auth_repo),
):
    """
    Validates state, exchanges authorization code for verified identity,
    creates/links user in SQLite, establishes HttpOnly session,
    and redirects directly to /console (strictly zero tokens in URLs).
    """
    login_err_redirect = lambda err_code: RedirectResponse(
        url=f"{settings.APP_BASE_URL.rstrip('/')}/login?error={urllib.parse.quote(err_code)}",
        status_code=status.HTTP_302_FOUND,
    )

    if error:
        return login_err_redirect("OAUTH_PROVIDER_ERROR")

    if not code or not state:
        return login_err_redirect("OAUTH_INVALID_CALLBACK")

    adapter = get_oauth_adapter(provider)
    if not adapter:
        return login_err_redirect("UNKNOWN_PROVIDER")

    # 1. Strictly validate and consume the cryptographic state (anti-CSRF & replay protection)
    if not repo.validate_and_consume_oauth_state(provider.lower(), state):
        _record_audit(request, "AUTHENTICATION_FAILED", f"OAuth state mismatch or replay attempt for {provider}.")
        return login_err_redirect("OAUTH_STATE_INVALID")

    # 2. Exchange authorization code with provider
    redirect_uri = f"{settings.APP_BASE_URL.rstrip('/')}/api/auth/oauth/{provider.lower()}/callback"
    try:
        identity = await adapter.exchange_code(code, redirect_uri)
    except OAuthError as oe:
        _record_audit(request, "AUTHENTICATION_FAILED", f"OAuth exchange error with {provider}: {oe.code}")
        return login_err_redirect(oe.code)
    except Exception as e:
        _record_audit(request, "AUTHENTICATION_FAILED", f"Unexpected OAuth error with {provider}: {str(e)}")
        return login_err_redirect("OAUTH_PROVIDER_ERROR")

    # 3. Account resolution & linking
    # Check if this exact OAuth identity already exists
    user = repo.get_user_by_oauth(provider.lower(), identity.provider_subject)
    if not user:
        # Check if email exists
        existing_user = repo.get_user_by_email(identity.email)
        if existing_user:
            if identity.email_verified:
                # Link OAuth provider to existing verified email account
                with repo._get_connection() as conn:
                    conn.execute(
                        "UPDATE users SET provider = ?, provider_subject = ?, updated_at = ? WHERE id = ?",
                        (provider.lower(), identity.provider_subject, datetime.now(timezone.utc).isoformat(), existing_user.id),
                    )
                    conn.commit()
                user = repo.get_user_by_id(existing_user.id)
            else:
                return login_err_redirect("OAUTH_UNVERIFIED_EMAIL")
        else:
            # Create new user
            user = repo.create_user(
                name=identity.name,
                email=identity.email,
                provider=provider.lower(),
                provider_subject=identity.provider_subject,
                role="operator",
            )

    if not user or not user.is_active:
        return login_err_redirect("USER_INACTIVE")

    # 4. Establish session
    token, jti, exp = create_session_jwt(user.id, user.email, user.role)
    user_agent = request.headers.get("User-Agent")
    ip_addr = request.client.host if request.client else None
    repo.create_session(user.id, jti, exp, user_agent=user_agent, ip_address=ip_addr)

    _record_audit(request, "OAUTH_LOGIN", f"User {user.email} authenticated via {provider}.")

    # 5. Redirect directly to /console with HttpOnly cookie (strictly NO JWT in URL query or hash)
    target_url = f"{settings.APP_BASE_URL.rstrip('/')}/console"
    redirect_res = RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
    _set_auth_cookie(redirect_res, token)
    return redirect_res


def _record_audit(request: Request, event_type: str, description: str):
    """Helper to safely record audit events into orchestrator if available on app state."""
    try:
        orch = getattr(request.app.state, "orchestrator", None)
        if orch and hasattr(orch, "record_auth_audit_event"):
            orch.record_auth_audit_event(event_type, description)
    except Exception:
        pass
