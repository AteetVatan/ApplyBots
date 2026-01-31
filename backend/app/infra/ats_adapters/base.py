"""Base ATS adapter with shared logic.

Standards: python_clean.mdc
- Abstract base class
- Audit logging
- Screenshot capture
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from playwright.async_api import Page

from app.core.exceptions import CaptchaDetectedError, FormFieldNotFoundError, MFARequiredError
from app.core.ports.ats import ApplicationData, AuditStep, ErrorAction, SubmissionResult
from app.core.ports.storage import FileStorage


class BaseATSAdapter(ABC):
    """Base class for ATS adapters."""

    def __init__(self, *, storage: FileStorage, application_id: str) -> None:
        self._storage = storage
        self._application_id = application_id
        self._audit_trail: list[AuditStep] = []
        self._screenshots: list[str] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """ATS name identifier."""
        ...

    @abstractmethod
    async def detect(self, *, url: str) -> bool:
        """Check if this adapter can handle the given URL."""
        ...

    @abstractmethod
    async def fill_form(
        self,
        *,
        page: Page,
        data: ApplicationData,
    ) -> None:
        """Fill the application form."""
        ...

    @abstractmethod
    async def submit(self, *, page: Page) -> SubmissionResult:
        """Submit the application."""
        ...

    async def check_blockers(self, *, page: Page) -> None:
        """Check for CAPTCHA, MFA, or other blockers."""
        url = page.url

        # Check for CAPTCHA
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            ".g-recaptcha",
            "#captcha",
            "[data-sitekey]",
        ]

        for selector in captcha_selectors:
            element = await page.query_selector(selector)
            if element:
                await self._capture_screenshot(page=page, step="captcha_detected")
                raise CaptchaDetectedError(url)

        # Check for login/MFA
        mfa_indicators = ["[data-testid='mfa']", ".mfa-challenge", "#otp-input"]

        for selector in mfa_indicators:
            element = await page.query_selector(selector)
            if element:
                await self._capture_screenshot(page=page, step="mfa_detected")
                raise MFARequiredError(url)

    async def handle_error(
        self,
        *,
        error: Exception,
        url: str,
    ) -> ErrorAction:
        """Determine action for an error."""
        if isinstance(error, CaptchaDetectedError):
            return ErrorAction.MANUAL_NEEDED
        if isinstance(error, MFARequiredError):
            return ErrorAction.MANUAL_NEEDED
        if isinstance(error, FormFieldNotFoundError):
            return ErrorAction.RETRY
        return ErrorAction.ABORT

    async def _fill_field(
        self,
        *,
        page: Page,
        selector: str,
        value: str,
        field_name: str,
        retries: int = 2,
    ) -> None:
        """Fill a form field with retry logic."""
        for attempt in range(retries + 1):
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    await element.fill(value)
                    self._log_step(
                        action="fill_field",
                        selector=selector,
                        value=value[:20] + "..." if len(value) > 20 else value,
                    )
                    return
            except Exception:
                if attempt == retries:
                    self._log_step(
                        action="fill_field_failed",
                        selector=selector,
                        success=False,
                        error_message=f"Field not found: {field_name}",
                    )
                    raise FormFieldNotFoundError(field_name, selector)

    async def _click_element(
        self,
        *,
        page: Page,
        selector: str,
        description: str,
    ) -> bool:
        """Click an element."""
        try:
            element = await page.wait_for_selector(selector, timeout=5000)
            if element:
                await element.click()
                self._log_step(action=f"click_{description}", selector=selector)
                return True
        except Exception as e:
            self._log_step(
                action=f"click_{description}_failed",
                selector=selector,
                success=False,
                error_message=str(e),
            )
        return False

    async def _upload_file(
        self,
        *,
        page: Page,
        selector: str,
        file_path: str,
    ) -> None:
        """Upload a file."""
        try:
            file_input = await page.wait_for_selector(selector, timeout=5000)
            if file_input:
                await file_input.set_input_files(file_path)
                self._log_step(action="upload_file", selector=selector)
        except Exception as e:
            self._log_step(
                action="upload_file_failed",
                selector=selector,
                success=False,
                error_message=str(e),
            )
            raise

    async def _capture_screenshot(
        self,
        *,
        page: Page,
        step: str,
    ) -> str:
        """Capture and store a screenshot."""
        screenshot_bytes = await page.screenshot(full_page=True)
        key = f"screenshots/{self._application_id}/{step}_{uuid.uuid4().hex[:8]}.png"

        await self._storage.upload(
            key=key,
            data=screenshot_bytes,
            content_type="image/png",
        )

        self._screenshots.append(key)
        self._log_step(action=f"screenshot_{step}", screenshot_key=key)

        return key

    def _log_step(
        self,
        *,
        action: str,
        selector: str | None = None,
        value: str | None = None,
        success: bool = True,
        error_message: str | None = None,
        screenshot_key: str | None = None,
    ) -> None:
        """Log an audit step."""
        self._audit_trail.append(
            AuditStep(
                action=action,
                selector=selector,
                value=value,
                success=success,
                error_message=error_message,
                screenshot_key=screenshot_key,
                timestamp=datetime.utcnow(),
            )
        )

    def get_audit_trail(self) -> list[AuditStep]:
        """Get the audit trail."""
        return self._audit_trail

    def get_screenshots(self) -> list[str]:
        """Get the screenshot keys."""
        return self._screenshots
