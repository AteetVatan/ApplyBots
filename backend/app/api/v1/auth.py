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

    user_repo = SQLUserRepository(session=db)
    auth_service = AuthService(
        user_repository=user_repo,
        secret_key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.access_token_expire_minutes,
        refresh_expire_days=settings.refresh_token_expire_days,
    )

    try:
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
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


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
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
    except Exception:
        pass  # Logout should not fail


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
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
