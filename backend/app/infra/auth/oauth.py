"""OAuth authentication service.

Standards: python_clean.mdc
- Async HTTP clients
- Proper error handling
- No secrets in logs
"""

from dataclasses import dataclass
from typing import Literal

import httpx
import structlog

from app.config import Settings

logger = structlog.get_logger(__name__)


@dataclass
class OAuthUserInfo:
    """User info from OAuth provider."""

    email: str
    name: str | None
    picture_url: str | None
    provider: Literal["google", "github"]
    provider_id: str


class OAuthError(Exception):
    """OAuth authentication error."""

    def __init__(self, message: str, provider: str) -> None:
        self.message = message
        self.provider = provider
        super().__init__(f"OAuth error ({provider}): {message}")


class OAuthService:
    """OAuth authentication service for Google and GitHub.

    Handles OAuth 2.0 flow for social login.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize OAuth service.

        Args:
            settings: Application settings with OAuth credentials
        """
        self._settings = settings

    # ========================
    # Google OAuth
    # ========================

    def get_google_auth_url(self, *, state: str | None = None) -> str:
        """Get Google OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Google authorization URL
        """
        params = {
            "client_id": self._settings.google_client_id.get_secret_value(),
            "redirect_uri": self._settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }

        if state:
            params["state"] = state

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    async def google_callback(self, *, code: str) -> OAuthUserInfo:
        """Handle Google OAuth callback.

        Args:
            code: Authorization code from Google

        Returns:
            User info from Google

        Raises:
            OAuthError: If OAuth flow fails
        """
        # Exchange code for tokens
        token_data = await self._google_get_tokens(code)
        access_token = token_data.get("access_token")

        if not access_token:
            raise OAuthError("No access token received", "google")

        # Get user info
        user_info = await self._google_get_user_info(access_token)

        return OAuthUserInfo(
            email=user_info["email"],
            name=user_info.get("name"),
            picture_url=user_info.get("picture"),
            provider="google",
            provider_id=user_info["sub"],
        )

    async def _google_get_tokens(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self._settings.google_client_id.get_secret_value(),
                    "client_secret": self._settings.google_client_secret.get_secret_value(),
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self._settings.google_redirect_uri,
                },
            )

            if response.status_code != 200:
                logger.error(
                    "google_token_exchange_failed",
                    status_code=response.status_code,
                )
                raise OAuthError("Token exchange failed", "google")

            return response.json()

    async def _google_get_user_info(self, access_token: str) -> dict:
        """Get user info from Google API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                logger.error(
                    "google_userinfo_failed",
                    status_code=response.status_code,
                )
                raise OAuthError("Failed to get user info", "google")

            return response.json()

    # ========================
    # GitHub OAuth
    # ========================

    def get_github_auth_url(self, *, state: str | None = None) -> str:
        """Get GitHub OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            GitHub authorization URL
        """
        params = {
            "client_id": self._settings.github_client_id.get_secret_value(),
            "redirect_uri": self._settings.github_redirect_uri,
            "scope": "read:user user:email",
        }

        if state:
            params["state"] = state

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://github.com/login/oauth/authorize?{query}"

    async def github_callback(self, *, code: str) -> OAuthUserInfo:
        """Handle GitHub OAuth callback.

        Args:
            code: Authorization code from GitHub

        Returns:
            User info from GitHub

        Raises:
            OAuthError: If OAuth flow fails
        """
        # Exchange code for tokens
        token_data = await self._github_get_tokens(code)
        access_token = token_data.get("access_token")

        if not access_token:
            raise OAuthError("No access token received", "github")

        # Get user info
        user_info = await self._github_get_user_info(access_token)

        # GitHub might not include email in user info, need to fetch separately
        email = user_info.get("email")
        if not email:
            email = await self._github_get_primary_email(access_token)

        if not email:
            raise OAuthError("Could not get user email", "github")

        return OAuthUserInfo(
            email=email,
            name=user_info.get("name"),
            picture_url=user_info.get("avatar_url"),
            provider="github",
            provider_id=str(user_info["id"]),
        )

    async def _github_get_tokens(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": self._settings.github_client_id.get_secret_value(),
                    "client_secret": self._settings.github_client_secret.get_secret_value(),
                    "code": code,
                    "redirect_uri": self._settings.github_redirect_uri,
                },
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                logger.error(
                    "github_token_exchange_failed",
                    status_code=response.status_code,
                )
                raise OAuthError("Token exchange failed", "github")

            data = response.json()

            if "error" in data:
                logger.error(
                    "github_token_error",
                    error=data.get("error"),
                    description=data.get("error_description"),
                )
                raise OAuthError(data.get("error_description", "Unknown error"), "github")

            return data

    async def _github_get_user_info(self, access_token: str) -> dict:
        """Get user info from GitHub API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code != 200:
                logger.error(
                    "github_userinfo_failed",
                    status_code=response.status_code,
                )
                raise OAuthError("Failed to get user info", "github")

            return response.json()

    async def _github_get_primary_email(self, access_token: str) -> str | None:
        """Get user's primary email from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code != 200:
                return None

            emails = response.json()

            # Find primary and verified email
            for email_data in emails:
                if email_data.get("primary") and email_data.get("verified"):
                    return email_data.get("email")

            # Fallback to any verified email
            for email_data in emails:
                if email_data.get("verified"):
                    return email_data.get("email")

            return None
