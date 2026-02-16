"""Authentication endpoints.

Standards: python_clean.mdc
- Thin controller layer
- Delegates to services
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import AppSettings, DBSession
from app.core.exceptions import (
    InvalidCredentialsError,
    ResourceAlreadyExistsError,
    SessionRevokedError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.schemas.auth import AuthResponse, LoginRequest, RefreshRequest, SignupRequest

router = APIRouter()
logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: DBSession,
    settings: AppSettings,
    http_request: Request,
) -> AuthResponse:
    """Create a new user account."""
    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.user import SQLUserRepository

    user_repo = SQLUserRepository(session=db)
    profile_repo = SQLProfileRepository(session=db)
    auth_service = AuthService(
        user_repository=user_repo,
        profile_repository=profile_repo,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.access_token_expire_minutes,
        refresh_expire_days=settings.refresh_token_expire_days,
    )

    try:
        tokens = await auth_service.signup(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )

        logger.info("user_signup", email=request.email)

        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except ResourceAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: DBSession,
    settings: AppSettings,
    http_request: Request,
) -> AuthResponse:
    """Login with email and password."""
    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.user import SQLUserRepository

    try:
        user_repo = SQLUserRepository(session=db)
        auth_service = AuthService(
            user_repository=user_repo,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
            access_expire_minutes=settings.access_token_expire_minutes,
            refresh_expire_days=settings.refresh_token_expire_days,
        )

        tokens = await auth_service.login(
            email=request.email,
            password=request.password,
        )

        logger.info("user_login", email=request.email)

        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except InvalidCredentialsError:
        logger.warning("login_failed", email=request.email, reason="invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    except Exception as e:
        logger.error(
            "login_error",
            email=request.email,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again later.",
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshRequest,
    db: DBSession,
    settings: AppSettings,
) -> AuthResponse:
    """Refresh access token using refresh token."""
    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.user import SQLUserRepository

    user_repo = SQLUserRepository(session=db)
    auth_service = AuthService(
        user_repository=user_repo,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.access_token_expire_minutes,
        refresh_expire_days=settings.refresh_token_expire_days,
    )

    try:
        tokens = await auth_service.refresh(refresh_token=request.refresh_token)

        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except (TokenExpiredError, TokenInvalidError, SessionRevokedError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: DBSession,
    settings: AppSettings,
) -> None:
    """Logout current session (revoke refresh token)."""
    if not credentials:
        return

    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.user import SQLUserRepository

    user_repo = SQLUserRepository(session=db)
    auth_service = AuthService(
        user_repository=user_repo,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.access_token_expire_minutes,
        refresh_expire_days=settings.refresh_token_expire_days,
    )

    try:
        await auth_service.logout(access_token=credentials.credentials)
        logger.info("user_logout")
    except Exception as e:
        logger.warning("logout_failed", error=str(e))  # Logout should not fail


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout_all(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: DBSession,
    settings: AppSettings,
) -> None:
    """Logout all sessions for current user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.user import SQLUserRepository

    user_repo = SQLUserRepository(session=db)
    auth_service = AuthService(
        user_repository=user_repo,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.access_token_expire_minutes,
        refresh_expire_days=settings.refresh_token_expire_days,
    )

    try:
        await auth_service.logout_all(access_token=credentials.credentials)
        logger.info("user_logout_all")
    except (TokenExpiredError, TokenInvalidError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# ========================
# OAuth Endpoints
# ========================

from pydantic import BaseModel


class OAuthUrlResponse(BaseModel):
    """OAuth authorization URL response."""

    url: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request."""

    code: str
    state: str | None = None


@router.get("/oauth/google", response_model=OAuthUrlResponse)
async def google_oauth_url(
    settings: AppSettings,
) -> OAuthUrlResponse:
    """Get Google OAuth authorization URL."""
    from app.infra.auth.oauth import OAuthService

    oauth_service = OAuthService(settings)

    # Generate state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)

    url = oauth_service.get_google_auth_url(state=state)
    return OAuthUrlResponse(url=url)


@router.post("/oauth/google/callback", response_model=AuthResponse)
async def google_oauth_callback(
    request: OAuthCallbackRequest,
    db: DBSession,
    settings: AppSettings,
) -> AuthResponse:
    """Handle Google OAuth callback."""
    from app.infra.auth.oauth import OAuthError, OAuthService
    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.user import SQLUserRepository

    oauth_service = OAuthService(settings)

    try:
        # Get user info from Google
        user_info = await oauth_service.google_callback(code=request.code)

        # Create or get user
        user_repo = SQLUserRepository(session=db)
        profile_repo = SQLProfileRepository(session=db)
        auth_service = AuthService(
            user_repository=user_repo,
            profile_repository=profile_repo,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
            access_expire_minutes=settings.access_token_expire_minutes,
            refresh_expire_days=settings.refresh_token_expire_days,
        )

        tokens = await auth_service.oauth_login(
            email=user_info.email,
            provider=user_info.provider,
            provider_id=user_info.provider_id,
            full_name=user_info.name,
        )

        logger.info("oauth_login", provider="google", email=user_info.email)

        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except OAuthError as e:
        logger.error("oauth_error", provider="google", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OAuth error: {e.message}",
        )


@router.get("/oauth/github", response_model=OAuthUrlResponse)
async def github_oauth_url(
    settings: AppSettings,
) -> OAuthUrlResponse:
    """Get GitHub OAuth authorization URL."""
    from app.infra.auth.oauth import OAuthService

    oauth_service = OAuthService(settings)

    # Generate state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)

    url = oauth_service.get_github_auth_url(state=state)
    return OAuthUrlResponse(url=url)


@router.post("/oauth/github/callback", response_model=AuthResponse)
async def github_oauth_callback(
    request: OAuthCallbackRequest,
    db: DBSession,
    settings: AppSettings,
) -> AuthResponse:
    """Handle GitHub OAuth callback."""
    from app.infra.auth.oauth import OAuthError, OAuthService
    from app.infra.auth.service import AuthService
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.user import SQLUserRepository

    oauth_service = OAuthService(settings)

    try:
        # Get user info from GitHub
        user_info = await oauth_service.github_callback(code=request.code)

        # Create or get user
        user_repo = SQLUserRepository(session=db)
        profile_repo = SQLProfileRepository(session=db)
        auth_service = AuthService(
            user_repository=user_repo,
            profile_repository=profile_repo,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
            access_expire_minutes=settings.access_token_expire_minutes,
            refresh_expire_days=settings.refresh_token_expire_days,
        )

        tokens = await auth_service.oauth_login(
            email=user_info.email,
            provider=user_info.provider,
            provider_id=user_info.provider_id,
            full_name=user_info.name,
        )

        logger.info("oauth_login", provider="github", email=user_info.email)

        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except OAuthError as e:
        logger.error("oauth_error", provider="github", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OAuth error: {e.message}",
        )