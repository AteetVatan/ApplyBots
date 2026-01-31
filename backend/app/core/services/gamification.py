"""Gamification service for streaks and achievements.

Standards: python_clean.mdc
- Domain-focused logic
- Event-driven achievement checks
"""

from datetime import date, datetime, timedelta
from typing import Protocol, Sequence

import structlog

from app.core.domain.gamification import (
    ACHIEVEMENTS,
    AchievementId,
    GamificationProgress,
    UserAchievement,
    UserStreak,
)

logger = structlog.get_logger(__name__)


class UserStreakRepository(Protocol):
    """Protocol for streak repository."""

    async def get_by_user_id(self, user_id: str) -> UserStreak | None: ...
    async def upsert(self, streak: UserStreak) -> UserStreak: ...
    async def add_points(self, user_id: str, points: int) -> int: ...


class UserAchievementRepository(Protocol):
    """Protocol for achievement repository."""

    async def get_by_user_id(self, user_id: str) -> Sequence[UserAchievement]: ...
    async def has_achievement(
        self, user_id: str, achievement_id: AchievementId
    ) -> bool: ...
    async def award(
        self, user_id: str, achievement_id: AchievementId
    ) -> UserAchievement | None: ...
    async def get_earned_count(self, user_id: str) -> int: ...


class GamificationService:
    """Service for gamification features."""

    def __init__(
        self,
        *,
        streak_repo: UserStreakRepository,
        achievement_repo: UserAchievementRepository,
    ) -> None:
        self._streak_repo = streak_repo
        self._achievement_repo = achievement_repo

    async def record_activity(self, user_id: str) -> UserStreak:
        """Record user activity and update streak.

        Call this when user performs a tracked action (e.g., submits application).

        Args:
            user_id: User ID

        Returns:
            Updated streak data
        """
        today = date.today()
        streak = await self._streak_repo.get_by_user_id(user_id)

        if not streak:
            # First activity
            streak = UserStreak(
                user_id=user_id,
                current_streak=1,
                longest_streak=1,
                last_activity_date=today,
                total_points=0,
            )
            await self._streak_repo.upsert(streak)

            logger.info("first_activity_recorded", user_id=user_id)
            return streak

        # Check if activity is on a new day
        if streak.last_activity_date == today:
            # Already recorded activity today
            return streak

        # Calculate streak
        if streak.last_activity_date:
            days_since = (today - streak.last_activity_date).days

            if days_since == 1:
                # Consecutive day - increment streak
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            elif days_since > 1:
                # Streak broken
                streak.current_streak = 1
        else:
            streak.current_streak = 1

        streak.last_activity_date = today
        await self._streak_repo.upsert(streak)

        # Check for streak achievements
        await self._check_streak_achievements(user_id, streak.current_streak)

        logger.info(
            "activity_recorded",
            user_id=user_id,
            current_streak=streak.current_streak,
        )

        return streak

    async def get_progress(self, user_id: str) -> GamificationProgress:
        """Get user's overall gamification progress.

        Args:
            user_id: User ID

        Returns:
            Complete gamification progress data
        """
        streak = await self._streak_repo.get_by_user_id(user_id)
        if not streak:
            streak = UserStreak(user_id=user_id)

        achievements = await self._achievement_repo.get_by_user_id(user_id)
        earned_count = len(achievements)

        return GamificationProgress(
            user_id=user_id,
            streak=streak,
            achievements=list(achievements),
            total_points=streak.total_points,
            achievements_earned=earned_count,
        )

    async def check_and_award_achievements(
        self,
        user_id: str,
        *,
        event: str,
        context: dict | None = None,
    ) -> list[UserAchievement]:
        """Check and award achievements based on an event.

        Args:
            user_id: User ID
            event: Event type (e.g., "application_submitted", "interview_received")
            context: Optional context data (e.g., match_score, count)

        Returns:
            List of newly awarded achievements
        """
        context = context or {}
        awarded: list[UserAchievement] = []

        # Map events to achievement checks
        if event == "application_submitted":
            # Check first application
            first = await self._award_if_eligible(user_id, AchievementId.FIRST_APPLY)
            if first:
                awarded.append(first)

            # Check application count milestones
            count = context.get("total_applications", 0)
            if count >= 10:
                a = await self._award_if_eligible(user_id, AchievementId.APPLY_10)
                if a:
                    awarded.append(a)
            if count >= 50:
                a = await self._award_if_eligible(user_id, AchievementId.APPLY_50)
                if a:
                    awarded.append(a)

        elif event == "match_score_calculated":
            score = context.get("match_score", 0)
            if score >= 95:
                a = await self._award_if_eligible(user_id, AchievementId.PERFECT_MATCH)
                if a:
                    awarded.append(a)

        elif event == "interview_received":
            a = await self._award_if_eligible(user_id, AchievementId.INTERVIEW_1)
            if a:
                awarded.append(a)

        elif event == "offer_received":
            a = await self._award_if_eligible(user_id, AchievementId.OFFER_1)
            if a:
                awarded.append(a)

        elif event == "profile_completed":
            a = await self._award_if_eligible(user_id, AchievementId.PROFILE_COMPLETE)
            if a:
                awarded.append(a)

        elif event == "resume_ats_score":
            score = context.get("ats_score", 0)
            if score >= 90:
                a = await self._award_if_eligible(user_id, AchievementId.RESUME_OPTIMIZED)
                if a:
                    awarded.append(a)

        return awarded

    async def _check_streak_achievements(
        self,
        user_id: str,
        current_streak: int,
    ) -> list[UserAchievement]:
        """Check and award streak-based achievements."""
        awarded: list[UserAchievement] = []

        if current_streak >= 7:
            a = await self._award_if_eligible(user_id, AchievementId.STREAK_7)
            if a:
                awarded.append(a)

        if current_streak >= 30:
            a = await self._award_if_eligible(user_id, AchievementId.STREAK_30)
            if a:
                awarded.append(a)

        return awarded

    async def _award_if_eligible(
        self,
        user_id: str,
        achievement_id: AchievementId,
    ) -> UserAchievement | None:
        """Award achievement if user doesn't already have it.

        Also adds points to user's total.

        Returns:
            Awarded achievement or None if already earned
        """
        achievement = await self._achievement_repo.award(user_id, achievement_id)

        if achievement:
            # Add points
            points = ACHIEVEMENTS[achievement_id].points
            await self._streak_repo.add_points(user_id, points)

            logger.info(
                "achievement_awarded",
                user_id=user_id,
                achievement_id=achievement_id.value,
                points=points,
            )

        return achievement

    async def get_all_achievements(self) -> list[dict]:
        """Get all available achievements with their definitions.

        Returns:
            List of achievement definitions
        """
        return [
            {
                "id": a.id.value,
                "name": a.name,
                "description": a.description,
                "points": a.points,
                "icon": a.icon,
            }
            for a in ACHIEVEMENTS.values()
        ]

    async def get_leaderboard(
        self,
        *,
        limit: int = 10,
    ) -> list[dict]:
        """Get top users by points (anonymized).

        Note: This is a stub - would need additional repo method.

        Args:
            limit: Max users to return

        Returns:
            List of anonymized leaderboard entries
        """
        # This would require a new repository method to query
        # top users by total_points
        return []
