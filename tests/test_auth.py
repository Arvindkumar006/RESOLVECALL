from __future__ import annotations

import os
import tempfile
import uuid
import pytest
from starlette.testclient import TestClient

from resolvecall.core.config import settings
from resolvecall.core.storage.auth_db import AuthRepository
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
)
from resolvecall.web.app import app


@pytest.fixture
def temp_repo():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = AuthRepository(db_path=db_path)
    yield repo
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass


def test_argon2id_password_hashing():
    pwd = "EnterpriseSecurePassword123!"
    h = hash_password(pwd)
    assert h.startswith("$argon2id$")
    assert verify_password(pwd, h) is True
    assert verify_password("WrongPassword!", h) is False
    assert verify_password("", h) is False


def test_password_strength_validation():
    valid, err = validate_password_strength("short")
    assert not valid
    assert "8 characters" in err

    valid, err = validate_password_strength("alllowercaseletters")
    assert not valid
    assert "number or special character" in err

    valid, err = validate_password_strength("1234567890!")
    assert not valid
    assert "letter" in err

    valid, err = validate_password_strength("ValidPassword123!")
    assert valid
    assert err is None


def test_user_repository_crud(temp_repo):
    user = temp_repo.create_user(
        name="Lead Operator",
        email="LEAD@ENTERPRISE.CORP",
        password_hash=hash_password("Pass123!"),
        role="operator",
    )
    assert user.email == "lead@enterprise.corp"  # Normalized
    assert user.role == "admin"  # First user auto-assigned admin

    found = temp_repo.get_user_by_email("lead@enterprise.corp")
    assert found is not None
    assert found.id == user.id

    # Duplicate rejection
    with pytest.raises(Exception):
        temp_repo.create_user(
            name="Another User",
            email="lead@enterprise.corp",
            password_hash=hash_password("Pass123!"),
        )


def test_jwt_creation_and_session_revocation(temp_repo):
    user = temp_repo.create_user(name="User A", email="usera@corp.com", role="operator")
    token, jti, exp = create_session_jwt(user.id, user.email, user.role)
    
    # Check JWT claims
    claims = decode_session_jwt(token)
    assert claims["sub"] == user.id
    assert claims["email"] == "usera@corp.com"
    assert claims["role"] == user.role
    assert claims["jti"] == jti

    # Create session in DB
    session = temp_repo.create_session(user.id, jti, exp)
    assert session.is_valid is True

    # Revoke session
    revoked = temp_repo.revoke_session(jti)
    assert revoked is True

    # Check revoked session
    updated_session = temp_repo.get_session_by_jti(jti)
    assert updated_session.revoked_at is not None
    assert updated_session.is_valid is False


def test_oauth_state_generation_and_consumption(temp_repo):
    state = temp_repo.create_oauth_state("google", expires_in_seconds=600)
    assert state is not None
    assert len(state) > 16

    # First consumption succeeds
    assert temp_repo.validate_and_consume_oauth_state("google", state) is True

    # Replay attack: second consumption MUST fail
    assert temp_repo.validate_and_consume_oauth_state("google", state) is False

    # Invalid state fails
    assert temp_repo.validate_and_consume_oauth_state("google", "invalid-state-token") is False

    # Wrong provider fails
    another_state = temp_repo.create_oauth_state("github", expires_in_seconds=600)
    assert temp_repo.validate_and_consume_oauth_state("google", another_state) is False


def test_oauth_provider_detection():
    providers = get_configured_providers()
    assert "google" in providers
    assert "github" in providers
    assert "linkedin" in providers
    
    adapter = get_oauth_adapter("google")
    assert adapter is not None
    assert adapter.provider_name == "google"


def test_api_auth_flow():
    client = TestClient(app)
    
    # Check providers endpoint
    resp = client.get("/api/auth/providers")
    assert resp.status_code == 200
    assert "providers" in resp.json()

    # Register new user with unique email
    test_email = f"alex.{uuid.uuid4().hex[:8]}@freightcorp.io"
    reg_payload = {
        "name": "Alex Dispatch",
        "email": test_email,
        "password": "SecurePassword123!",
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["ok"] is True
    assert reg_data["user"]["email"] == test_email
    assert "password" not in reg_data["user"]
    assert "password_hash" not in reg_data["user"]

    # Verify session cookie was set
    assert settings.SESSION_COOKIE_NAME in client.cookies

    # Test /api/auth/me
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["email"] == test_email

    # Test /api/auth/logout
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["ok"] is True

    # Subsequent /api/auth/me should fail
    me_after_logout = client.get("/api/auth/me")
    assert me_after_logout.status_code == 401
