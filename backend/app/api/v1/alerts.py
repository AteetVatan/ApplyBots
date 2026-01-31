"""Alert API endpoints.

Standards: python_clean.mdc
- FastAPI router
- Dependency injection
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_db_session
from app.core.domain.alert import AlertType as DomainAlertType
from app.core.services.alerts import AlertService
from app.infra.db.repositories.alert import (
    SQLAlertPreferenceRepository,
    SQLAlertRepository,
)
from app.schemas.alert import (
    AlertPreferencesResponse,
    AlertPreferencesUpdateRequest,
    AlertResponse,
    AlertsPageResponse,
    AlertType,
    UnreadCountResponse,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _get_alert_service(session) -> AlertService:
    """Create alert service with dependencies."""
    return AlertService(
        alert_repo=SQLAlertRepository(session=session),
        preference_repo=SQLAlertPreferenceRepository(session=session),
    )


@router.get("", response_model=AlertsPageResponse)
async def get_alerts(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
    unread_only: bool = Query(False, description="Filter to unread alerts only"),
    limit: int = Query(50, ge=1, le=100, description="Max alerts to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Get paginated alerts for the current user."""
    service = _get_alert_service(session)

    page = await service.get_alerts(
        current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    return AlertsPageResponse(
        alerts=[
            AlertResponse(
                id=a.id,
                alert_type=AlertType(a.alert_type.value),
                title=a.title,
                message=a.message,
                data=a.data,
                read=a.read,
                created_at=a.created_at,
            )
            for a in page.alerts
        ],
        total_unread=page.total_unread,
        has_more=page.has_more,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get count of unread alerts."""
    repo = SQLAlertRepository(session=session)
    count = await repo.get_unread_count(current_user.id)
    return UnreadCountResponse(count=count)


@router.post("/{alert_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_alert_read(
    alert_id: str,
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Mark a single alert as read."""
    service = _get_alert_service(session)

    # Verify alert belongs to user
    repo = SQLAlertRepository(session=session)
    alert = await repo.get_by_id(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    if alert.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access this alert",
        )

    await service.mark_read(alert_id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Mark all alerts as read."""
    service = _get_alert_service(session)
    await service.mark_all_read(current_user.id)


@router.get("/preferences", response_model=AlertPreferencesResponse)
async def get_preferences(
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Get alert preferences for the current user."""
    service = _get_alert_service(session)
    prefs = await service.get_preferences(current_user.id)

    return AlertPreferencesResponse(
        dream_job_threshold=prefs.dream_job_threshold,
        interview_reminder_hours=prefs.interview_reminder_hours,
        daily_digest=prefs.daily_digest,
        enabled_types=[AlertType(t.value) for t in prefs.enabled_types],
    )


@router.put("/preferences", response_model=AlertPreferencesResponse)
async def update_preferences(
    request: AlertPreferencesUpdateRequest,
    session: Annotated[object, Depends(get_db_session)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Update alert preferences."""
    service = _get_alert_service(session)

    # Convert schema types to domain types
    enabled_types = None
    if request.enabled_types is not None:
        enabled_types = [DomainAlertType(t.value) for t in request.enabled_types]

    prefs = await service.update_preferences(
        current_user.id,
        dream_job_threshold=request.dream_job_threshold,
        interview_reminder_hours=request.interview_reminder_hours,
        daily_digest=request.daily_digest,
        enabled_types=enabled_types,
    )

    return AlertPreferencesResponse(
        dream_job_threshold=prefs.dream_job_threshold,
        interview_reminder_hours=prefs.interview_reminder_hours,
        daily_digest=prefs.daily_digest,
        enabled_types=[AlertType(t.value) for t in prefs.enabled_types],
    )
