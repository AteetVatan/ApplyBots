"""Resume processing service.

Standards: python_clean.mdc
- Coordinates storage and parsing
- Generates embeddings for semantic search
- Multi-library PDF extraction with AI fallback

Extraction Flow:
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│   pypdf     │ → │ pdfplumber   │ → │ pdfminer    │
│ (BSD-3, $0) │   │ (MIT, $0)    │   │ (MIT, $0)   │
└─────────────┘   └──────────────┘   └─────────────┘
                          │
                          ▼
                ┌─────────────────┐   ┌──────────────────┐
                │ Tesseract OCR   │ → │ Together Vision  │
                │ (Apache, $0)    │   │ (~$0.002/resume) │
                └─────────────────┘   └──────────────────┘
"""

import base64
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

# Minimum text length threshold for valid extraction
MIN_TEXT_THRESHOLD = 50

# Vision OCR prompt for resume text extraction
VISION_OCR_PROMPT = """Extract ALL text from this resume image exactly as written.
Preserve the structure and formatting.
Include: name, contact info, work experience, education, skills, and any other sections.
Return ONLY the extracted text, no commentary or explanations."""


class ExtractionMethod(Enum):
    """Method used to extract text from PDF."""

    NATIVE = "native"  # pypdf, pdfplumber, or pdfminer
    OCR = "ocr"  # Local Tesseract OCR
    VISION_AI = "vision_ai"  # Together AI Vision model
    FAILED = "failed"


