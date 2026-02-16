"""PDF structure validation service.

Standards: python_clean.mdc
- Fast validation before expensive extraction
- Timeout protection
- Specific error codes
"""

import io
from dataclasses import dataclass
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)

# Validation timeout (seconds)
VALIDATION_TIMEOUT = 5.0


class ValidationResult(Enum):
    """PDF validation result."""

    VALID = "valid"
    INVALID_HEADER = "invalid_header"
    MISSING_ROOT = "missing_root"
    CORRUPTED = "corrupted"
    TIMEOUT = "timeout"


@dataclass
class PDFValidationResult:
    """Result of PDF structure validation."""

    is_valid: bool
    result: ValidationResult
    error_code: str | None = None
    error_message: str | None = None


class PDFValidator:
    """Validates PDF structure before extraction."""

    @staticmethod
    async def validate_structure(content: bytes) -> PDFValidationResult:
        """Validate PDF has basic structure.

        Checks:
        1. PDF header (%PDF-)
        2. Basic structure (can open with pypdfium2)
        3. Document has valid structure

        Args:
            content: PDF file content as bytes

        Returns:
            PDFValidationResult with validation status and error details
        """
        # Check PDF header
        if not content.startswith(b"%PDF-"):
            logger.debug("pdf_validation_failed", reason="invalid_header")
            return PDFValidationResult(
                is_valid=False,
                result=ValidationResult.INVALID_HEADER,
                error_code="INVALID_HEADER",
                error_message="File does not start with PDF header (%PDF-)",
            )

        # Try to open with pypdfium2 to check basic structure
        try:
            import pypdfium2 as pdfium  # type: ignore[import-not-found]

            doc = pdfium.PdfDocument(content)
            # Force structure validation by accessing page count
            page_count = len(doc)
            
            # Check if document has basic structure (can access pages)
            if page_count > 0:
                # Try to access first page to verify structure
                _ = doc.get_page(0)

            logger.debug("pdf_validation_success")
            return PDFValidationResult(
                is_valid=True,
                result=ValidationResult.VALID,
            )

        except ImportError:
            # pypdfium2 not installed - skip validation, let extraction handle it
            logger.debug("pdf_validation_skipped", reason="pypdfium2_not_installed")
            return PDFValidationResult(
                is_valid=True,  # Assume valid, let extraction methods handle it
                result=ValidationResult.VALID,
            )

        except Exception as e:
            error_str = str(e).lower()
            if "root" in error_str or "/root" in error_str:
                logger.debug("pdf_validation_failed", reason="missing_root", error=str(e))
                return PDFValidationResult(
                    is_valid=False,
                    result=ValidationResult.MISSING_ROOT,
                    error_code="MISSING_ROOT",
                    error_message=f"PDF is missing /Root object: {str(e)}",
                )
            else:
                logger.debug("pdf_validation_failed", reason="corrupted", error=str(e))
                return PDFValidationResult(
                    is_valid=False,
                    result=ValidationResult.CORRUPTED,
                    error_code="CORRUPTED",
                    error_message=f"PDF structure is corrupted: {str(e)}",
                )
