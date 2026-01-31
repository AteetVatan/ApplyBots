"""Domain exception hierarchy.

Standards: python_clean.mdc
- Domain-specific exceptions
- Re-raise with context
- No swallowing exceptions
"""


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(message)


# Authentication Errors
class AuthenticationError(DomainError):
    """Base authentication error."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password", code="INVALID_CREDENTIALS")


class TokenExpiredError(AuthenticationError):
    """JWT token has expired."""

    def __init__(self) -> None:
        super().__init__("Token has expired", code="TOKEN_EXPIRED")


class TokenInvalidError(AuthenticationError):
    """JWT token is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid token", code="TOKEN_INVALID")


class SessionRevokedError(AuthenticationError):
    """Session has been revoked."""

    def __init__(self) -> None:
        super().__init__("Session has been revoked", code="SESSION_REVOKED")


# Authorization Errors
class AuthorizationError(DomainError):
    """Base authorization error."""

    pass


class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions."""

    def __init__(self, action: str) -> None:
        super().__init__(
            f"Insufficient permissions to {action}",
            code="INSUFFICIENT_PERMISSIONS",
        )


class PlanLimitExceededError(AuthorizationError):
    """User has exceeded their plan limits."""

    def __init__(self, limit_type: str, limit_value: int) -> None:
        super().__init__(
            f"Daily {limit_type} limit of {limit_value} exceeded",
            code="PLAN_LIMIT_EXCEEDED",
        )


# Resource Errors
class ResourceNotFoundError(DomainError):
    """Requested resource not found."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        super().__init__(
            f"{resource_type} with ID '{resource_id}' not found",
            code="RESOURCE_NOT_FOUND",
        )


class ResourceAlreadyExistsError(DomainError):
    """Resource already exists."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        super().__init__(
            f"{resource_type} with identifier '{identifier}' already exists",
            code="RESOURCE_EXISTS",
        )


# Validation Errors
class ValidationError(DomainError):
    """Input validation failed."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"Validation error on '{field}': {message}", code="VALIDATION_ERROR")


# Application Errors
class ApplicationError(DomainError):
    """Base application processing error."""

    pass


class LowMatchScoreError(ApplicationError):
    """Match score below threshold."""

    def __init__(self, score: int, threshold: int) -> None:
        super().__init__(
            f"Match score {score} is below threshold {threshold}",
            code="LOW_MATCH_SCORE",
        )


class TruthLockViolationError(ApplicationError):
    """Generated content contains unverified claims."""

    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        super().__init__(
            f"Truth-lock violations detected: {', '.join(violations)}",
            code="TRUTH_LOCK_VIOLATION",
        )


class QCRejectionError(ApplicationError):
    """Quality control rejected the application."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"QC rejected: {reason}", code="QC_REJECTED")


# Automation Errors
class AutomationError(DomainError):
    """Base automation error."""

    pass


class CaptchaDetectedError(AutomationError):
    """CAPTCHA detected during automation."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"CAPTCHA detected at {url}", code="CAPTCHA_DETECTED")


class MFARequiredError(AutomationError):
    """MFA/2FA required during automation."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"MFA required at {url}", code="MFA_REQUIRED")


class FormFieldNotFoundError(AutomationError):
    """Required form field not found."""

    def __init__(self, field: str, selector: str) -> None:
        self.field = field
        self.selector = selector
        super().__init__(
            f"Form field '{field}' not found with selector '{selector}'",
            code="FIELD_NOT_FOUND",
        )


# External Service Errors
class ExternalServiceError(DomainError):
    """External service error."""

    def __init__(self, service: str, message: str) -> None:
        self.service = service
        super().__init__(f"{service} error: {message}", code="EXTERNAL_SERVICE_ERROR")
