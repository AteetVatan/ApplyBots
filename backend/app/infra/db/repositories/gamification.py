"""Gamification repository implementation.

Standards: python_clean.mdc
- Async operations
- Type hints
"""

from datetime import date, datetime
from typing import Sequence

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.gamification import (
    ACHIEVEMENTS,
    AchievementId,
    UserAchievement,
    UserStreak,
)
from app.infra.db.models import UserAchievementModel, UserStreakModel, generate_cuid

logger = structlog.get_logger(__name__)


class SQLUserStreakRepository:
    """SQL repository for user streaks."""

    def __init__(self, *, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> UserStreak | None:
        """Get streak data for a user."""
        result = await self._session.execute(
            select(UserStreakModel).where(UserStreakModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def upsert(self, streak: UserStreak) -> UserStreak:
        """Create or update streak data."""
        existing = await self.get_by_user_id(streak.user_id)

        if existing:
            await self._session.execute(
                update(UserStreakModel)
                .where(UserStreakModel.user_id == streak.user_id)
                .values(
                    current_streak=streak.current_streak,
                    longest_streak=streak.longest_streak,
                    last_activity_date=streak.last_activity_date,
                    total_points=streak.total_points,
                )
            )
            return streak

        model = UserStreakModel(
            id=generate_cuid(),
            user_id=streak.user_id,
            current_streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            last_activity_date=streak.last_activity_date,
            total_points=streak.total_points,
        )
        self._session.add(model)
        await self._session.flush()

        return self._to_domain(model)

    async def add_points(self, user_id: str, points: int) -> int:
        """Add points to user's total.

        Returns new total points.
        """
        streak = await self.get_by_user_id(user_id)
        if not streak:
            streak = UserStreak(user_id=user_id, total_points=points)
            await self.upsert(streak)
            return points

        new_total = streak.total_points + points
        await self._session.execute(
            update(UserStreakModel)
            .where(UserStreakModel.user_id == user_id)
            .values(total_points=new_total)
        )
        return new_total

    def _to_domain(self, model: UserStreakModel) -> UserStreak:
        """Convert model to domain entity."""
        last_date = None
        if model.last_activity_date:
            if isinstance(model.last_activity_date, datetime):
                last_date = model.last_activity_date.date()
            else:
                last_date = model.last_activity_date

        return UserStreak(
            user_id=model.user_id,
            current_streak=model.current_streak,
            longest_streak=model.longest_streak,
            last_activity_date=last_date,
            total_points=model.total_points,
        )


class SQLUserAchievementRepository:
    """SQL repository for user achievements."""

    def __init__(self, *, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Sequence[UserAchievement]:
        """Get all achievements for a user."""
        result = await self._session.execute(
            select(UserAchievementModel)
            .where(UserAchievementModel.user_id == user_id)
            .order_by(UserAchievementModel.earned_at.desc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def has_achievement(
        self,
        user_id: str,
        achievement_id: AchievementId,
    ) -> bool:
        """Check if user has a specific achievement."""
        result = await self._session.execute(
            select(UserAchievementModel.id)
            .where(UserAchievementModel.user_id == user_id)
            .where(UserAchievementModel.achievement_id == achievement_id.value)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def award(
        self,
        user_id: str,
        achievement_id: AchievementId,
    ) -> UserAchievement | None:
        """Award an achievement to a user.

        Returns None if already earned.
        """
        # Check if already has achievement
        if await self.has_achievement(user_id, achievement_id):
            logger.debug(
                "achievement_already_earned",
                user_id=user_id,
                achievement_id=achievement_id.value,
            )
            return None

        model = UserAchievementModel(
            id=generate_cuid(),
            user_id=user_id,
            achievement_id=achievement_id.value,
            earned_at=datetime.utcnow(),
        )
        self._session.add(model)
        await self._session.flush()

        logger.info(
            "achievement_awarded",
            user_id=user_id,
            achievement_id=achievement_id.value,
            points=ACHIEVEMENTS[achievement_id].points,
        )

        return self._to_domain(model)

    async def get_earned_count(self, user_id: str) -> int:
        """Get count of achievements earned."""
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count(UserAchievementModel.id)).where(
                UserAchievementModel.user_id == user_id
            )
        )
        return result.scalar() or 0

    def _to_domain(self, model: UserAchievementModel) -> UserAchievement:
        """Convert model to domain entity."""
        return UserAchievement(
            id=model.id,
            user_id=model.user_id,
            achievement_id=AchievementId(model.achievement_id),
            earned_at=model.earned_at,
        )
