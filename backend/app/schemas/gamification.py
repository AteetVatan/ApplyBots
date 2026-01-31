"""Gamification API schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class AchievementDefinitionResponse(BaseModel):
    """Achievement definition response."""

    id: str
    name: str
    description: str
    points: int
    icon: str


class UserAchievementResponse(BaseModel):
    """User's earned achievement response."""

    id: str
    achievement_id: str
    name: str
    description: str
    points: int
    icon: str
    earned_at: datetime


class UserStreakResponse(BaseModel):
    """User streak response."""

    current_streak: int
    longest_streak: int
    last_activity_date: date | None
    total_points: int


class GamificationProgressResponse(BaseModel):
    """User's gamification progress response."""

    streak: UserStreakResponse
    achievements: list[UserAchievementResponse]
    total_points: int
    achievements_earned: int
    achievements_total: int
    completion_percentage: float = Field(ge=0, le=100)


class AllAchievementsResponse(BaseModel):
    """All available achievements response."""

    achievements: list[AchievementDefinitionResponse]
    total: int


class AchievementEarnedEvent(BaseModel):
    """Event when an achievement is earned."""

    achievement_id: str
    name: str
    points: int
    icon: str
    earned_at: datetime
