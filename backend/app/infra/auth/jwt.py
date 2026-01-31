"""JWT token utilities.

Standards: python_clean.mdc
- Pure functions for token encoding/decoding
- Domain exceptions for errors
"""

from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt

from app.core.exceptions import TokenExpiredError, TokenInvalidError


def create_token(
    *,
    user_id: str,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta,
    token_type: Literal["access", "refresh"],
) -> str:
    """Create a JWT token."""
    # Use timezone-aware datetime to avoid timestamp conversion issues
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": token_type,
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(
    *,
    token: str,
    secret_key: str,
    algorithm: str,
) -> dict:
    """Decode and validate an access token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])

        if payload.get("type") != "access":
            raise TokenInvalidError()

        return payload

    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError() from e
    except jwt.InvalidTokenError as e:
        raise TokenInvalidError() from e


def decode_refresh_token(
    *,
    token: str,
    secret_key: str,
    algorithm: str,
) -> dict:
    """Decode and validate a refresh token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])

        if payload.get("type") != "refresh":
            raise TokenInvalidError()

        return payload

    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError() from e
    except jwt.InvalidTokenError as e:
        raise TokenInvalidError() from e
