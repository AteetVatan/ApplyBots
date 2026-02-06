"""PDF generation service using Playwright.

Provides high-quality PDF generation by rendering resume templates
via Reactive Resume's printer route and capturing as PDF.

Uses multiprocessing to run Playwright in a separate process, avoiding
Windows asyncio subprocess issues (NotImplementedError on SelectorEventLoop).
"""

import asyncio
import logging
import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Literal

logger = logging.getLogger(__name__)

# Process pool for running Playwright (separate process has its own event loop)
_executor: ProcessPoolExecutor | None = None

# Page format dimensions (CSS pixels at 96 DPI)
PAGE_DIMENSIONS: dict[str, tuple[str, str]] = {
    "letter": ("816px", "1056px"),  # 8.5" x 11"
    "a4": ("794px", "1123px"),  # 210mm x 297mm
}


# PDF size thresholds (bytes)
# A typical 1-page CV should be 50-200KB
MAX_EXPECTED_PDF_SIZE = 1_000_000  # 1MB - warn if exceeded
MAX_ALLOWED_PDF_SIZE = 3_000_000  # 3MB - fail if exceeded (likely wrong content)


def _generate_pdf_in_process(
    reactive_resume_url: str,
    resume_id: str,
    printer_token: str,
    service_token: str,
    page_format: str,
    margin_x: int,
    margin_y: int,
    timeout_ms: int,
) -> bytes:
    """Generate PDF in a separate process using Playwright.

    This runs in a separate process to have its own event loop,
    avoiding Windows asyncio subprocess issues.

    Includes safety checks:
    - Detects redirects (indicates token verification failure)
    - Requires .resume-preview-container to be present
    - Validates PDF size to catch wrong content
    """
    import sys

    # On Windows, set ProactorEventLoop policy before any asyncio operations.
    # sync_playwright internally uses asyncio for subprocess management.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Import playwright here to ensure it's in the subprocess
    from playwright.sync_api import sync_playwright

    page_dimensions = {
        "letter": ("816px", "1056px"),
        "a4": ("794px", "1123px"),
    }

    browser = None
    playwright = None
    try:
        playwright = sync_playwright().start()
        print("pdf_printer: playwright started")

        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
            ],
        )
        print("pdf_printer: browser launched")

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
        )
        page = context.new_page()

        # Construct printer URL with tokens
        url = (
            f"{reactive_resume_url}/printer/{resume_id}"
            f"?token={printer_token}&service_token={service_token}"
        )

        print(f"pdf_printer: navigating to {url.split('?')[0]}")

        # Navigate and wait for network idle
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        print("pdf_printer: page loaded")

        # SAFETY CHECK 1: Detect redirects (indicates auth/token failure)
        # If token verification fails, Reactive Resume redirects to homepage
        final_url = page.url
        if "/printer/" not in final_url:
            raise RuntimeError(
                f"Redirect detected: expected /printer/ route but ended at {final_url}. "
                "Token verification likely failed - check AUTH_SECRET matches PRINTER_TOKEN_SECRET."
            )
        print(f"pdf_printer: URL verified (still on printer route)")

        # Wait for resume to be fully rendered (webfonts loaded)
        # data-wf-loaded is set by Reactive Resume's useWebfonts hook
        webfonts_loaded = False
        try:
            page.wait_for_function(
                "document.body.getAttribute('data-wf-loaded') === 'true'",
                timeout=5000,  # 5s - fonts should load quickly
            )
            print("pdf_printer: webfonts loaded")
            webfonts_loaded = True
        except Exception as e:
            print(f"pdf_printer: webfonts timeout ({e}), will verify container")

        # SAFETY CHECK 2: Resume container MUST be present (not optional)
        # This ensures we're rendering the actual CV, not an error page or homepage
        try:
            page.wait_for_selector(".resume-preview-container", timeout=10000)
            print("pdf_printer: resume container found")
        except Exception as e:
            raise RuntimeError(
                "Resume preview container (.resume-preview-container) not found. "
                "The page is likely showing an error or the homepage instead of the CV. "
                f"Current URL: {page.url}. Error: {e}"
            )

        # Small delay if webfonts didn't load to let content settle
        if not webfonts_loaded:
            time.sleep(0.5)

        # Get page dimensions
        width, height = page_dimensions.get(page_format, page_dimensions["letter"])

        # Convert margins from points (pt) to millimeters (mm) for Playwright
        # 1pt = 0.352778mm (standard conversion)
        PT_TO_MM = 0.352778
        margin_x_mm = margin_x * PT_TO_MM
        margin_y_mm = margin_y * PT_TO_MM

        # Generate PDF with margins and background colors
        pdf_buffer = page.pdf(
            width=width,
            height=height,
            print_background=True,  # Ensures colors are captured
            margin={
                "top": f"{margin_y_mm}mm",
                "bottom": f"{margin_y_mm}mm",
                "left": f"{margin_x_mm}mm",
                "right": f"{margin_x_mm}mm",
            },
        )

        pdf_size = len(pdf_buffer)
        print(f"pdf_printer: generated {pdf_size} bytes")

        # SAFETY CHECK 3: Validate PDF size
        # A typical 1-page CV is 50-200KB. If it's >1MB, something may be wrong
        if pdf_size > MAX_ALLOWED_PDF_SIZE:
            raise RuntimeError(
                f"PDF size ({pdf_size:,} bytes) exceeds maximum allowed ({MAX_ALLOWED_PDF_SIZE:,} bytes). "
                "This suggests the wrong content was captured (possibly homepage or error page)."
            )
        if pdf_size > MAX_EXPECTED_PDF_SIZE:
            print(
                f"pdf_printer: WARNING - PDF size ({pdf_size:,} bytes) is larger than expected. "
                f"A typical CV is under {MAX_EXPECTED_PDF_SIZE:,} bytes."
            )

        context.close()
        browser.close()
        playwright.stop()

        return pdf_buffer

    except Exception as e:
        print(f"pdf_printer: FAILED - {type(e).__name__}: {e}")
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        if playwright:
            try:
                playwright.stop()
            except Exception:
                pass
        raise RuntimeError(f"Playwright error: {type(e).__name__}: {e}") from e