@dataclass
class PDFExtractionResult:
    """Result of PDF text extraction with metadata."""

    text: str
    method: ExtractionMethod
    page_count: int
    is_encrypted: bool = False
    ocr_available: bool = True
    extraction_library: str | None = None  # Which library succeeded (pypdf, pdfplumber, etc)
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
        """Extract text from PDF using multi-library fallback chain.

        Strategy:
        1. pypdf - Fast, lightweight extraction
        2. pdfplumber - Good for structured documents
        3. pdfminer.six - Handles complex layouts
        4. Local Tesseract OCR - For scanned PDFs
        5. Together AI Vision - AI fallback for problematic PDFs
        """
        result = await self._extract_pdf_with_metadata(content)

        logger.info(
            "pdf_extraction_complete",
            method=result.method.value,
            extraction_library=result.extraction_library,
            page_count=result.page_count,
            text_length=len(result.text),
            is_encrypted=result.is_encrypted,
            ocr_available=result.ocr_available,
            error=result.error_message,
        )

        return result.text

    async def _extract_pdf_with_metadata(self, content: bytes) -> PDFExtractionResult:
        """Extract text from PDF using multi-library fallback chain with AI fallback.

        Extraction priority (MIT-compatible):
        1. pypdf - Fast, lightweight (BSD-3-Clause)
        2. pdfplumber - Good for structured text (MIT)
        3. pdfminer.six - Handles complex layouts (MIT)
        4. Local Tesseract OCR - For scanned PDFs (Apache 2.0)
        5. Together AI Vision - AI fallback for problematic PDFs
        """
        page_count = 0
        has_images = False

        # Method 1: Try pypdf (fastest, most lightweight)
        text, page_count = await self._try_pypdf(content)
        if text and len(text) >= MIN_TEXT_THRESHOLD:
            logger.info("pypdf_extraction_success", text_length=len(text))
            return PDFExtractionResult(
                text=text,
                method=ExtractionMethod.NATIVE,
                page_count=page_count,
                extraction_library="pypdf",
            )

        # Method 2: Try pdfplumber (good for structured documents)
        text, page_count, has_images = await self._try_pdfplumber(content)
        if text and len(text) >= MIN_TEXT_THRESHOLD:
            logger.info("pdfplumber_extraction_success", text_length=len(text))
            return PDFExtractionResult(
                text=text,
                method=ExtractionMethod.NATIVE,
                page_count=page_count,
                extraction_library="pdfplumber",
            )

        # Method 3: Try pdfminer.six (handles complex layouts)
        text = await self._try_pdfminer(content)
        if text and len(text) >= MIN_TEXT_THRESHOLD:
            logger.info("pdfminer_extraction_success", text_length=len(text))
            return PDFExtractionResult(
                text=text,
                method=ExtractionMethod.NATIVE,
                page_count=page_count or 1,
                extraction_library="pdfminer",
            )

        # Check OCR availability
        ocr_available = self._is_tesseract_available()

        # Method 4: Try local Tesseract OCR (free, if available)
        if ocr_available:
            ocr_text = await self._attempt_ocr_extraction(content)
            if ocr_text and len(ocr_text) >= MIN_TEXT_THRESHOLD:
                logger.info("tesseract_ocr_success", text_length=len(ocr_text))
                return PDFExtractionResult(
                    text=ocr_text,
                    method=ExtractionMethod.OCR,
                    page_count=page_count or 1,
                    ocr_available=True,
                    extraction_library="tesseract",
                )

        # Method 5: Try Together AI Vision OCR (paid fallback)
        vision_text = await self._extract_with_vision_ocr(content)
        if vision_text and len(vision_text) >= MIN_TEXT_THRESHOLD:
            logger.info("vision_ai_ocr_success", text_length=len(vision_text))
            return PDFExtractionResult(
                text=vision_text,
                method=ExtractionMethod.VISION_AI,
                page_count=page_count or 1,
                ocr_available=ocr_available,
                extraction_library="together_vision",
            )

        # All methods failed - build specific error message
        if has_images and not ocr_available:
            error_msg = (
                "PDF appears to be scanned/image-based but local OCR is unavailable. "
                "AI extraction was attempted but could not extract sufficient text."
            )
        elif has_images:
            error_msg = "PDF is scanned/image-based. All extraction methods failed."
        else:
            error_msg = "No text could be extracted from PDF using any available method."

        logger.warning(
            "all_extraction_methods_failed",
            page_count=page_count,
            has_images=has_images,
            ocr_available=ocr_available,
        )

        return PDFExtractionResult(
            text="",
            method=ExtractionMethod.FAILED,
            page_count=page_count or 0,
            ocr_available=ocr_available,
            error_message=error_msg,
        )

    async def _try_pypdf(self, content: bytes) -> tuple[str, int]:
        """Try text extraction using pypdf (BSD-3-Clause license).

        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            from pypdf import PdfReader  # type: ignore[import-not-found]

            pdf = PdfReader(io.BytesIO(content))
            page_count = len(pdf.pages)
            text_parts: list[str] = []

            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)

            text = "\n".join(text_parts).strip()
            return text, page_count

        except ImportError:
            logger.debug("pypdf_not_installed")
            return "", 0
        except Exception as e:
            logger.debug("pypdf_extraction_failed", error=str(e))
            return "", 0

    async def _try_pdfplumber(self, content: bytes) -> tuple[str, int, bool]:
        """Try text extraction using pdfplumber (MIT license).

        Returns:
            Tuple of (extracted_text, page_count, has_images)
        """
        try:
            import pdfplumber  # type: ignore[import-not-found]

            pdf = pdfplumber.open(io.BytesIO(content))
            page_count = len(pdf.pages)
            text_parts: list[str] = []
            has_images = False

            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)

                # Check if page has images (potential scanned content)
                if not page_text.strip() and page.images:
                    has_images = True

            pdf.close()
            text = "\n".join(text_parts).strip()
            return text, page_count, has_images

        except ImportError:
            logger.debug("pdfplumber_not_installed")
            return "", 0, False
        except Exception as e:
            error_str = str(e).lower()
            if "password" in error_str or "encrypt" in error_str:
                logger.warning("pdf_encrypted", error=str(e))
            else:
                logger.debug("pdfplumber_extraction_failed", error=str(e))
            return "", 0, False

    async def _try_pdfminer(self, content: bytes) -> str:
        """Try text extraction using pdfminer.six (MIT license).

        Handles complex PDF layouts better than other libraries.
        """
        try:
            from pdfminer.high_level import extract_text  # type: ignore[import-not-found]

            text = extract_text(io.BytesIO(content)).strip()
            return text

        except ImportError:
            logger.debug("pdfminer_not_installed")
            return ""
        except Exception as e:
            logger.debug("pdfminer_extraction_failed", error=str(e))
            return ""

    async def _extract_with_vision_ocr(self, content: bytes) -> str:
        """Extract text from PDF using Together AI Vision model.

        Converts PDF pages to images and uses Llama Vision for text extraction.
        This is a paid fallback used when all local methods fail.

        Cost: ~$0.002 per 2-page resume with Llama-3.2-11B-Vision-Instruct-Turbo.

        Returns:
            Extracted text from all pages, or empty string on failure.
        """
        try:
            from pdf2image import convert_from_bytes  # type: ignore[import-not-found]
        except ImportError:
            logger.warning("pdf2image_not_installed_for_vision_ocr")
            return ""

        # Get Together AI client
        try:
            from app.config import get_settings
            from app.infra.llm.together_client import TogetherLLMClient
            from app.agents.config import Models

            settings = get_settings()
            vision_client = TogetherLLMClient(
                api_key=settings.together_api_key.get_secret_value(),
                timeout=60.0,
            )
        except Exception as e:
            logger.warning("vision_client_init_failed", error=str(e))
            return ""

        try:
            # Convert PDF to images at 200 DPI (balance between quality and cost)
            images = convert_from_bytes(content, dpi=200)

            logger.info(
                "vision_ocr_started",
                page_count=len(images),
                model=Models.LLAMA_VISION_11B,
            )

            text_parts: list[str] = []

            for page_num, image in enumerate(images):
                try:
                    # Convert PIL Image to base64
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    image_b64 = base64.b64encode(buffer.getvalue()).decode()

                    # Call Together AI Vision model
                    page_text = await vision_client.complete_vision(
                        image_base64=image_b64,
                        prompt=VISION_OCR_PROMPT,
                        model=Models.LLAMA_VISION_11B,
                        temperature=0.1,
                        max_tokens=4096,
                    )

                    text_parts.append(page_text)

                    logger.debug(
                        "vision_ocr_page_complete",
                        page_num=page_num,
                        text_length=len(page_text),
                    )

                except Exception as e:
                    logger.warning(
                        "vision_ocr_page_failed",
                        page_num=page_num,
                        error=str(e),
                    )
                    text_parts.append("")

            combined_text = "\n\n".join(text_parts).strip()

            logger.info(
                "vision_ocr_complete",
                page_count=len(images),
                total_text_length=len(combined_text),
            )

            return combined_text

        except Exception as e:
            logger.warning("vision_ocr_extraction_failed", error=str(e))
            return ""

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
