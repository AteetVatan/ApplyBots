"""Job schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime

from pydantic import BaseModel, Field


class JobFilters(BaseModel):
    """Job search filters."""

    query: str | None = None
    location: str | None = None
    remote_only: bool = False
    salary_min: int | None = Field(None, ge=0)
    min_match_score: int | None = Field(None, ge=0, le=100)


class JobRequirementsResponse(BaseModel):
    """Job requirements response."""

    required_skills: list[str]
    preferred_skills: list[str]
    experience_years_min: int | None
    experience_years_max: int | None
    education_level: str | None


class JobSummaryResponse(BaseModel):
    """Job summary for list view."""

    id: str
    title: str
    company: str
    location: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    match_score: int | None
    posted_at: datetime | None


class JobDetailResponse(BaseModel):
    """Full job details."""

    id: str
    external_id: str
    title: str
    company: str
    location: str | None
    description: str
    url: str
    source: str
    remote: bool
    salary_min: int | None
    salary_max: int | None
    salary_currency: str
    requirements: JobRequirementsResponse
    match_score: int | None
    posted_at: datetime | None
    ingested_at: datetime


class JobListResponse(BaseModel):
    """Paginated job list response."""

    items: list[JobSummaryResponse]
    total: int
    page: int
    limit: int
    has_more: bool


class MatchAnalysis(BaseModel):
    """Detailed match score analysis."""

    overall_score: int
    skills_score: int
    skills_matched: list[str]
    skills_missing: list[str]
    experience_score: int
    experience_gap: str | None
    location_score: int
    location_match: bool
    salary_score: int
    salary_in_range: bool | None
    culture_score: int
    recommendation: str
