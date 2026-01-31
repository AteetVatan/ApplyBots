"""Lever ATS adapter.

Standards: python_clean.mdc
- Specific selectors for Lever forms
- Audit logging for each step
"""

from playwright.async_api import Page

from app.core.ports.ats import ApplicationData, SubmissionResult
from app.core.ports.storage import FileStorage
from app.infra.ats_adapters.base import BaseATSAdapter


class LeverAdapter(BaseATSAdapter):
    """Adapter for Lever ATS job applications."""

    # Lever-specific selectors
    SELECTORS = {
        "name": "input[name='name']",
        "email": "input[name='email']",
        "phone": "input[name='phone']",
        "resume": "input[type='file']",
        "cover_letter": "textarea[name='comments']",
        "linkedin": "input[name='urls[LinkedIn]']",
        "portfolio": "input[name='urls[Portfolio]']",
        "submit_button": "button[type='submit'], .application-submit",
    }

    def __init__(self, *, storage: FileStorage, application_id: str) -> None:
        super().__init__(storage=storage, application_id=application_id)

    @property
    def name(self) -> str:
        return "lever"

    async def detect(self, *, url: str) -> bool:
        """Check if URL is a Lever job listing."""
        lever_patterns = [
            "lever.co",
            "jobs.lever.co",
        ]
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in lever_patterns)

    async def fill_form(
        self,
        *,
        page: Page,
        data: ApplicationData,
    ) -> None:
        """Fill the Lever application form."""
        # Check for blockers first
        await self.check_blockers(page=page)

        # Screenshot before filling
        await self._capture_screenshot(page=page, step="form_loaded")

        # Lever typically uses full name field
        full_name = f"{data.first_name} {data.last_name}".strip()
        if full_name:
            await self._fill_field(
                page=page,
                selector=self.SELECTORS["name"],
                value=full_name,
                field_name="Name",
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
                    error_message="Resume upload not available",
                )

        # Fill additional info / cover letter
        if data.cover_letter:
            try:
                await self._fill_field(
                    page=page,
                    selector=self.SELECTORS["cover_letter"],
                    value=data.cover_letter,
                    field_name="Additional Info",
                )
            except Exception:
                self._log_step(
                    action="cover_letter_skipped",
                    success=True,
                    error_message="Additional info field not available",
                )

        # Fill LinkedIn URL
        if data.linkedin_url:
            try:
                await self._fill_field(
                    page=page,
                    selector=self.SELECTORS["linkedin"],
                    value=data.linkedin_url,
                    field_name="LinkedIn",
                )
            except Exception:
                self._log_step(
                    action="linkedin_skipped",
                    success=True,
                    error_message="LinkedIn field not available",
                )

        # Fill portfolio URL
        if data.portfolio_url:
            try:
                await self._fill_field(
                    page=page,
                    selector=self.SELECTORS["portfolio"],
                    value=data.portfolio_url,
                    field_name="Portfolio",
                )
            except Exception:
                self._log_step(
                    action="portfolio_skipped",
                    success=True,
                    error_message="Portfolio field not available",
                )

        # Fill custom answers for Lever's card-based questions
        for question, answer in data.answers.items():
            question_selector = f"textarea[data-hook*='{question}'], input[data-hook*='{question}']"
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
        """Submit the Lever application."""
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

        # Wait for response
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        # Screenshot after submit
        await self._capture_screenshot(page=page, step="after_submit")

        # Check for Lever's thank you page
        confirmation_selectors = [
            ".thank-you",
            "[data-qa='thank-you']",
            "text=Thank you for applying",
            "text=Application received",
        ]

        for selector in confirmation_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    return SubmissionResult(
                        success=True,
                        audit_trail=self._audit_trail,
                        screenshots=self._screenshots,
                    )
            except Exception:
                continue

        # Check for validation errors
        error_selectors = [".error", ".validation-error", "[role='alert']"]

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

        # Assume success if no errors
        return SubmissionResult(
            success=True,
            audit_trail=self._audit_trail,
            screenshots=self._screenshots,
        )
