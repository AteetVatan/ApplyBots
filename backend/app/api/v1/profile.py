"""Profile endpoints.

Standards: python_clean.mdc
- Thin controller layer
- Proper error handling
"""

import structlog
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from typing import Any, Literal

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.exceptions import ExtractionError, ExtractionFailedError, PDFCorruptedError, ResourceNotFoundError
from pydantic import BaseModel
from app.schemas.profile import (
    PreferencesResponse,
    PreferencesUpdate,
    ProfileResponse,
    ProfileUpdate,
    ResumeResponse,
)

router = APIRouter()
logger = structlog.get_logger()


class ExtractionErrorResponse(BaseModel):
    """Error response for extraction failures."""

    error_code: str
    message: str
    details: dict[str, Any] | None = None
    guidance: list[str] = []


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: CurrentUser,
    db: DBSession,
) -> ProfileResponse:
    """Get current user's profile."""
    from app.infra.db.repositories.profile import SQLProfileRepository

    profile_repo = SQLProfileRepository(session=db)
    profile = await profile_repo.get_by_user_id(current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        headline=profile.headline,
        location=profile.location,
        phone=profile.phone,
        linkedin_url=profile.linkedin_url,
        portfolio_url=profile.portfolio_url,
        preferences=PreferencesResponse(
            target_roles=profile.preferences.target_roles,
            target_locations=profile.preferences.target_locations,
            remote_only=profile.preferences.remote_only,
            salary_min=profile.preferences.salary_min,
            salary_max=profile.preferences.salary_max,
            negative_keywords=profile.preferences.negative_keywords,
            experience_years=profile.preferences.experience_years,
        ),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> ProfileResponse:
    """Update current user's profile."""
    from app.infra.db.repositories.profile import SQLProfileRepository

    profile_repo = SQLProfileRepository(session=db)
    profile = await profile_repo.get_by_user_id(current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Update fields
    if request.full_name is not None:
        profile.full_name = request.full_name
    if request.headline is not None:
        profile.headline = request.headline
    if request.location is not None:
        profile.location = request.location
    if request.phone is not None:
        profile.phone = request.phone
    if request.linkedin_url is not None:
        profile.linkedin_url = str(request.linkedin_url)
    if request.portfolio_url is not None:
        profile.portfolio_url = str(request.portfolio_url)

    updated = await profile_repo.update(profile)

    logger.info("profile_updated", user_id=current_user.id)

    return ProfileResponse(
        id=updated.id,
        user_id=updated.user_id,
        full_name=updated.full_name,
        headline=updated.headline,
        location=updated.location,
        phone=updated.phone,
        linkedin_url=updated.linkedin_url,
        portfolio_url=updated.portfolio_url,
        preferences=PreferencesResponse(
            target_roles=updated.preferences.target_roles,
            target_locations=updated.preferences.target_locations,
            remote_only=updated.preferences.remote_only,
            salary_min=updated.preferences.salary_min,
            salary_max=updated.preferences.salary_max,
            negative_keywords=updated.preferences.negative_keywords,
            experience_years=updated.preferences.experience_years,
        ),
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(
    request: PreferencesUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> PreferencesResponse:
    """Update job search preferences."""
    from app.infra.db.repositories.profile import SQLProfileRepository

    profile_repo = SQLProfileRepository(session=db)
    profile = await profile_repo.get_by_user_id(current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Update preferences
    if request.target_roles is not None:
        profile.preferences.target_roles = request.target_roles
    if request.target_locations is not None:
        profile.preferences.target_locations = request.target_locations
    if request.remote_only is not None:
        profile.preferences.remote_only = request.remote_only
    if request.salary_min is not None:
        profile.preferences.salary_min = request.salary_min
    if request.salary_max is not None:
        profile.preferences.salary_max = request.salary_max
    if request.negative_keywords is not None:
        profile.preferences.negative_keywords = request.negative_keywords
    if request.experience_years is not None:
        profile.preferences.experience_years = request.experience_years

    await profile_repo.update(profile)

    logger.info("preferences_updated", user_id=current_user.id)

    return PreferencesResponse(
        target_roles=profile.preferences.target_roles,
        target_locations=profile.preferences.target_locations,
        remote_only=profile.preferences.remote_only,
        salary_min=profile.preferences.salary_min,
        salary_max=profile.preferences.salary_max,
        negative_keywords=profile.preferences.negative_keywords,
        experience_years=profile.preferences.experience_years,
    )


@router.post("/resumes", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    db: DBSession = None,
    settings: AppSettings = None,
) -> ResumeResponse:
    """Upload a resume file."""
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported",
        )

    try:
        from app.infra.db.repositories.resume import SQLResumeRepository
        from app.infra.services.resume_service import ResumeService
        from app.infra.storage.s3 import S3Storage
    except ImportError as e:
        logger.warning("storage_service_not_available", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available. Please try again later.",
        )

    # Read file content
    content = await file.read()

    # Initialize services
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

    try:
        resume, extraction_metadata = await resume_service.upload_and_parse(
            user_id=current_user.id,
            filename=file.filename or "resume",
            content=content,
            content_type=file.content_type,
        )

        logger.info("resume_uploaded", user_id=current_user.id, resume_id=resume.id)

        parsed_response = None
        if resume.parsed_data:
            from app.schemas.profile import ParsedResumeResponse
            parsed_response = ParsedResumeResponse(
                full_name=resume.parsed_data.full_name,
                email=resume.parsed_data.email,
                phone=resume.parsed_data.phone,
                location=resume.parsed_data.location,
                summary=resume.parsed_data.summary,
                skills=resume.parsed_data.skills,
                total_years_experience=resume.parsed_data.total_years_experience,
            )

        # Compute extraction status from raw_text and extraction_error
        from app.infra.services.resume_service import MIN_TEXT_THRESHOLD

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
            parsed_data=parsed_response,
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
        logger.error("resume_upload_unexpected_error", user_id=current_user.id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during resume upload",
        )


@router.get("/resumes", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: CurrentUser,
    db: DBSession,
) -> list[ResumeResponse]:
    """List all resumes for current user."""
    from app.infra.db.repositories.resume import SQLResumeRepository

    resume_repo = SQLResumeRepository(session=db)
    resumes = await resume_repo.get_by_user_id(current_user.id)

    result = []
    for resume in resumes:
        parsed_response = None
        if resume.parsed_data:
            from app.schemas.profile import ParsedResumeResponse
            parsed_response = ParsedResumeResponse(
                full_name=resume.parsed_data.full_name,
                email=resume.parsed_data.email,
                phone=resume.parsed_data.phone,
                location=resume.parsed_data.location,
                summary=resume.parsed_data.summary,
                skills=resume.parsed_data.skills,
                total_years_experience=resume.parsed_data.total_years_experience,
            )

        result.append(ResumeResponse(
            id=resume.id,
            filename=resume.filename,
            is_primary=resume.is_primary,
            parsed_data=parsed_response,
            created_at=resume.created_at,
        ))

    return result


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_resume(
    resume_id: str,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> None:
    """Delete a resume."""
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.storage.s3 import S3Storage

    resume_repo = SQLResumeRepository(session=db)
    resume = await resume_repo.get_by_id(resume_id)

    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # Delete from storage
    storage = S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )

    try:
        await storage.delete(key=resume.s3_key)
    except Exception as e:
        logger.warning("storage_delete_failed", key=resume.s3_key, error=str(e))

    await resume_repo.delete(resume_id)

    logger.info("resume_deleted", user_id=current_user.id, resume_id=resume_id)
