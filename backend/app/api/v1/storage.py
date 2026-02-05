"""Storage API endpoints.

Standards: python_clean.mdc
- RESTful endpoint design
- Dependency injection
- Proper error handling
- File validation
"""

import time
from typing import Literal

import structlog
from fastapi import APIRouter, Form, HTTPException, Query, UploadFile, status

from app.api.deps import AppSettings, CurrentUser
from app.infra.storage.s3 import S3Storage

logger = structlog.get_logger(__name__)

router = APIRouter()

# File size limits (standardized)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB for all files
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB for images

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

ALLOWED_PDF_TYPES = {
    "application/pdf": "pdf",
}

ALLOWED_CONTENT_TYPES = {**ALLOWED_IMAGE_TYPES, **ALLOWED_PDF_TYPES}


# ============================================================================
# Response Models
# ============================================================================


class FileUploadResponse:
    """File upload response."""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key

    def dict(self):
        return {"url": self.url, "key": self.key}


class FileInfo:
    """File information for list response."""

    def __init__(self, key: str, url: str, lastModified: str):
        self.key = key
        self.url = url
        self.lastModified = lastModified

    def dict(self):
        return {
            "key": self.key,
            "url": self.url,
            "lastModified": self.lastModified,
        }


class FileListResponse:
    """File list response."""

    def __init__(self, files: list[FileInfo]):
        self.files = files

    def dict(self):
        return {"files": [f.dict() for f in self.files]}


class DeleteResponse:
    """Delete response."""

    def __init__(self, deleted: int):
        self.deleted = deleted

    def dict(self):
        return {"deleted": self.deleted}


class HealthResponse:
    """Health check response."""

    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message

    def dict(self):
        return {"status": self.status, "message": self.message}


# ============================================================================
# Helper Functions
# ============================================================================


def _get_storage(settings: AppSettings) -> S3Storage:
    """Get S3 storage instance."""
    return S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )


def _generate_s3_key(
    *,
    user_id: str,
    file_type: Literal["picture", "screenshot", "pdf"],
    resume_id: str | None = None,
) -> str:
    """Generate S3 key based on file type."""
    timestamp = int(time.time() * 1000)  # milliseconds

    if file_type == "picture":
        return f"uploads/{user_id}/pictures/{timestamp}.webp"
    elif file_type == "screenshot":
        if not resume_id:
            raise ValueError("resume_id is required for screenshot uploads")
        return f"uploads/{user_id}/screenshots/{resume_id}/{timestamp}.webp"
    elif file_type == "pdf":
        if not resume_id:
            raise ValueError("resume_id is required for pdf uploads")
        return f"uploads/{user_id}/pdfs/{resume_id}/{timestamp}.pdf"
    else:
        raise ValueError(f"Invalid file_type: {file_type}")


