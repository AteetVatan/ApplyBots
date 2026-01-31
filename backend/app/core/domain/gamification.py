"""Gamification domain model.

Standards: python_clean.mdc
- Enum for achievement types
- Dataclass for domain models
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class AchievementId(str, Enum):
    """Achievement identifiers."""

    FIRST_APPLY = "first_apply"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    PERFECT_MATCH = "perfect_match"
    INTERVIEW_1 = "interview_1"
    OFFER_1 = "offer_1"
    PROFILE_COMPLETE = "profile_complete"
    RESUME_OPTIMIZED = "resume_optimized"
    APPLY_10 = "apply_10"
    APPLY_50 = "apply_50"


@dataclass(frozen=True)
class AchievementDefinition:
    """Static achievement definition."""

    id: AchievementId
    name: str
    description: str
    points: int
    icon: str  # Emoji or icon name


# Achievement definitions - static data
ACHIEVEMENTS: dict[AchievementId, AchievementDefinition] = {
    AchievementId.FIRST_APPLY: AchievementDefinition(
        id=AchievementId.FIRST_APPLY,
        name="First Application",
        description="Submit your first job application",
        points=10,
        icon="🎯",
    ),
    AchievementId.STREAK_7: AchievementDefinition(
        id=AchievementId.STREAK_7,
        name="Week Warrior",
        description="Maintain a 7-day activity streak",
        points=50,
        icon="🔥",
    ),
    AchievementId.STREAK_30: AchievementDefinition(
        id=AchievementId.STREAK_30,
        name="Monthly Master",
        description="Maintain a 30-day activity streak",
        points=200,
        icon="💪",
    ),
    AchievementId.PERFECT_MATCH: AchievementDefinition(
        id=AchievementId.PERFECT_MATCH,
        name="Perfect Match",
        description="Get a 95%+ match score on a job",
        points=25,
        icon="⭐",
    ),
    AchievementId.INTERVIEW_1: AchievementDefinition(
        id=AchievementId.INTERVIEW_1,
        name="Interview Unlocked",
        description="Receive your first interview invitation",
        points=100,
        icon="🎤",
    ),
    AchievementId.OFFER_1: AchievementDefinition(
        id=AchievementId.OFFER_1,
        name="Offer Received",
        description="Receive your first job offer",
        points=500,
        icon="🏆",
    ),
    AchievementId.PROFILE_COMPLETE: AchievementDefinition(
        id=AchievementId.PROFILE_COMPLETE,
        name="Profile Pro",
        description="Complete all profile sections",
        points=30,
        icon="✅",
    ),
    AchievementId.RESUME_OPTIMIZED: AchievementDefinition(
        id=AchievementId.RESUME_OPTIMIZED,
        name="Resume Master",
        description="Achieve 90%+ ATS score on your resume",
        points=40,
        icon="📄",
    ),
    AchievementId.APPLY_10: AchievementDefinition(
        id=AchievementId.APPLY_10,
        name="Consistent Applicant",
        description="Submit 10 job applications",
        points=75,
        icon="📝",
    ),
    AchievementId.APPLY_50: AchievementDefinition(
        id=AchievementId.APPLY_50,
        name="Application Machine",
        description="Submit 50 job applications",
        points=150,
        icon="🚀",
    ),
}


@dataclass
class UserStreak:
    """User activity streak data."""

    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: date | None = None
    total_points: int = 0


@dataclass
class UserAchievement:
    """User's earned achievement."""

    id: str
    user_id: str
    achievement_id: AchievementId
    earned_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def definition(self) -> AchievementDefinition:
        """Get the achievement definition."""
        return ACHIEVEMENTS[self.achievement_id]


@dataclass
class GamificationProgress:
    """User's overall gamification progress."""

    user_id: str
    streak: UserStreak
    achievements: list[UserAchievement]
    total_points: int
    achievements_earned: int
    achievements_total: int = len(ACHIEVEMENTS)

    @property
    def completion_percentage(self) -> float:
        """Calculate achievement completion percentage."""
        return (self.achievements_earned / self.achievements_total) * 100
