"""Campaign Pydantic schemas.

Standards: python_clean.mdc
- Request/response validation
- Typed models
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# Campaign status types
CampaignStatusType = Literal["draft", "active", "paused", "completed", "archived"]
CampaignJobStatusType = Literal["pending", "saved", "applied", "rejected", "skipped"]


class CampaignCreate(BaseModel):
    """Request to create a new campaign."""

    name: str = Field(..., min_length=1, max_length=255)
    resume_id: str

    # Search criteria
    target_roles: list[str] = Field(default_factory=list)
    target_locations: list[str] = Field(default_factory=list)
    target_countries: list[str] = Field(default_factory=list)
    target_companies: list[str] = Field(default_factory=list)
    remote_only: bool = False
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    negative_keywords: list[str] = Field(default_factory=list)

    # Behavior settings
    auto_apply: bool = False
    daily_limit: int = Field(10, ge=1, le=100)
    min_match_score: int = Field(70, ge=0, le=100)
    send_per_app_email: bool = False
    cover_letter_template: str | None = None


class CampaignUpdate(BaseModel):
    """Request to update a campaign."""

    name: str | None = Field(None, min_length=1, max_length=255)
    resume_id: str | None = None

    # Search criteria
    target_roles: list[str] | None = None
    target_locations: list[str] | None = None
    target_countries: list[str] | None = None
    target_companies: list[str] | None = None
    remote_only: bool | None = None
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    negative_keywords: list[str] | None = None

    # Behavior settings
    auto_apply: bool | None = None
    daily_limit: int | None = Field(None, ge=1, le=100)
    min_match_score: int | None = Field(None, ge=0, le=100)
    send_per_app_email: bool | None = None
    cover_letter_template: str | None = None


class CampaignStats(BaseModel):
    """Campaign statistics."""

    jobs_found: int
    jobs_applied: int
    interviews: int
    offers: int


class CampaignResponse(BaseModel):
    """Campaign response model."""

    id: str
    user_id: str
    name: str
    resume_id: str

    # Search criteria
    target_roles: list[str]
    target_locations: list[str]
    target_countries: list[str]
    target_companies: list[str]
    remote_only: bool
    salary_min: int | None
    salary_max: int | None
    negative_keywords: list[str]

    # Behavior settings
    auto_apply: bool
    daily_limit: int
    min_match_score: int
    send_per_app_email: bool
    cover_letter_template: str | None

    # Status
    status: CampaignStatusType

    # Statistics
    stats: CampaignStats

    # Timestamps
    created_at: datetime
    updated_at: datetime | None
    completed_at: datetime | None


class CampaignListResponse(BaseModel):
    """List of campaigns response."""

    campaigns: list[CampaignResponse]
    total: int
    has_more: bool


class CampaignJobResponse(BaseModel):
    """Campaign job relationship response."""

    campaign_id: str
    job_id: str
    match_score: int
    adjusted_score: int
    status: CampaignJobStatusType
    rejection_reason: str | None
    created_at: datetime
    applied_at: datetime | None
    rejected_at: datetime | None

    # Job details (populated when fetching)
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    job_url: str | None = None


class CampaignJobListResponse(BaseModel):
    """List of campaign jobs response."""

    jobs: list[CampaignJobResponse]
    total: int
    has_more: bool


class RejectJobRequest(BaseModel):
    """Request to reject a job."""

    reason: str | None = Field(None, max_length=255)
