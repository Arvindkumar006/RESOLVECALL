from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import httpx

from resolvecall.core.config import settings


@dataclass
class OAuthIdentity:
    provider: str
    provider_subject: str
    email: str
    email_verified: bool
    name: str
    avatar: Optional[str] = None


class OAuthError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class BaseOAuthAdapter:
    provider_name: str = ""
    auth_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    scopes: List[str] = []

    def get_client_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError

    def is_configured(self) -> bool:
        client_id, client_secret = self.get_client_credentials()
        return bool(client_id and client_secret and len(client_id.strip()) > 0 and len(client_secret.strip()) > 0)

    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        client_id, _ = self.get_client_credentials()
        if not client_id:
            raise OAuthError("OAUTH_CONFIGURATION_MISSING", f"{self.provider_name} OAuth credentials are not configured.")

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthIdentity:
        raise NotImplementedError


class GoogleOAuthAdapter(BaseOAuthAdapter):
    provider_name = "google"
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    scopes = ["openid", "email", "profile"]

    def get_client_credentials(self):
        return settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET

    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        client_id, _ = self.get_client_credentials()
        if not client_id:
            raise OAuthError("OAUTH_CONFIGURATION_MISSING", "Google OAuth credentials are not configured.")
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthIdentity:
        client_id, client_secret = self.get_client_credentials()
        if not client_id or not client_secret:
            raise OAuthError("OAUTH_CONFIGURATION_MISSING", "Google OAuth is not configured.")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                token_resp = await client.post(
                    self.token_url,
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Accept": "application/json"},
                )
            except Exception as e:
                raise OAuthError("OAUTH_NETWORK_ERROR", f"Failed to connect to Google token endpoint: {e}")

            if token_resp.status_code != 200:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Failed to exchange authorization code with Google.")

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Google did not return an access token.")

            try:
                user_resp = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except Exception as e:
                raise OAuthError("OAUTH_NETWORK_ERROR", f"Failed to fetch Google profile: {e}")

            if user_resp.status_code != 200:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Failed to retrieve Google user profile.")

            info = user_resp.json()
            email = info.get("email")
            if not email:
                raise OAuthError("OAUTH_MISSING_EMAIL", "Google account did not provide an email address.")

            return OAuthIdentity(
                provider="google",
                provider_subject=str(info.get("sub")),
                email=email.strip().lower(),
                email_verified=bool(info.get("email_verified", False)),
                name=info.get("name") or email.split("@")[0],
                avatar=info.get("picture"),
            )


class GitHubOAuthAdapter(BaseOAuthAdapter):
    provider_name = "github"
    auth_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    userinfo_url = "https://api.github.com/user"
    emails_url = "https://api.github.com/user/emails"
    scopes = ["read:user", "user:email"]

    def get_client_credentials(self):
        return settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthIdentity:
        client_id, client_secret = self.get_client_credentials()
        if not client_id or not client_secret:
            raise OAuthError("OAUTH_CONFIGURATION_MISSING", "GitHub OAuth is not configured.")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                token_resp = await client.post(
                    self.token_url,
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                )
            except Exception as e:
                raise OAuthError("OAUTH_NETWORK_ERROR", f"Failed to connect to GitHub token endpoint: {e}")

            if token_resp.status_code != 200:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Failed to exchange authorization code with GitHub.")

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "GitHub did not return an access token.")

            try:
                user_resp = await client.get(
                    self.userinfo_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )
            except Exception as e:
                raise OAuthError("OAUTH_NETWORK_ERROR", f"Failed to fetch GitHub profile: {e}")

            if user_resp.status_code != 200:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Failed to retrieve GitHub user profile.")

            info = user_resp.json()
            email = info.get("email")
            email_verified = False

            # If email is private on GitHub profile, fetch from /user/emails
            if not email:
                try:
                    email_resp = await client.get(
                        self.emails_url,
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github.v3+json",
                        },
                    )
                    if email_resp.status_code == 200:
                        emails = email_resp.json()
                        primary_email = next((e for e in emails if e.get("primary")), None)
                        if primary_email:
                            email = primary_email.get("email")
                            email_verified = bool(primary_email.get("verified"))
                        elif emails:
                            email = emails[0].get("email")
                            email_verified = bool(emails[0].get("verified"))
                except Exception:
                    pass

            if not email:
                raise OAuthError("OAUTH_MISSING_EMAIL", "GitHub account did not provide a valid email address.")

            return OAuthIdentity(
                provider="github",
                provider_subject=str(info.get("id")),
                email=email.strip().lower(),
                email_verified=email_verified,
                name=info.get("name") or info.get("login") or email.split("@")[0],
                avatar=info.get("avatar_url"),
            )


class LinkedInOAuthAdapter(BaseOAuthAdapter):
    provider_name = "linkedin"
    auth_url = "https://www.linkedin.com/oauth/v2/authorization"
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    userinfo_url = "https://api.linkedin.com/v2/userinfo"
    scopes = ["openid", "profile", "email"]

    def get_client_credentials(self):
        return settings.LINKEDIN_CLIENT_ID, settings.LINKEDIN_CLIENT_SECRET

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthIdentity:
        client_id, client_secret = self.get_client_credentials()
        if not client_id or not client_secret:
            raise OAuthError("OAUTH_CONFIGURATION_MISSING", "LinkedIn OAuth is not configured.")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                token_resp = await client.post(
                    self.token_url,
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
            except Exception as e:
                raise OAuthError("OAUTH_NETWORK_ERROR", f"Failed to connect to LinkedIn token endpoint: {e}")

            if token_resp.status_code != 200:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Failed to exchange authorization code with LinkedIn.")

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "LinkedIn did not return an access token.")

            try:
                user_resp = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except Exception as e:
                raise OAuthError("OAUTH_NETWORK_ERROR", f"Failed to fetch LinkedIn profile: {e}")

            if user_resp.status_code != 200:
                raise OAuthError("OAUTH_PROVIDER_ERROR", "Failed to retrieve LinkedIn user profile.")

            info = user_resp.json()
            email = info.get("email")
            if not email:
                raise OAuthError("OAUTH_MISSING_EMAIL", "LinkedIn account did not provide an email address.")

            return OAuthIdentity(
                provider="linkedin",
                provider_subject=str(info.get("sub")),
                email=email.strip().lower(),
                email_verified=bool(info.get("email_verified", True)),
                name=info.get("name") or email.split("@")[0],
                avatar=info.get("picture"),
            )


_adapters: Dict[str, BaseOAuthAdapter] = {
    "google": GoogleOAuthAdapter(),
    "github": GitHubOAuthAdapter(),
    "linkedin": LinkedInOAuthAdapter(),
}


def get_oauth_adapter(provider: str) -> Optional[BaseOAuthAdapter]:
    return _adapters.get(provider.lower())


def is_provider_configured(provider: str) -> bool:
    adapter = get_oauth_adapter(provider)
    return adapter.is_configured() if adapter else False


def get_configured_providers() -> Dict[str, bool]:
    return {name: adapter.is_configured() for name, adapter in _adapters.items()}
