"""Resume processing service.

Standards: python_clean.mdc
- Coordinates storage and parsing
- Generates embeddings for semantic search
"""

import io
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import structlog

from app.core.domain.resume import ParsedResume, Resume
from app.core.ports.llm import LLMClient
from app.core.ports.repositories import ResumeRepository
from app.core.ports.storage import FileStorage
from app.core.ports.vector_store import VectorStore

logger = structlog.get_logger(__name__)

# Collection name for resume embeddings
RESUMES_COLLECTION = "resumes"


class ExtractionMethod(Enum):
    """Method used to extract text from PDF."""

    NATIVE = "native"
    OCR = "ocr"
    FAILED = "failed"


@dataclass
class PDFExtractionResult:
    """Result of PDF text extraction with metadata."""

    text: str
    method: ExtractionMethod
    page_count: int
    is_encrypted: bool = False
    ocr_available: bool = True
    error_message: str | None = None


class ResumeService:
    """Service for resume upload and parsing."""

    def __init__(
        self,
        *,
        storage: FileStorage,
        resume_repository: ResumeRepository,
        llm_client: LLMClient | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self._storage = storage
        self._resume_repo = resume_repository
        self._llm_client = llm_client
        self._vector_store = vector_store

    async def upload_and_parse(
        self,
        *,
        user_id: str,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> Resume:
        """Upload resume and parse its content."""
        resume_id = str(uuid.uuid4())
        s3_key = f"resumes/{user_id}/{resume_id}/{filename}"

        # Upload to storage
        await self._storage.upload(
            key=s3_key,
            data=content,
            content_type=content_type,
        )

        # Extract text based on file type
        raw_text = await self._extract_text(content=content, content_type=content_type)

        # Parse resume text
        parsed_data = await self._parse_resume_text(raw_text) if raw_text else None

        # Generate embedding for semantic search
        embedding = None
        if raw_text and self._llm_client:
            try:
                # Truncate text for embedding (8k chars max for most models)
                embed_text = raw_text[:8000]
                embedding = await self._llm_client.embed(text=embed_text)

                logger.info(
                    "resume_embedding_generated",
                    resume_id=resume_id,
                    text_length=len(embed_text),
                    embedding_dim=len(embedding),
                )

                # Store in vector database for semantic search
                if self._vector_store:
                    await self._vector_store.add_embedding(
                        collection=RESUMES_COLLECTION,
                        doc_id=resume_id,
                        embedding=embedding,
                        metadata={
                            "user_id": user_id,
                            "filename": filename,
                        },
                    )
                    logger.info(
                        "resume_stored_in_vector_db",
                        resume_id=resume_id,
                        collection=RESUMES_COLLECTION,
                    )

            except Exception as e:
                logger.warning(
                    "resume_embedding_failed",
                    resume_id=resume_id,
                    error=str(e),
                )
                # Continue without embedding - not critical

        # Check if this is the first resume (make it primary)
        existing = await self._resume_repo.get_by_user_id(user_id)
        is_primary = len(existing) == 0

        # Create resume record
        resume = Resume(
            id=resume_id,
            user_id=user_id,
            filename=filename,
            s3_key=s3_key,
            raw_text=raw_text,
            parsed_data=parsed_data,
            embedding=embedding,
            is_primary=is_primary,
            created_at=datetime.utcnow(),
        )

        return await self._resume_repo.create(resume)

    async def _extract_text(
        self,
        *,
        content: bytes,
        content_type: str,
    ) -> str | None:
        """Extract text from resume file."""
        file_size = len(content)
        logger.info(
            "text_extraction_started",
            content_type=content_type,
            file_size_bytes=file_size,
        )

        try:
            if content_type == "application/pdf":
                text = await self._extract_pdf_text(content)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = await self._extract_docx_text(content)
            else:
                logger.warning("unsupported_content_type", content_type=content_type)
                return None

            if text:
                logger.info(
                    "text_extraction_succeeded",
                    content_type=content_type,
                    text_length=len(text),
                )
            else:
                logger.warning(
                    "text_extraction_empty",
                    content_type=content_type,
                )

            return text if text else None

        except Exception as e:
            logger.error(
                "text_extraction_failed",
                content_type=content_type,
                error=str(e),
                exc_info=True,
            )
            return None

    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF using pdfplumber with OCR fallback.

        Strategy:
        1. Try native text extraction (fast, works for text-based PDFs)
        2. If empty/insufficient, check for images and attempt OCR
        3. Log extraction method and any issues for debugging
        """
        result = await self._extract_pdf_with_metadata(content)

        logger.info(
            "pdf_extraction_complete",
            method=result.method.value,
            page_count=result.page_count,
            text_length=len(result.text),
            is_encrypted=result.is_encrypted,
            ocr_available=result.ocr_available,
            error=result.error_message,
        )

        return result.text

    async def _extract_pdf_with_metadata(self, content: bytes) -> PDFExtractionResult:
        """Extract text from PDF with detailed metadata about the extraction."""
        try:
            import pdfplumber  # type: ignore[import-not-found]
        except ImportError:
            logger.error("pdfplumber_not_installed")
            return PDFExtractionResult(
                text="",
                method=ExtractionMethod.FAILED,
                page_count=0,
                error_message="pdfplumber not installed",
            )

        try:
            pdf = pdfplumber.open(io.BytesIO(content))
        except Exception as e:
            # pdfplumber raises exception for encrypted PDFs it cannot open
            error_str = str(e).lower()
            if "password" in error_str or "encrypt" in error_str:
                logger.warning("pdf_encrypted", error=str(e))
                return PDFExtractionResult(
                    text="",
                    method=ExtractionMethod.FAILED,
                    page_count=0,
                    is_encrypted=True,
                    error_message="PDF is password-protected",
                )
            logger.warning("pdf_open_failed", error=str(e))
            return PDFExtractionResult(
                text="",
                method=ExtractionMethod.FAILED,
                page_count=0,
                error_message=f"Failed to open PDF: {e}",
            )

        page_count = len(pdf.pages)

        # First pass: native text extraction
        text_parts: list[str] = []
        has_images = False

        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

            # Check if page has images (potential scanned content)
            if not page_text.strip():
                if page.images:
                    has_images = True

        pdf.close()
        native_text = "\n".join(text_parts).strip()

        # If we got sufficient text, return it
        if len(native_text) >= 50:  # Minimum threshold for valid content
            return PDFExtractionResult(
                text=native_text,
                method=ExtractionMethod.NATIVE,
                page_count=page_count,
            )

        # Check OCR availability upfront for better error messages
        ocr_available = self._is_tesseract_available()

        # If native extraction failed and there are images, try OCR
        if has_images or not native_text:
            if ocr_available:
                ocr_text = await self._attempt_ocr_extraction(content)
                if ocr_text and len(ocr_text) > len(native_text):
                    return PDFExtractionResult(
                        text=ocr_text,
                        method=ExtractionMethod.OCR,
                        page_count=page_count,
                        ocr_available=True,
                    )
            else:
                logger.warning(
                    "ocr_unavailable_scanned_pdf",
                    has_images=has_images,
                    native_text_length=len(native_text),
                )

        # Return whatever we have (even if empty)
        if native_text:
            return PDFExtractionResult(
                text=native_text,
                method=ExtractionMethod.NATIVE,
                page_count=page_count,
                ocr_available=ocr_available,
            )

        # Build specific error message based on what failed
        if has_images and not ocr_available:
            error_msg = (
                "PDF appears to be scanned/image-based but OCR is unavailable. "
                "Install Tesseract OCR or upload a text-based PDF."
            )
        elif has_images:
            error_msg = "PDF is scanned/image-based and OCR could not extract text."
        else:
            error_msg = "No text could be extracted from PDF."

        return PDFExtractionResult(
            text="",
            method=ExtractionMethod.FAILED,
            page_count=page_count,
            ocr_available=ocr_available,
            error_message=error_msg,
        )

    async def _attempt_ocr_extraction(self, content: bytes) -> str:
        """Attempt OCR extraction on PDF pages using pdf2image.

        Renders each page as a high-resolution image and runs Tesseract OCR.
        Requires Tesseract and poppler-utils to be installed on the system.
        Returns empty string if OCR is not available or fails.
        """
        # Check if Tesseract is available
        if not self._is_tesseract_available():
            logger.info("ocr_skipped_tesseract_not_available")
            return ""

        try:
            from pdf2image import convert_from_bytes  # type: ignore[import-not-found]
        except ImportError:
            logger.warning("pdf2image_not_installed")
            return ""

        try:
            # Convert PDF pages to images at 300 DPI for OCR
            images = convert_from_bytes(content, dpi=300)

            text_parts: list[str] = []
            for page_num, image in enumerate(images):
                try:
                    ocr_text = self._ocr_image(image)

                    if ocr_text:
                        logger.debug(
                            "ocr_page_success",
                            page_num=page_num,
                            text_length=len(ocr_text),
                        )

                    text_parts.append(ocr_text)
                except Exception as e:
                    logger.warning(
                        "ocr_page_failed",
                        page_num=page_num,
                        error=str(e),
                    )
                    text_parts.append("")

            return "\n".join(text_parts).strip()

        except Exception as e:
            logger.warning("ocr_extraction_failed", error=str(e))
            return ""

    def _ocr_image(self, image: "Image.Image") -> str:  # type: ignore[name-defined]
        """Run OCR on a PIL Image using pytesseract."""
        try:
            import pytesseract  # type: ignore[import-not-found]

            # Run OCR
            text: str = pytesseract.image_to_string(image)
            return text

        except ImportError:
            logger.debug("pytesseract_not_available")
            return ""
        except Exception as e:
            logger.warning("ocr_image_failed", error=str(e))
            return ""

    def _is_tesseract_available(self) -> bool:
        """Check if Tesseract OCR is available on the system."""
        try:
            import shutil

            return shutil.which("tesseract") is not None
        except Exception:
            return False

    async def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX."""
        try:
            from docx import Document

            doc = Document(io.BytesIO(content))
            text_parts: list[str] = []

            for para in doc.paragraphs:
                text_parts.append(para.text)

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_parts.append(cell.text)

            text = "\n".join(text_parts)

            logger.info(
                "docx_extraction_complete",
                paragraph_count=len(doc.paragraphs),
                table_count=len(doc.tables),
                text_length=len(text),
            )

            return text

        except ImportError:
            logger.error("python_docx_not_installed")
            return ""
        except Exception as e:
            logger.warning("docx_extraction_failed", error=str(e))
            return ""

    async def _parse_resume_text(self, text: str) -> ParsedResume:
        """Parse resume text into structured data.

        This is a simplified parser. In production, use LLM for better parsing.
        """
        lines = text.split("\n")
        skills: list[str] = []

        # Simple skill extraction (look for common patterns)
        skill_keywords = [
            "python", "javascript", "typescript", "react", "node.js", "aws",
            "docker", "kubernetes", "sql", "postgresql", "mongodb", "redis",
            "fastapi", "django", "flask", "git", "linux", "api", "rest",
        ]

        text_lower = text.lower()
        for keyword in skill_keywords:
            if keyword in text_lower:
                skills.append(keyword.title() if len(keyword) > 3 else keyword.upper())

        # Extract email
        import re
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        email = email_match.group(0) if email_match else None

        # Extract phone
        phone_match = re.search(r"[\+]?[\d\s\-\(\)]{10,}", text)
        phone = phone_match.group(0).strip() if phone_match else None

        # First non-empty line is often the name
        full_name = None
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) < 50 and "@" not in stripped:
                full_name = stripped
                break

        return ParsedResume(
            full_name=full_name,
            email=email,
            phone=phone,
            skills=skills,
            total_years_experience=None,  # Would need more sophisticated parsing
        )
