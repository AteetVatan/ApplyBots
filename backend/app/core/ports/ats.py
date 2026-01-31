"""ATS adapter port interface.

Standards: python_clean.mdc
- Protocol for interfaces
- Enum for error actions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol


class ErrorAction(Enum):
    """Action to take on automation error."""

    RETRY = "retry"
    ABORT = "abort"
    MANUAL_NEEDED = "manual_needed"
    SKIP = "skip"


@dataclass
class ApplicationData:
    """Data needed to fill an application."""

    resume_path: str
    cover_letter: str | None = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    answers: dict[str, str] = field(default_factory=dict)


@dataclass
class AuditStep:
    """Single step in the automation audit trail."""

    action: str
    selector: str | None = None
    value: str | None = None
    success: bool = True
    error_message: str | None = None
    screenshot_key: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SubmissionResult:
    """Result of application submission."""

    success: bool
    confirmation_id: str | None = None
    error_message: str | None = None
    needs_manual: bool = False
    audit_trail: list[AuditStep] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)


class ATSAdapter(Protocol):
    """ATS adapter interface for Playwright automation."""

    async def detect(self, *, url: str) -> bool:
        """Check if this adapter can handle the given URL."""
        ...

    async def fill_form(
        self,
        *,
        url: str,
        data: ApplicationData,
    ) -> list[AuditStep]:
        """Fill the application form, return audit steps."""
        ...

    async def submit(self, *, url: str) -> SubmissionResult:
        """Submit the application."""
        ...

    async def handle_error(
        self,
        *,
        error: Exception,
        url: str,
    ) -> ErrorAction:
        """Determine action for an error."""
        ...

    async def capture_screenshot(self, *, key: str) -> str:
        """Capture and store a screenshot, return S3 key."""
        ...
