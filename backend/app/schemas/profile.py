"""Profile schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class PreferencesUpdate(BaseModel):
    """Update job search preferences."""

    target_roles: list[str] | None = None
    target_locations: list[str] | None = None
    remote_only: bool | None = None
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    negative_keywords: list[str] | None = None
    experience_years: int | None = Field(None, ge=0, le=50)


class PreferencesResponse(BaseModel):
    """Job search preferences response."""

    target_roles: list[str]
    target_locations: list[str]
    remote_only: bool
    salary_min: int | None
    salary_max: int | None
    negative_keywords: list[str]
    experience_years: int | None


class ProfileUpdate(BaseModel):
    """Update user profile."""

    full_name: str | None = Field(None, max_length=255)
    headline: str | None = Field(None, max_length=500)
    location: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    linkedin_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None


class ProfileResponse(BaseModel):
    """User profile response."""

    id: str
    user_id: str
    full_name: str | None
    headline: str | None
    location: str | None
    phone: str | None
    linkedin_url: str | None
    portfolio_url: str | None
    preferences: PreferencesResponse
    created_at: datetime
    updated_at: datetime | None


class ParsedResumeResponse(BaseModel):
    """Parsed resume data response."""

    full_name: str | None
    email: str | None
    phone: str | None
    location: str | None
    summary: str | None
    skills: list[str]
    total_years_experience: float | None


class ResumeResponse(BaseModel):
    """Resume response."""

    id: str
    filename: str
    is_primary: bool
    parsed_data: ParsedResumeResponse | None
    created_at: datetime
    extraction_status: Literal["success", "partial", "failed", "pending_ocr"] | None = None
    extraction_warnings: list[str] | None = None
    extraction_method: str | None = None