"""Alert domain model.

Standards: python_clean.mdc
- Enum for alert types
- Dataclass for domain models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Type of alert notification."""

    DREAM_JOB_MATCH = "dream_job_match"
    APPLICATION_STATUS_CHANGE = "application_status_change"
    INTERVIEW_REMINDER = "interview_reminder"
    CAMPAIGN_MILESTONE = "campaign_milestone"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    WELLNESS_TIP = "wellness_tip"


@dataclass
class Alert:
    """Alert notification domain entity."""

    id: str
    user_id: str
    alert_type: AlertType
    title: str
    message: str
    data: dict = field(default_factory=dict)
    read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertPreferences:
    """User preferences for alerts."""

    user_id: str
    dream_job_threshold: int = 90  # Min match score to trigger dream job alert
    interview_reminder_hours: int = 24  # Hours before interview to remind
    daily_digest: bool = False  # Whether to send daily summary
    enabled_types: list[AlertType] = field(
        default_factory=lambda: list(AlertType)
    )
