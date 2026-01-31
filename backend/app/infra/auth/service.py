"""Authentication service.

Standards: python_clean.mdc
- Async methods
- Domain exceptions
- kw-only args
"""

import uuid
from dataclasses import dataclass
from datetime import timedelta

from app.core.domain.profile import Preferences, Profile
from app.core.domain.subscription import PLAN_DAILY_LIMITS, Plan, Subscription
from app.core.domain.user import User
from app.core.exceptions import (
    InvalidCredentialsError,
    ResourceAlreadyExistsError,
    SessionRevokedError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.core.ports.repositories import ProfileRepository, UserRepository
from app.infra.auth.jwt import create_token, decode_access_token, decode_refresh_token
from app.infra.auth.password import hash_password, verify_password


@dataclass
class TokenPair:
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str


class AuthService:
    """Authentication service handling signup, login, and token management."""

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
        profile_repository: ProfileRepository | None = None,
    ) -> None:
        self._user_repo = user_repository
        self._profile_repo = profile_repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire = timedelta(minutes=access_expire_minutes)
        self._refresh_expire = timedelta(days=refresh_expire_days)

    async def signup(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> TokenPair:
        """Create a new user account."""
        # Check if email exists
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise ResourceAlreadyExistsError("User", email)

        # Create user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=email,
            password_hash=hash_password(password),
        )
        await self._user_repo.create(user)

        # Create profile with default preferences
        if self._profile_repo:
            profile = Profile(
                id=str(uuid.uuid4()),
                user_id=user_id,
                full_name=full_name,
                preferences=Preferences(),
            )
            await self._profile_repo.create(profile)

        # Generate tokens
        return self._create_token_pair(user_id)

    async def login(
        self,
        *,
        email: str,
        password: str,
    ) -> TokenPair:
        """Authenticate user and return tokens."""
        user = await self._user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        return self._create_token_pair(user.id)

    async def oauth_login(
        self,
        *,
        email: str,
        provider: str,
        provider_id: str,
        full_name: str | None = None,
    ) -> TokenPair:
        """Login or signup via OAuth provider.

        Creates a new user if one doesn't exist for this email/provider.

        Args:
            email: User email from OAuth provider
            provider: OAuth provider name (google, github)
            provider_id: User ID from OAuth provider
            full_name: User's full name from OAuth provider

        Returns:
            Token pair for authenticated user
        """
        # Check if user exists
        user = await self._user_repo.get_by_email(email)

        if not user:
            # Create new user (OAuth users don't have a password)
            import secrets
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                email=email,
                password_hash=hash_password(secrets.token_urlsafe(32)),  # Random password
                oauth_provider=provider,
                oauth_provider_id=provider_id,
            )
            await self._user_repo.create(user)

            # Create profile
            if self._profile_repo:
                profile = Profile(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    full_name=full_name,
                    preferences=Preferences(),
                )
                await self._profile_repo.create(profile)

        return self._create_token_pair(user.id)

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token."""
        try:
            payload = decode_refresh_token(
                token=refresh_token,
                secret_key=self._secret_key,
                algorithm=self._algorithm,
            )
        except (TokenExpiredError, TokenInvalidError):
            raise

        user_id = payload["sub"]

        # Verify user still exists
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise TokenInvalidError()

        # TODO: Check if refresh token is revoked in session store

        return self._create_token_pair(user_id)

    async def logout(self, *, access_token: str) -> None:
        """Revoke the current session's refresh token."""
        try:
            payload = decode_access_token(
                token=access_token,
                secret_key=self._secret_key,
                algorithm=self._algorithm,
            )
            # TODO: Revoke refresh token in session store
        except (TokenExpiredError, TokenInvalidError):
            pass  # Logout should not fail

    async def logout_all(self, *, access_token: str) -> None:
        """Revoke all sessions for the current user."""
        payload = decode_access_token(
            token=access_token,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
        )
        # TODO: Revoke all refresh tokens for user in session store

    def _create_token_pair(self, user_id: str) -> TokenPair:
        """Create access and refresh token pair."""
        access_token = create_token(
            user_id=user_id,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
            expires_delta=self._access_expire,
            token_type="access",
        )

        refresh_token = create_token(
            user_id=user_id,
            secret_key=self._secret_key,
            algorithm=self._algorithm,
            expires_delta=self._refresh_expire,
            token_type="refresh",
        )

        return TokenPair(access_token=access_token, refresh_token=refresh_token)
