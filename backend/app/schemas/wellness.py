"""Wellness API schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class WellnessInsightType(str, Enum):
    """Type of wellness insight."""

    ENCOURAGEMENT = "encouragement"
    MILESTONE = "milestone"
    TIP = "tip"
    BURNOUT_WARNING = "burnout_warning"
    BREAK_REMINDER = "break_reminder"
    SUCCESS_STORY = "success_story"


class WellnessInsightResponse(BaseModel):
    """Wellness insight response."""

    insight_type: WellnessInsightType
    title: str
    message: str
    action_suggestion: str | None
    priority: int


class WellnessStatusResponse(BaseModel):
    """Wellness status response."""

    activity_level: str
    rejection_streak: int
    days_since_last_positive: int | None
    burnout_risk: str
    recommended_action: str
    last_checked: datetime


class BurnoutSignalsResponse(BaseModel):
    """Burnout signals response."""

    consecutive_rejections: int
    hours_active_today: float
    declining_match_scores: bool
    panic_applying: bool
    no_breaks_taken: bool
