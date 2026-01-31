"""Alert service for notifications.

Standards: python_clean.mdc
- Async operations
- Domain-focused logic
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Sequence

import structlog

from app.core.domain.alert import Alert, AlertPreferences, AlertType

logger = structlog.get_logger(__name__)


class AlertRepository(Protocol):
    """Protocol for alert repository."""

    async def create(self, alert: Alert) -> Alert: ...
    async def get_by_id(self, alert_id: str) -> Alert | None: ...
    async def get_by_user_id(
        self,
        user_id: str,
        *,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Alert]: ...
    async def get_unread_count(self, user_id: str) -> int: ...
    async def mark_read(self, alert_id: str) -> bool: ...
    async def mark_all_read(self, user_id: str) -> int: ...


class AlertPreferenceRepository(Protocol):
    """Protocol for alert preference repository."""

    async def get_by_user_id(self, user_id: str) -> AlertPreferences | None: ...
    async def upsert(self, preferences: AlertPreferences) -> AlertPreferences: ...
    async def get_users_with_dream_job_alerts(
        self, min_threshold: int = 0
    ) -> Sequence[AlertPreferences]: ...


@dataclass
class AlertsPage:
    """Paginated alerts response."""

    alerts: list[Alert]
    total_unread: int
    has_more: bool


class AlertService:
    """Service for managing user alerts."""

    def __init__(
        self,
        *,
        alert_repo: AlertRepository,
        preference_repo: AlertPreferenceRepository,
    ) -> None:
        self._alert_repo = alert_repo
        self._preference_repo = preference_repo

    async def create_alert(
        self,
        *,
        user_id: str,
        alert_type: AlertType,
        title: str,
        message: str,
        data: dict | None = None,
    ) -> Alert:
        """Create a new alert for a user.

        Args:
            user_id: Target user ID
            alert_type: Type of alert
            title: Alert title
            message: Alert message body
            data: Optional JSON data payload

        Returns:
            Created alert
        """
        import uuid

        # Check user preferences
        prefs = await self._preference_repo.get_by_user_id(user_id)
        if prefs and alert_type not in prefs.enabled_types:
            logger.debug(
                "alert_type_disabled",
                user_id=user_id,
                alert_type=alert_type.value,
            )
            # Still create but could be filtered in future
            pass

        alert = Alert(
            id=str(uuid.uuid4()),
            user_id=user_id,
            alert_type=alert_type,
            title=title,
            message=message,
            data=data or {},
            read=False,
            created_at=datetime.utcnow(),
        )

        created = await self._alert_repo.create(alert)

        logger.info(
            "alert_created",
            alert_id=created.id,
            user_id=user_id,
            alert_type=alert_type.value,
        )

        return created

    async def get_alerts(
        self,
        user_id: str,
        *,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> AlertsPage:
        """Get paginated alerts for a user.

        Args:
            user_id: User ID
            unread_only: Filter to unread only
            limit: Max alerts to return
            offset: Pagination offset

        Returns:
            AlertsPage with alerts and metadata
        """
        alerts = await self._alert_repo.get_by_user_id(
            user_id,
            unread_only=unread_only,
            limit=limit + 1,  # Fetch one extra to check has_more
            offset=offset,
        )

        has_more = len(alerts) > limit
        if has_more:
            alerts = alerts[:limit]

        unread_count = await self._alert_repo.get_unread_count(user_id)

        return AlertsPage(
            alerts=list(alerts),
            total_unread=unread_count,
            has_more=has_more,
        )

    async def mark_read(self, alert_id: str) -> bool:
        """Mark a single alert as read.

        Args:
            alert_id: Alert ID

        Returns:
            True if marked, False if not found
        """
        return await self._alert_repo.mark_read(alert_id)

    async def mark_all_read(self, user_id: str) -> int:
        """Mark all alerts as read for a user.

        Args:
            user_id: User ID

        Returns:
            Number of alerts marked read
        """
        count = await self._alert_repo.mark_all_read(user_id)
        logger.info("alerts_marked_read", user_id=user_id, count=count)
        return count

    async def get_preferences(self, user_id: str) -> AlertPreferences:
        """Get alert preferences for a user.

        Creates default preferences if none exist.

        Args:
            user_id: User ID

        Returns:
            User's alert preferences
        """
        prefs = await self._preference_repo.get_by_user_id(user_id)
        if not prefs:
            prefs = AlertPreferences(user_id=user_id)
        return prefs

    async def update_preferences(
        self,
        user_id: str,
        *,
        dream_job_threshold: int | None = None,
        interview_reminder_hours: int | None = None,
        daily_digest: bool | None = None,
        enabled_types: list[AlertType] | None = None,
    ) -> AlertPreferences:
        """Update alert preferences.

        Args:
            user_id: User ID
            dream_job_threshold: Min match score for dream job alerts
            interview_reminder_hours: Hours before interview to remind
            daily_digest: Enable daily digest
            enabled_types: List of enabled alert types

        Returns:
            Updated preferences
        """
        current = await self.get_preferences(user_id)

        updated = AlertPreferences(
            user_id=user_id,
            dream_job_threshold=(
                dream_job_threshold
                if dream_job_threshold is not None
                else current.dream_job_threshold
            ),
            interview_reminder_hours=(
                interview_reminder_hours
                if interview_reminder_hours is not None
                else current.interview_reminder_hours
            ),
            daily_digest=(
                daily_digest if daily_digest is not None else current.daily_digest
            ),
            enabled_types=(
                enabled_types if enabled_types is not None else current.enabled_types
            ),
        )

        return await self._preference_repo.upsert(updated)

    # ==========================================================================
    # Alert Creation Helpers
    # ==========================================================================

    async def notify_dream_job_match(
        self,
        *,
        user_id: str,
        job_id: str,
        job_title: str,
        company: str,
        match_score: int,
    ) -> Alert:
        """Create a dream job match alert.

        Args:
            user_id: User ID
            job_id: Job ID
            job_title: Job title
            company: Company name
            match_score: Match score percentage

        Returns:
            Created alert
        """
        return await self.create_alert(
            user_id=user_id,
            alert_type=AlertType.DREAM_JOB_MATCH,
            title=f"Dream Job Alert: {job_title}",
            message=f"{company} is looking for someone like you! {match_score}% match.",
            data={
                "job_id": job_id,
                "job_title": job_title,
                "company": company,
                "match_score": match_score,
            },
        )

    async def notify_application_status_change(
        self,
        *,
        user_id: str,
        application_id: str,
        job_title: str,
        company: str,
        new_status: str,
    ) -> Alert:
        """Create an application status change alert.

        Args:
            user_id: User ID
            application_id: Application ID
            job_title: Job title
            company: Company name
            new_status: New status value

        Returns:
            Created alert
        """
        status_messages = {
            "interview": f"Great news! {company} wants to interview you!",
            "offer": f"Congratulations! {company} made you an offer!",
            "rejected": f"Update from {company} regarding your application.",
            "submitted": f"Your application to {company} was submitted.",
        }

        message = status_messages.get(
            new_status, f"Your application status at {company} has changed."
        )

        return await self.create_alert(
            user_id=user_id,
            alert_type=AlertType.APPLICATION_STATUS_CHANGE,
            title=f"Application Update: {job_title}",
            message=message,
            data={
                "application_id": application_id,
                "job_title": job_title,
                "company": company,
                "new_status": new_status,
            },
        )

    async def notify_interview_reminder(
        self,
        *,
        user_id: str,
        application_id: str,
        job_title: str,
        company: str,
        interview_time: datetime,
    ) -> Alert:
        """Create an interview reminder alert.

        Args:
            user_id: User ID
            application_id: Application ID
            job_title: Job title
            company: Company name
            interview_time: Scheduled interview time

        Returns:
            Created alert
        """
        return await self.create_alert(
            user_id=user_id,
            alert_type=AlertType.INTERVIEW_REMINDER,
            title=f"Interview Reminder: {company}",
            message=f"Your interview for {job_title} is coming up!",
            data={
                "application_id": application_id,
                "job_title": job_title,
                "company": company,
                "interview_time": interview_time.isoformat(),
            },
        )

    async def notify_achievement_unlocked(
        self,
        *,
        user_id: str,
        achievement_id: str,
        achievement_name: str,
        points: int,
    ) -> Alert:
        """Create an achievement unlocked alert.

        Args:
            user_id: User ID
            achievement_id: Achievement ID
            achievement_name: Display name
            points: Points awarded

        Returns:
            Created alert
        """
        return await self.create_alert(
            user_id=user_id,
            alert_type=AlertType.ACHIEVEMENT_UNLOCKED,
            title=f"Achievement Unlocked: {achievement_name}!",
            message=f"You earned {points} points!",
            data={
                "achievement_id": achievement_id,
                "achievement_name": achievement_name,
                "points": points,
            },
        )

    async def notify_campaign_milestone(
        self,
        *,
        user_id: str,
        campaign_id: str,
        campaign_name: str,
        milestone: str,
        value: int,
    ) -> Alert:
        """Create a campaign milestone alert.

        Args:
            user_id: User ID
            campaign_id: Campaign ID
            campaign_name: Campaign name
            milestone: Milestone type (e.g., "applications_sent")
            value: Milestone value

        Returns:
            Created alert
        """
        milestone_messages = {
            "applications_10": f"You've sent 10 applications in {campaign_name}!",
            "applications_25": f"25 applications sent in {campaign_name}! Keep going!",
            "applications_50": f"50 applications! You're crushing it!",
            "first_interview": f"Your first interview from {campaign_name}!",
        }

        message = milestone_messages.get(
            milestone, f"Campaign milestone reached: {milestone}!"
        )

        return await self.create_alert(
            user_id=user_id,
            alert_type=AlertType.CAMPAIGN_MILESTONE,
            title=f"Campaign Milestone: {campaign_name}",
            message=message,
            data={
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "milestone": milestone,
                "value": value,
            },
        )
