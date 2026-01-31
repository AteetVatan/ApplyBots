"""Analytics API endpoints.

Standards: python_clean.mdc
- FastAPI router
- Dependency injection
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_db_session
from app.core.services.analytics import AnalyticsService
from app.infra.db.repositories.application import SQLApplicationRepository
from app.infra.db.repositories.job import SQLJobRepository
from app.schemas.analytics import (
    AdvancedAnalyticsResponse,
    ApplicationFunnelResponse,
    ConversionMetricsResponse,
    HeatmapCellResponse,
    HeatmapResponse,
    PredictiveInsightsResponse,
    TrendDataResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_analytics_service(session) -> AnalyticsService:
    """Create analytics service with dependencies."""
    return AnalyticsService(
        application_repository=SQLApplicationRepository(session=session),
        job_repository=SQLJobRepository(session=session),
    )


@router.get("/funnel", response_model=ApplicationFunnelResponse)
async def get_funnel(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """Get application funnel metrics."""
    service = _get_analytics_service(session)
    funnel = await service.get_funnel(user_id=current_user.id, days=days)

    return ApplicationFunnelResponse(
        total_applied=funnel.total_applied,
        pending=funnel.pending,
        interviews=funnel.interviews,
        offers=funnel.offers,
        rejected=funnel.rejected,
        no_response=funnel.no_response,
        conversion_rate=funnel.conversion_rate,
    )


@router.get("/trends", response_model=TrendDataResponse)
async def get_trends(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=90, description="Number of days of history"),
):
    """Get application trend data."""
    service = _get_analytics_service(session)
    trends = await service.get_trends(user_id=current_user.id, days=days)

    return TrendDataResponse(
        labels=trends.labels,
        applications=trends.applications,
        interviews=trends.interviews,
        offers=trends.offers,
    )


@router.get("/advanced", response_model=AdvancedAnalyticsResponse)
async def get_advanced_analytics(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
    days: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
):
    """Get comprehensive advanced analytics."""
    service = _get_analytics_service(session)
    analytics = await service.get_advanced_analytics(user_id=current_user.id, days=days)

    return AdvancedAnalyticsResponse(
        funnel=ApplicationFunnelResponse(
            total_applied=analytics.funnel.total_applied,
            pending=analytics.funnel.pending,
            interviews=analytics.funnel.interviews,
            offers=analytics.funnel.offers,
            rejected=analytics.funnel.rejected,
            no_response=analytics.funnel.no_response,
            conversion_rate=analytics.funnel.conversion_rate,
        ),
        apply_to_interview_rate=analytics.apply_to_interview_rate,
        interview_to_offer_rate=analytics.interview_to_offer_rate,
        overall_conversion_rate=analytics.overall_conversion_rate,
        avg_time_to_first_response_days=analytics.avg_time_to_first_response_days,
        avg_time_to_interview_days=analytics.avg_time_to_interview_days,
        success_by_source={
            k: ConversionMetricsResponse(
                total=v.total,
                interviews=v.interviews,
                offers=v.offers,
                interview_rate=v.interview_rate,
                offer_rate=v.offer_rate,
            )
            for k, v in analytics.success_by_source.items()
        },
        success_by_match_score_range={
            k: ConversionMetricsResponse(
                total=v.total,
                interviews=v.interviews,
                offers=v.offers,
                interview_rate=v.interview_rate,
                offer_rate=v.offer_rate,
            )
            for k, v in analytics.success_by_match_score_range.items()
        },
        success_by_remote_type={
            k: ConversionMetricsResponse(
                total=v.total,
                interviews=v.interviews,
                offers=v.offers,
                interview_rate=v.interview_rate,
                offer_rate=v.offer_rate,
            )
            for k, v in analytics.success_by_remote_type.items()
        },
        applications_by_day_of_week=analytics.applications_by_day_of_week,
        applications_by_hour=analytics.applications_by_hour,
        best_performing_day=analytics.best_performing_day,
        best_performing_hour=analytics.best_performing_hour,
        estimated_interviews_this_month=analytics.estimated_interviews_this_month,
        recommended_daily_applications=analytics.recommended_daily_applications,
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
    days: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
):
    """Get application success heatmap by day and hour."""
    service = _get_analytics_service(session)
    heatmap = await service.get_heatmap(user_id=current_user.id, days=days)

    return HeatmapResponse(
        cells=[
            HeatmapCellResponse(
                day=c.day,
                hour=c.hour,
                count=c.count,
                success_rate=c.success_rate,
            )
            for c in heatmap.cells
        ],
        best_day=heatmap.best_day,
        best_hour=heatmap.best_hour,
        total_applications=heatmap.total_applications,
    )


@router.get("/predictions", response_model=PredictiveInsightsResponse)
async def get_predictions(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get predictive insights for job search."""
    service = _get_analytics_service(session)
    predictions = await service.get_predictions(user_id=current_user.id)

    return PredictiveInsightsResponse(
        estimated_time_to_offer_days=predictions.estimated_time_to_offer_days,
        estimated_applications_needed=predictions.estimated_applications_needed,
        current_success_rate=predictions.current_success_rate,
        trend_direction=predictions.trend_direction,
        recommendations=predictions.recommendations,
    )
