"""Alert API schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Type of alert notification."""

    DREAM_JOB_MATCH = "dream_job_match"
    APPLICATION_STATUS_CHANGE = "application_status_change"
    INTERVIEW_REMINDER = "interview_reminder"
    CAMPAIGN_MILESTONE = "campaign_milestone"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    WELLNESS_TIP = "wellness_tip"


class AlertResponse(BaseModel):
    """Alert response schema."""

    id: str
    alert_type: AlertType
    title: str
    message: str
    data: dict = Field(default_factory=dict)
    read: bool
    created_at: datetime


class AlertsPageResponse(BaseModel):
    """Paginated alerts response."""

    alerts: list[AlertResponse]
    total_unread: int
    has_more: bool


class AlertPreferencesResponse(BaseModel):
    """Alert preferences response."""

    dream_job_threshold: int = Field(ge=0, le=100)
    interview_reminder_hours: int = Field(ge=1, le=168)
    daily_digest: bool
    enabled_types: list[AlertType]


class AlertPreferencesUpdateRequest(BaseModel):
    """Request to update alert preferences."""

    dream_job_threshold: int | None = Field(default=None, ge=0, le=100)
    interview_reminder_hours: int | None = Field(default=None, ge=1, le=168)
    daily_digest: bool | None = None
    enabled_types: list[AlertType] | None = None


class UnreadCountResponse(BaseModel):
    """Unread alerts count response."""

    count: int
