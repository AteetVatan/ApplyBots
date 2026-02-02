"""Gamification API endpoints.

Standards: python_clean.mdc
- FastAPI router
- Dependency injection
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_db
from app.core.domain.gamification import ACHIEVEMENTS
from app.core.services.gamification import GamificationService
from app.infra.db.repositories.gamification import (
    SQLUserAchievementRepository,
    SQLUserStreakRepository,
)
from app.schemas.gamification import (
    AchievementDefinitionResponse,
    AllAchievementsResponse,
    GamificationProgressResponse,
    UserAchievementResponse,
    UserStreakResponse,
)

router = APIRouter(prefix="/gamification", tags=["gamification"])


def _get_gamification_service(session) -> GamificationService:
    """Create gamification service with dependencies."""
    return GamificationService(
        streak_repo=SQLUserStreakRepository(session=session),
        achievement_repo=SQLUserAchievementRepository(session=session),
    )


@router.get("/progress", response_model=GamificationProgressResponse)
async def get_progress(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get current user's gamification progress including streak and achievements."""
    service = _get_gamification_service(session)
    progress = await service.get_progress(current_user.id)

    return GamificationProgressResponse(
        streak=UserStreakResponse(
            current_streak=progress.streak.current_streak,
            longest_streak=progress.streak.longest_streak,
            last_activity_date=progress.streak.last_activity_date,
            total_points=progress.streak.total_points,
        ),
        achievements=[
            UserAchievementResponse(
                id=a.id,
                achievement_id=a.achievement_id.value,
                name=a.definition.name,
                description=a.definition.description,
                points=a.definition.points,
                icon=a.definition.icon,
                earned_at=a.earned_at,
            )
            for a in progress.achievements
        ],
        total_points=progress.total_points,
        achievements_earned=progress.achievements_earned,
        achievements_total=progress.achievements_total,
        completion_percentage=progress.completion_percentage,
    )


@router.get("/achievements", response_model=AllAchievementsResponse)
async def get_all_achievements(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get all available achievements with earned status."""
    service = _get_gamification_service(session)

    # Get user's progress to know which are earned
    progress = await service.get_progress(current_user.id)
    earned_ids = {a.achievement_id.value for a in progress.achievements}

    achievements = [
        AchievementDefinitionResponse(
            id=a.id.value,
            name=a.name,
            description=a.description,
            points=a.points,
            icon=a.icon,
        )
        for a in ACHIEVEMENTS.values()
    ]

    return AllAchievementsResponse(
        achievements=achievements,
        total=len(achievements),
    )


@router.get("/streak", response_model=UserStreakResponse)
async def get_streak(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get current user's streak data."""
    service = _get_gamification_service(session)
    progress = await service.get_progress(current_user.id)

    return UserStreakResponse(
        current_streak=progress.streak.current_streak,
        longest_streak=progress.streak.longest_streak,
        last_activity_date=progress.streak.last_activity_date,
        total_points=progress.streak.total_points,
    )
