"""Internal service token generation and verification.

Used for secure service-to-service communication between FastAPI and Reactive Resume.
Tokens are HMAC-signed and contain user_id, resume_id, and timestamp for validation.
"""

import base64
import hashlib
import hmac
import time
from dataclasses import dataclass

# Token validity durations
SERVICE_TOKEN_TTL_SECONDS = 300  # 5 minutes
PRINTER_TOKEN_TTL_SECONDS = 300  # 5 minutes


@dataclass(frozen=True)
class ServiceTokenPayload:
    """Payload extracted from a verified service token."""

    user_id: str
    resume_id: str
    timestamp: int


def generate_service_token(
    *,
    user_id: str,
    resume_id: str,
    secret: str,
) -> str:
    """Generate HMAC-signed service token for internal API authentication.

    Args:
        user_id: The user ID to embed in the token.
        resume_id: The resume ID to embed in the token.
        secret: The shared secret for HMAC signing.

    Returns:
        A base64-encoded token in format: {payload_b64}.{signature}
    """
    timestamp = int(time.time())
    payload = f"{user_id}:{resume_id}:{timestamp}"
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    signature = hmac.new(
        secret.encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_service_token(
    *,
    token: str,
    secret: str,
) -> ServiceTokenPayload | None:
    """Verify service token and extract payload if valid.

    Args:
        token: The token to verify.
        secret: The shared secret for HMAC verification.

    Returns:
        ServiceTokenPayload if valid, None if invalid or expired.
    """
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None

        payload_b64, signature = parts
        expected_sig = hmac.new(
            secret.encode(),
            payload_b64.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        payload = base64.urlsafe_b64decode(payload_b64).decode()
        payload_parts = payload.split(":")
        if len(payload_parts) != 3:
            return None

        user_id, resume_id, timestamp_str = payload_parts
        timestamp = int(timestamp_str)

        # Check expiration
        if time.time() - timestamp > SERVICE_TOKEN_TTL_SECONDS:
            return None

        return ServiceTokenPayload(
            user_id=user_id,
            resume_id=resume_id,
            timestamp=timestamp,
        )
    except (ValueError, UnicodeDecodeError, base64.binascii.Error):
        return None


def generate_printer_token(
    *,
    resume_id: str,
    secret: str,
) -> str:
    """Generate printer token compatible with Reactive Resume's format.

    This token format matches Reactive Resume's printer-token.ts implementation
    to allow Playwright to access the printer route.

    Args:
        resume_id: The resume ID to embed in the token.
        secret: The AUTH_SECRET used by Reactive Resume.

    Returns:
        A base64-encoded token in format: {payload_b64}.{signature}
    """
    timestamp = int(time.time() * 1000)  # Milliseconds like JS
    payload = f"{resume_id}:{timestamp}"
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    # Reactive Resume uses SHA-256 of "{payload}.{secret}"
    signature = hashlib.sha256(f"{payload_b64}.{secret}".encode()).hexdigest()
    return f"{payload_b64}.{signature}"
