"""Greenhouse ATS adapter.

Standards: python_clean.mdc
- Specific selectors for Greenhouse forms
- Audit logging for each step
"""

from playwright.async_api import Page

from app.core.ports.ats import ApplicationData, SubmissionResult
from app.core.ports.storage import FileStorage
from app.infra.ats_adapters.base import BaseATSAdapter


class GreenhouseAdapter(BaseATSAdapter):
    """Adapter for Greenhouse ATS job applications."""

    # Greenhouse-specific selectors
    SELECTORS = {
        "first_name": "#first_name, input[name='job_application[first_name]']",
        "last_name": "#last_name, input[name='job_application[last_name]']",
        "email": "#email, input[name='job_application[email]']",
        "phone": "#phone, input[name='job_application[phone]']",
        "resume": "input[type='file'][name*='resume'], #resume",
        "cover_letter": "textarea[name*='cover_letter'], #cover_letter",
        "linkedin": "input[name*='linkedin'], input[placeholder*='LinkedIn']",
        "submit_button": "button[type='submit'], input[type='submit']",
    }

    def __init__(self, *, storage: FileStorage, application_id: str) -> None:
        super().__init__(storage=storage, application_id=application_id)

    @property
    def name(self) -> str:
        return "greenhouse"

    async def detect(self, *, url: str) -> bool:
        """Check if URL is a Greenhouse job listing."""
        greenhouse_patterns = [
            "greenhouse.io",
            "boards.greenhouse.io",
            "/jobs/",
        ]
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in greenhouse_patterns)

    async def fill_form(
        self,
        *,
        page: Page,
        data: ApplicationData,
    ) -> None:
        """Fill the Greenhouse application form."""
        # Check for blockers first
        await self.check_blockers(page=page)

        # Screenshot before filling
        await self._capture_screenshot(page=page, step="form_loaded")

        # Fill basic info
        if data.first_name:
            await self._fill_field(
                page=page,
                selector=self.SELECTORS["first_name"],
                value=data.first_name,
                field_name="First Name",
            )

        if data.last_name:
            await self._fill_field(
                page=page,
                selector=self.SELECTORS["last_name"],
                value=data.last_name,
                field_name="Last Name",
            )

        if data.email:
            await self._fill_field(
                page=page,
                selector=self.SELECTORS["email"],
                value=data.email,
                field_name="Email",
            )

        if data.phone:
            await self._fill_field(
                page=page,
                selector=self.SELECTORS["phone"],
                value=data.phone,
                field_name="Phone",
            )

        # Upload resume
        if data.resume_path:
            try:
                await self._upload_file(
                    page=page,
                    selector=self.SELECTORS["resume"],
                    file_path=data.resume_path,
                )
            except Exception:
                self._log_step(
                    action="resume_upload_skipped",
                    success=True,
                    error_message="Resume upload not available or already uploaded",
                )

        # Fill cover letter if provided
        if data.cover_letter:
            try:
                await self._fill_field(
                    page=page,
                    selector=self.SELECTORS["cover_letter"],
                    value=data.cover_letter,
                    field_name="Cover Letter",
                )
            except Exception:
                self._log_step(
                    action="cover_letter_skipped",
                    success=True,
                    error_message="Cover letter field not available",
                )

        # Fill LinkedIn if provided
        if data.linkedin_url:
            try:
                await self._fill_field(
                    page=page,
                    selector=self.SELECTORS["linkedin"],
                    value=data.linkedin_url,
                    field_name="LinkedIn URL",
                )
            except Exception:
                self._log_step(
                    action="linkedin_skipped",
                    success=True,
                    error_message="LinkedIn field not available",
                )

        # Fill custom answers
        for question, answer in data.answers.items():
            # Try to find the question field
            question_selector = f"textarea[name*='{question}'], input[name*='{question}']"
            try:
                await self._fill_field(
                    page=page,
                    selector=question_selector,
                    value=answer,
                    field_name=question,
                )
            except Exception:
                self._log_step(
                    action=f"custom_answer_skipped",
                    success=True,
                    error_message=f"Field not found for: {question}",
                )

        # Screenshot after filling
        await self._capture_screenshot(page=page, step="form_filled")

    async def submit(self, *, page: Page) -> SubmissionResult:
        """Submit the Greenhouse application."""
        # Check for blockers before submit
        await self.check_blockers(page=page)

        # Screenshot before submit
        await self._capture_screenshot(page=page, step="before_submit")

        # Click submit button
        submitted = await self._click_element(
            page=page,
            selector=self.SELECTORS["submit_button"],
            description="submit",
        )

        if not submitted:
            return SubmissionResult(
                success=False,
                error_message="Submit button not found",
                needs_manual=True,
                audit_trail=self._audit_trail,
                screenshots=self._screenshots,
            )

        # Wait for navigation or confirmation
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        # Screenshot after submit
        await self._capture_screenshot(page=page, step="after_submit")

        # Check for confirmation
        confirmation_selectors = [
            ".success-message",
            "[data-testid='success']",
            "text=Thank you",
            "text=Application submitted",
        ]

        for selector in confirmation_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    return SubmissionResult(
                        success=True,
                        confirmation_id=None,
                        audit_trail=self._audit_trail,
                        screenshots=self._screenshots,
                    )
            except Exception:
                continue

        # Check for errors
        error_selectors = [".error-message", ".field-error", "[role='alert']"]

        for selector in error_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    error_text = await element.text_content()
                    return SubmissionResult(
                        success=False,
                        error_message=error_text,
                        needs_manual=True,
                        audit_trail=self._audit_trail,
                        screenshots=self._screenshots,
                    )
            except Exception:
                continue

        # Assume success if no errors found
        return SubmissionResult(
            success=True,
            audit_trail=self._audit_trail,
            screenshots=self._screenshots,
        )
