from __future__ import annotations

import os
import sqlite3
import uuid
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from resolvecall.core.config import settings


@dataclass
class UserRecord:
    id: str
    email: str
    name: str
    password_hash: Optional[str]
    provider: str
    provider_subject: Optional[str]
    role: str
    is_active: bool
    created_at: str
    updated_at: str

    def to_safe_dict(self) -> Dict[str, Any]:
        """Returns safe user data, strictly omitting password_hash or provider secrets."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "provider": self.provider,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }


@dataclass
class SessionRecord:
    id: str
    user_id: str
    token_id: str  # jti
    created_at: str
    expires_at: str
    revoked_at: Optional[str]
    last_seen_at: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        if self.revoked_at is not None:
            return False
        try:
            exp = datetime.fromisoformat(self.expires_at)
            now = datetime.now(timezone.utc)
            # Ensure exp is timezone-aware
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            return now < exp
        except Exception:
            return False


class AuthRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.AUTH_DB_PATH
        # Ensure parent directory exists
        parent = os.path.dirname(self.db_path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT,
                    provider TEXT NOT NULL DEFAULT 'local',
                    provider_subject TEXT,
                    role TEXT NOT NULL DEFAULT 'operator',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_provider_subject ON users(provider, provider_subject) WHERE provider_subject IS NOT NULL")

            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    token_id TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT,
                    last_seen_at TEXT NOT NULL,
                    user_agent TEXT,
                    ip_address TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token_id ON sessions(token_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")

            # OAuth state table (CSRF defense)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS oauth_states (
                    state TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    consumed_at TEXT
                )
            """)
            conn.commit()

    # User Methods
    def create_user(
        self,
        name: str,
        email: str,
        password_hash: Optional[str] = None,
        provider: str = "local",
        provider_subject: Optional[str] = None,
        role: str = "operator",
    ) -> UserRecord:
        normalized_email = email.strip().lower()
        now = datetime.now(timezone.utc).isoformat()
        user_id = str(uuid.uuid4())

        # If this is the very first user in the database, promote to admin
        if self.count_users() == 0:
            role = "admin"

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (id, email, name, password_hash, provider, provider_subject, role, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (user_id, normalized_email, name.strip(), password_hash, provider, provider_subject, role, now, now),
            )
            conn.commit()

        return self.get_user_by_id(user_id)  # type: ignore

    def count_users(self) -> int:
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
            return row["cnt"] if row else 0

    def get_user_by_id(self, user_id: str) -> Optional[UserRecord]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def get_user_by_email(self, email: str) -> Optional[UserRecord]:
        normalized_email = email.strip().lower()
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (normalized_email,)).fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def get_user_by_oauth(self, provider: str, provider_subject: str) -> Optional[UserRecord]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE provider = ? AND provider_subject = ?",
                (provider, provider_subject),
            ).fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def update_user_password(self, user_id: str, new_password_hash: str):
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (new_password_hash, now, user_id),
            )
            conn.commit()

    # Session Methods
    def create_session(
        self,
        user_id: str,
        token_id: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> SessionRecord:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        exp_iso = expires_at.isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, user_id, token_id, created_at, expires_at, revoked_at, last_seen_at, user_agent, ip_address)
                VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?)
                """,
                (session_id, user_id, token_id, now, exp_iso, now, user_agent, ip_address),
            )
            conn.commit()

        return self.get_session_by_jti(token_id)  # type: ignore

    def get_session_by_jti(self, token_id: str) -> Optional[SessionRecord]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE token_id = ?", (token_id,)).fetchone()
            if not row:
                return None
            return self._row_to_session(row)

    def touch_session(self, token_id: str):
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute("UPDATE sessions SET last_seen_at = ? WHERE token_id = ?", (now, token_id))
            conn.commit()

    def revoke_session(self, token_id: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE sessions SET revoked_at = ? WHERE token_id = ? AND revoked_at IS NULL",
                (now, token_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def revoke_all_user_sessions(self, user_id: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL",
                (now, user_id),
            )
            conn.commit()
            return cursor.rowcount

    # OAuth State Management (CSRF Defense)
    def create_oauth_state(self, provider: str, expires_in_seconds: int = 600) -> str:
        state = secrets.token_urlsafe(32)
        now_dt = datetime.now(timezone.utc)
        exp_dt = now_dt + timedelta(seconds=expires_in_seconds)

        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO oauth_states (state, provider, created_at, expires_at, consumed_at) VALUES (?, ?, ?, ?, NULL)",
                (state, provider, now_dt.isoformat(), exp_dt.isoformat()),
            )
            conn.commit()
        return state

    def validate_and_consume_oauth_state(self, provider: str, state: str) -> bool:
        if not state or not provider:
            return False
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()

        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM oauth_states WHERE state = ? AND provider = ?",
                (state, provider),
            ).fetchone()

            if not row:
                return False

            # Check if consumed already
            if row["consumed_at"] is not None:
                return False

            # Check if expired
            try:
                exp = datetime.fromisoformat(row["expires_at"])
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if now_dt > exp:
                    return False
            except Exception:
                return False

            # Mark state as consumed immediately (one-time use)
            conn.execute("UPDATE oauth_states SET consumed_at = ? WHERE state = ?", (now_iso, state))
            conn.commit()
            return True

    # Helpers
    def _row_to_user(self, row: sqlite3.Row) -> UserRecord:
        return UserRecord(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            password_hash=row["password_hash"],
            provider=row["provider"],
            provider_subject=row["provider_subject"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_session(self, row: sqlite3.Row) -> SessionRecord:
        return SessionRecord(
            id=row["id"],
            user_id=row["user_id"],
            token_id=row["token_id"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            revoked_at=row["revoked_at"],
            last_seen_at=row["last_seen_at"],
            user_agent=row["user_agent"],
            ip_address=row["ip_address"],
        )


_repo_instance: Optional[AuthRepository] = None


def get_auth_repo() -> AuthRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = AuthRepository()
    return _repo_instance
