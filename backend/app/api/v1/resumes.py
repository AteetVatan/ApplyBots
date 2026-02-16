"""Resume management API endpoints.

Standards: python_clean.mdc
- FastAPI router
- Pydantic response models
- Proper error handling
"""

from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.domain.resume import ParsedResume
from app.core.exceptions import ExtractionError, ExtractionFailedError, PDFCorruptedError
from app.infra.db.models import UserModel
from app.infra.db.repositories.resume import SQLResumeRepository
from app.infra.services.resume_service import MIN_TEXT_THRESHOLD, ResumeService
from app.infra.storage.s3 import S3Storage
from app.config import get_settings

router = APIRouter()


# Response models
class ParsedResumeResponse(BaseModel):
    """Parsed resume data response."""

    full_name: str | None
    email: str | None
    phone: str | None
    location: str | None
    skills: list[str]
    total_years_experience: float | None


class ResumeResponse(BaseModel):
    """Resume response model."""

    id: str
    filename: str
    is_primary: bool
    parsed_data: ParsedResumeResponse | None
    created_at: datetime
    extraction_status: Literal["success", "partial", "failed", "pending_ocr"] | None = None
    extraction_warnings: list[str] | None = None
    extraction_method: str | None = None


class ResumeListResponse(BaseModel):
    """Resume list response."""

    items: list[ResumeResponse]
    total: int


class ExtractionErrorResponse(BaseModel):
    """Error response for extraction failures."""

    error_code: str
    message: str
    details: dict[str, Any] | None = None
    guidance: list[str] = []


def _parsed_to_response(parsed: ParsedResume | None) -> ParsedResumeResponse | None:
    """Convert domain ParsedResume to response model."""
    if not parsed:
        return None
    return ParsedResumeResponse(
        full_name=parsed.full_name,
        email=parsed.email,
        phone=parsed.phone,
        location=parsed.location,
        skills=parsed.skills or [],
        total_years_experience=parsed.total_years_experience,
    )


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResumeListResponse:
    """List all resumes for the current user."""
    resume_repo = SQLResumeRepository(session=db)
    resumes = await resume_repo.get_by_user_id(current_user.id)

    return ResumeListResponse(
        items=[
            ResumeResponse(
                id=r.id,
                filename=r.filename,
                is_primary=r.is_primary,
                parsed_data=_parsed_to_response(r.parsed_data),
                created_at=r.created_at,
            )
            for r in resumes
        ],
        total=len(resumes),
    )


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
) -> ResumeResponse:
    """Upload and parse a new resume."""
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content_type = file.content_type or ""
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {content_type}. Only PDF and DOCX are allowed.",
        )

    # Read file content
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    # Initialize services
    settings = get_settings()
    storage = S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )
    resume_repo = SQLResumeRepository(session=db)
    resume_service = ResumeService(
        storage=storage,
        resume_repository=resume_repo,
    )

    # Upload and parse
    try:
        resume, extraction_metadata = await resume_service.upload_and_parse(
            user_id=current_user.id,
            filename=file.filename,
            content=content,
            content_type=content_type,
        )

        await db.commit()

        # Compute extraction status from raw_text and extraction_error
        extraction_status: Literal["success", "partial", "failed", "pending_ocr"] | None = None
        if resume.extraction_error:
            # Text extraction failed, but file was saved - mark as pending OCR
            extraction_status = "pending_ocr"
        elif resume.raw_text:
            text_length = len(resume.raw_text.strip())
            if text_length >= MIN_TEXT_THRESHOLD:
                extraction_status = "success"
            elif text_length > 0:
                extraction_status = "partial"
            else:
                extraction_status = "failed"
        else:
            extraction_status = "failed"

        # Build warnings list - include extraction_error if present
        warnings = extraction_metadata.get("extraction_warnings") or []
        if resume.extraction_error:
            warnings.append(f"Text extraction failed: {resume.extraction_error}")

        return ResumeResponse(
            id=resume.id,
            filename=resume.filename,
            is_primary=resume.is_primary,
            parsed_data=_parsed_to_response(resume.parsed_data),
            created_at=resume.created_at,
            extraction_status=extraction_status,
            extraction_warnings=warnings if warnings else None,
            extraction_method=extraction_metadata.get("extraction_method"),
        )

    except PDFCorruptedError as e:
        await db.rollback()
        error_response = ExtractionErrorResponse(
            error_code=e.code,
            message=e.message,
            details={"details": e.details} if e.details else None,
            guidance=[
                "Try re-exporting the PDF from the original source",
                "Use a PDF repair tool (Adobe Acrobat, iLovePDF, PDF2Go)",
                "Open PDF in Chrome/Edge and save as PDF again",
                "If you have the original document, upload as DOCX instead",
            ],
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_response.model_dump(),
        )

    except ExtractionError as e:
        await db.rollback()
        error_response = ExtractionErrorResponse(
            error_code=e.code,
            message=e.message,
            guidance=["Please try again or contact support if the issue persists"],
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_response.model_dump(),
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during resume upload",
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResumeResponse:
    """Get a specific resume."""
    resume_repo = SQLResumeRepository(session=db)
    resume = await resume_repo.get_by_id(resume_id)

    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    return ResumeResponse(
        id=resume.id,
        filename=resume.filename,
        is_primary=resume.is_primary,
        parsed_data=_parsed_to_response(resume.parsed_data),
        created_at=resume.created_at,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_resume(
    resume_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a resume."""
    resume_repo = SQLResumeRepository(session=db)
    resume = await resume_repo.get_by_id(resume_id)

    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete from storage
    settings = get_settings()
    storage = S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )
    await storage.delete(key=resume.s3_key)

    # Delete from database
    await resume_repo.delete(resume_id)
    await db.commit()


@router.post("/{resume_id}/set-primary", response_model=ResumeResponse)
async def set_primary_resume(
    resume_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResumeResponse:
    """Set a resume as the primary resume."""
    resume_repo = SQLResumeRepository(session=db)

    # Get the resume
    resume = await resume_repo.get_by_id(resume_id)
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get all user resumes and unset primary
    all_resumes = await resume_repo.get_by_user_id(current_user.id)
    for r in all_resumes:
        if r.is_primary:
            r.is_primary = False
            await resume_repo.update(r)

    # Set new primary
    resume.is_primary = True
    await resume_repo.update(resume)
    await db.commit()

    return ResumeResponse(
        id=resume.id,
        filename=resume.filename,
        is_primary=resume.is_primary,
        parsed_data=_parsed_to_response(resume.parsed_data),
        created_at=resume.created_at,
    )