def _get_executor() -> ProcessPoolExecutor:
    """Get or create the process pool executor."""
    global _executor
    if _executor is None:
        # Use spawn to create clean processes on Windows
        mp_context = mp.get_context("spawn")
        _executor = ProcessPoolExecutor(max_workers=1, mp_context=mp_context)
    return _executor


async def generate_pdf(
    *,
    reactive_resume_url: str,
    resume_id: str,
    printer_token: str,
    service_token: str,
    page_format: Literal["letter", "a4"] = "letter",
    margin_x: int = 14,
    margin_y: int = 12,
    timeout_ms: int = 30000,
) -> bytes:
    """Generate PDF using Playwright by rendering Reactive Resume's printer route.

    Uses a process pool executor to run Playwright in a separate process,
    which has its own event loop and avoids Windows asyncio issues.

    Args:
        reactive_resume_url: Base URL of Reactive Resume frontend.
        resume_id: The resume/draft ID to render.
        printer_token: Token for Reactive Resume's printer route access.
        service_token: Internal service token for FastAPI authentication.
        page_format: Page size - "letter" (US) or "a4" (international).
        margin_x: Horizontal margin in points (pt). Defaults to 14pt.
        margin_y: Vertical margin in points (pt). Defaults to 12pt.
        timeout_ms: Maximum time to wait for page load in milliseconds.

    Returns:
        PDF file contents as bytes.

    Raises:
        RuntimeError: If PDF generation fails.
    """
    loop = asyncio.get_event_loop()
    executor = _get_executor()

    try:
        logger.info(
            f"pdf_printer: starting generation for {resume_id} "
            f"(format={page_format}, margins={margin_x}pt x {margin_y}pt)"
        )

        pdf_buffer = await loop.run_in_executor(
            executor,
            _generate_pdf_in_process,
            reactive_resume_url,
            resume_id,
            printer_token,
            service_token,
            page_format,
            margin_x,
            margin_y,
            timeout_ms,
        )

        logger.info(f"pdf_printer: completed for {resume_id}, {len(pdf_buffer)} bytes")
        return pdf_buffer

    except Exception as e:
        logger.error(f"pdf_printer: failed for {resume_id} - {e}")
        raise RuntimeError(f"PDF generation failed: {e}") from e


async def close_browser() -> None:
    """Shutdown the process pool executor.

    Should be called during application shutdown.
    """
    global _executor
    if _executor:
        _executor.shutdown(wait=False)
        _executor = None
    logger.info("pdf_printer: executor shutdown")