def _validate_file(
    *,
    content: bytes,
    content_type: str,
    file_type: Literal["picture", "screenshot", "pdf"],
) -> None:
    """Validate file content, type, and size."""
    # Validate content type
    if file_type == "picture":
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type for picture. Allowed: {list(ALLOWED_IMAGE_TYPES.keys())}. Got: {content_type}",
            )
        max_size = MAX_IMAGE_SIZE_BYTES
    elif file_type in ("screenshot", "pdf"):
        if file_type == "screenshot":
            if content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type for screenshot. Allowed: {list(ALLOWED_IMAGE_TYPES.keys())}. Got: {content_type}",
                )
        else:  # pdf
            if content_type not in ALLOWED_PDF_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type for PDF. Allowed: {list(ALLOWED_PDF_TYPES.keys())}. Got: {content_type}",
                )
        max_size = MAX_FILE_SIZE_BYTES
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file_type: {file_type}",
        )

    # Validate file size
    if len(content) > max_size:
        size_mb = len(content) / 1024 / 1024
        max_mb = max_size / 1024 / 1024
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {max_mb}MB. Got: {size_mb:.2f}MB",
        )


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    file_type: Literal["picture", "screenshot", "pdf"] = Form(...),
    resume_id: str | None = Form(None),
    user: CurrentUser = None,
    settings: AppSettings = None,
) -> dict:
    """Upload a file (picture, screenshot, or PDF).

    - Pictures: JPEG, PNG, or WebP images, max 5MB
    - Screenshots: JPEG, PNG, or WebP images, max 10MB
    - PDFs: PDF files, max 10MB
    - Returns full public URL and S3 key
    """
    # Validate resume_id for screenshot/pdf
    if file_type in ("screenshot", "pdf") and not resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"resume_id is required for {file_type} uploads",
        )

    # Read file content
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"

    # Validate file
    _validate_file(content=content, content_type=content_type, file_type=file_type)

    # Generate S3 key
    try:
        s3_key = _generate_s3_key(
            user_id=user.id,
            file_type=file_type,
            resume_id=resume_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Upload to S3
    storage = _get_storage(settings)
    try:
        url = await storage.upload(
            key=s3_key,
            data=content,
            content_type=content_type,
        )
    except Exception as e:
        logger.error(
            "file_upload_failed",
            user_id=user.id,
            file_type=file_type,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file",
        )

    logger.info(
        "file_uploaded",
        user_id=user.id,
        file_type=file_type,
        s3_key=s3_key,
        size_bytes=len(content),
        content_type=content_type,
    )

    return FileUploadResponse(url=url, key=s3_key).dict()


@router.get("/files")
async def list_files(
    prefix: str = Query(..., description="S3 key prefix to list files"),
    user: CurrentUser = None,
    settings: AppSettings = None,
) -> dict:
    """List files by prefix.

    Returns list of files with key, URL, and lastModified timestamp.
    Used for screenshot caching in reactive-resume.
    """
    # Ensure prefix is scoped to user's files
    if not prefix.startswith(f"uploads/{user.id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Prefix must start with user's upload directory",
        )

    storage = _get_storage(settings)
    try:
        files_data = await storage.list(prefix=prefix)
    except Exception as e:
        logger.error(
            "file_list_failed",
            user_id=user.id,
            prefix=prefix,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files",
        )

    # Build response with full URLs
    files = []
    for file_data in files_data:
        key = file_data["key"]
        url = f"{settings.s3_endpoint}/{settings.s3_bucket}/{key}"
        files.append(
            FileInfo(
                key=key,
                url=url,
                lastModified=file_data["lastModified"],
            )
        )

    return FileListResponse(files=files).dict()


@router.delete("/files/{key:path}")
async def delete_file(
    key: str,
    user: CurrentUser = None,
    settings: AppSettings = None,
) -> dict:
    """Delete file(s) by S3 key or prefix.

    - If key is a single file, deletes that file
    - If key is a prefix (ends with /) or matches multiple files, deletes all matching files
    - Returns number of files deleted
    """
    # Ensure key is scoped to user's files
    if not key.startswith(f"uploads/{user.id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Key must start with user's upload directory",
        )

    storage = _get_storage(settings)

    # Check if it's a prefix (ends with /) or if multiple files match
    try:
        # Try to list files with this prefix
        files_data = await storage.list(prefix=key)
        if len(files_data) > 1 or (len(files_data) == 1 and key.endswith("/")):
            # It's a prefix, delete all matching files
            deleted_count = await storage.delete_prefix(prefix=key)
        elif len(files_data) == 1:
            # Single file match
            await storage.delete(key=key)
            deleted_count = 1
        else:
            # No files found
            deleted_count = 0
    except Exception as e:
        logger.error(
            "file_delete_failed",
            user_id=user.id,
            key=key,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file(s)",
        )

    logger.info(
        "file_deleted",
        user_id=user.id,
        key=key,
        deleted_count=deleted_count,
    )

    return DeleteResponse(deleted=deleted_count).dict()


@router.get("/health")
async def health_check(settings: AppSettings = None) -> dict:
    """Health check endpoint for storage service."""
    storage = _get_storage(settings)

    try:
        # Try to upload and delete a test file
        test_key = "healthcheck"
        await storage.upload(
            key=test_key,
            data=b"OK",
            content_type="text/plain",
        )
        await storage.delete(key=test_key)

        return HealthResponse(
            status="healthy",
            message="Storage service is accessible and credentials are valid.",
        ).dict()
    except Exception as e:
        logger.error(
            "storage_health_check_failed",
            error=str(e),
            exc_info=True,
        )
        return HealthResponse(
            status="unhealthy",
            message=f"Failed to connect to storage: {str(e)}",
        ).dict()
