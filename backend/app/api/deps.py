"""API dependencies for dependency injection.

Standards: python_clean.mdc
- DIP: inject abstractions
- Async context managers for cleanup
"""

from typing import Annotated, AsyncGenerator

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.domain.user import User
from app.core.exceptions import TokenExpiredError, TokenInvalidError
from app.infra.db.session import async_session_factory

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with proper cleanup."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_settings_dep() -> Settings:
    """Get application settings."""
    return get_settings()


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None

    try:
        from app.infra.auth.jwt import decode_access_token
        from app.infra.db.repositories.user import SQLUserRepository

        payload = decode_access_token(
            token=credentials.credentials,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

        user_repo = SQLUserRepository(session=db)
        user = await user_repo.get_by_id(payload["sub"])

        return user
    except (TokenExpiredError, TokenInvalidError):
        return None
    except Exception as e:
        logger.warning("auth_error", error=str(e))
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> User:
    """Get current authenticated user or raise 401."""
    # Debug logging
    logger.info("auth_check", credentials_present=credentials is not None)
    
    if not credentials:
        logger.warning("auth_failed", reason="no_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        from app.infra.auth.jwt import decode_access_token
        from app.infra.db.repositories.user import SQLUserRepository

        logger.info("auth_decoding", token_preview=credentials.credentials[:20] + "..." if credentials.credentials else "None")
        
        payload = decode_access_token(
            token=credentials.credentials,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

        logger.info("auth_decoded", user_id=payload.get("sub"))
        
        user_repo = SQLUserRepository(session=db)
        user = await user_repo.get_by_id(payload["sub"])

        if not user:
            logger.warning("auth_failed", reason="user_not_found", user_id=payload.get("sub"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        logger.info("auth_success", user_id=user.id)
        return user

    except TokenExpiredError:
        logger.warning("auth_failed", reason="token_expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError as e:
        logger.warning("auth_failed", reason="token_invalid", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Type aliases for cleaner endpoint signatures
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
AppSettings = Annotated[Settings, Depends(get_settings_dep)]
