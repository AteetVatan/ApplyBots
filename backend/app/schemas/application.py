"""Application schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateApplicationRequest(BaseModel):
    """Request to create a new application."""

    job_id: str
    resume_id: str | None = None  # Uses primary resume if not specified


class ApproveRequest(BaseModel):
    """Request to approve and submit an application."""

    cover_letter: str | None = None  # Override generated cover letter
    answers: dict[str, str] | None = None  # Override generated answers


class EditApplicationRequest(BaseModel):
    """Request to edit application content."""

    cover_letter: str | None = None
    answers: dict[str, str] | None = None


class AuditStepResponse(BaseModel):
    """Audit trail step response."""

    action: str
    selector: str | None
    success: bool
    error_message: str | None
    screenshot_url: str | None
    timestamp: datetime


class ApplicationSummaryResponse(BaseModel):
    """Application summary for list view."""

    id: str
    job_id: str
    job_title: str
    company: str
    status: str
    match_score: int
    created_at: datetime
    submitted_at: datetime | None


class ApplicationDetailResponse(BaseModel):
    """Full application details."""

    id: str
    user_id: str
    job_id: str
    resume_id: str
    status: str
    match_score: int
    match_explanation: dict | None
    cover_letter: str | None
    generated_answers: dict[str, str]
    qc_approved: bool
    qc_feedback: str | None
    audit_trail: list[AuditStepResponse]
    created_at: datetime
    submitted_at: datetime | None
    error_message: str | None

    # Nested job info
    job_title: str
    company: str
    job_url: str


class ApplicationListResponse(BaseModel):
    """Paginated application list response."""

    items: list[ApplicationSummaryResponse]
    total: int
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    has_more: bool
