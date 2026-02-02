"""Wellness API endpoints.

Standards: python_clean.mdc
- FastAPI router
- Dependency injection
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_db
from app.core.services.wellness import WellnessService
from app.infra.db.repositories.application import SQLApplicationRepository
from app.schemas.wellness import (
    BurnoutSignalsResponse,
    WellnessInsightResponse,
    WellnessInsightType,
    WellnessStatusResponse,
)

router = APIRouter(prefix="/wellness", tags=["wellness"])


def _get_wellness_service(session) -> WellnessService:
    """Create wellness service with dependencies."""
    return WellnessService(
        application_repo=SQLApplicationRepository(session=session),
    )


@router.get("/insight", response_model=WellnessInsightResponse)
async def get_daily_insight(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get a personalized daily wellness insight."""
    service = _get_wellness_service(session)
    insight = await service.get_daily_insight(current_user.id)

    return WellnessInsightResponse(
        insight_type=WellnessInsightType(insight.insight_type.value),
        title=insight.title,
        message=insight.message,
        action_suggestion=insight.action_suggestion,
        priority=insight.priority,
    )


@router.get("/status", response_model=WellnessStatusResponse)
async def get_wellness_status(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get comprehensive wellness status."""
    service = _get_wellness_service(session)
    status = await service.get_wellness_status(current_user.id)

    return WellnessStatusResponse(
        activity_level=status.activity_level,
        rejection_streak=status.rejection_streak,
        days_since_last_positive=status.days_since_last_positive,
        burnout_risk=status.burnout_risk,
        recommended_action=status.recommended_action,
        last_checked=status.last_checked,
    )


@router.get("/burnout-signals", response_model=BurnoutSignalsResponse)
async def get_burnout_signals(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Detect burnout warning signals."""
    service = _get_wellness_service(session)
    signals = await service.detect_burnout_signals(current_user.id)

    return BurnoutSignalsResponse(
        consecutive_rejections=signals.consecutive_rejections,
        hours_active_today=signals.hours_active_today,
        declining_match_scores=signals.declining_match_scores,
        panic_applying=signals.panic_applying,
        no_breaks_taken=signals.no_breaks_taken,
    )


@router.get("/break-reminder", response_model=WellnessInsightResponse)
async def get_break_reminder(
    session: Annotated[object, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get a break reminder insight."""
    service = _get_wellness_service(session)
    insight = service.get_break_reminder()

    return WellnessInsightResponse(
        insight_type=WellnessInsightType(insight.insight_type.value),
        title=insight.title,
        message=insight.message,
        action_suggestion=insight.action_suggestion,
        priority=insight.priority,
    )
