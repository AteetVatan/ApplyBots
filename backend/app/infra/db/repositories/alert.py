"""Alert repository implementation.

Standards: python_clean.mdc
- Async operations
- Type hints
"""

from datetime import datetime
from typing import Sequence

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.alert import Alert, AlertPreferences, AlertType
from app.infra.db.models import AlertModel, AlertPreferenceModel, generate_cuid

logger = structlog.get_logger(__name__)


class SQLAlertRepository:
    """SQL repository for alerts."""

    def __init__(self, *, session: AsyncSession) -> None:
        self._session = session

    async def create(self, alert: Alert) -> Alert:
        """Create a new alert."""
        model = AlertModel(
            id=alert.id or generate_cuid(),
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            title=alert.title,
            message=alert.message,
            data=alert.data,
            read=alert.read,
            created_at=alert.created_at,
        )
        self._session.add(model)
        await self._session.flush()

        logger.info(
            "alert_created",
            alert_id=model.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type.value,
        )

        return self._to_domain(model)

    async def get_by_id(self, alert_id: str) -> Alert | None:
        """Get alert by ID."""
        result = await self._session.execute(
            select(AlertModel).where(AlertModel.id == alert_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Alert]:
        """Get alerts for a user."""
        query = (
            select(AlertModel)
            .where(AlertModel.user_id == user_id)
            .order_by(AlertModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if unread_only:
            query = query.where(AlertModel.read == False)  # noqa: E712

        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread alerts."""
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count(AlertModel.id))
            .where(AlertModel.user_id == user_id)
            .where(AlertModel.read == False)  # noqa: E712
        )
        return result.scalar() or 0

    async def mark_read(self, alert_id: str) -> bool:
        """Mark an alert as read."""
        result = await self._session.execute(
            update(AlertModel)
            .where(AlertModel.id == alert_id)
            .values(read=True)
        )
        return result.rowcount > 0

    async def mark_all_read(self, user_id: str) -> int:
        """Mark all alerts as read for a user."""
        result = await self._session.execute(
            update(AlertModel)
            .where(AlertModel.user_id == user_id)
            .where(AlertModel.read == False)  # noqa: E712
            .values(read=True)
        )
        return result.rowcount

    async def delete_old_alerts(
        self,
        *,
        older_than: datetime,
        read_only: bool = True,
    ) -> int:
        """Delete old alerts."""
        from sqlalchemy import delete

        query = delete(AlertModel).where(AlertModel.created_at < older_than)
        if read_only:
            query = query.where(AlertModel.read == True)  # noqa: E712

        result = await self._session.execute(query)
        return result.rowcount

    def _to_domain(self, model: AlertModel) -> Alert:
        """Convert model to domain entity."""
        return Alert(
            id=model.id,
            user_id=model.user_id,
            alert_type=model.alert_type,
            title=model.title,
            message=model.message,
            data=model.data or {},
            read=model.read,
            created_at=model.created_at,
        )


class SQLAlertPreferenceRepository:
    """SQL repository for alert preferences."""

    def __init__(self, *, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> AlertPreferences | None:
        """Get alert preferences for a user."""
        result = await self._session.execute(
            select(AlertPreferenceModel).where(AlertPreferenceModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def upsert(self, preferences: AlertPreferences) -> AlertPreferences:
        """Create or update alert preferences."""
        existing = await self.get_by_user_id(preferences.user_id)

        if existing:
            await self._session.execute(
                update(AlertPreferenceModel)
                .where(AlertPreferenceModel.user_id == preferences.user_id)
                .values(
                    dream_job_threshold=preferences.dream_job_threshold,
                    interview_reminder_hours=preferences.interview_reminder_hours,
                    daily_digest=preferences.daily_digest,
                    enabled_types=[t.value for t in preferences.enabled_types],
                )
            )
            return preferences

        model = AlertPreferenceModel(
            id=generate_cuid(),
            user_id=preferences.user_id,
            dream_job_threshold=preferences.dream_job_threshold,
            interview_reminder_hours=preferences.interview_reminder_hours,
            daily_digest=preferences.daily_digest,
            enabled_types=[t.value for t in preferences.enabled_types],
        )
        self._session.add(model)
        await self._session.flush()

        return self._to_domain(model)

    async def get_users_with_dream_job_alerts(
        self,
        min_threshold: int = 0,
    ) -> Sequence[AlertPreferences]:
        """Get all users who want dream job alerts."""
        result = await self._session.execute(
            select(AlertPreferenceModel).where(
                AlertPreferenceModel.dream_job_threshold >= min_threshold
            )
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    def _to_domain(self, model: AlertPreferenceModel) -> AlertPreferences:
        """Convert model to domain entity."""
        enabled_types = [AlertType(t) for t in (model.enabled_types or [])]
        if not enabled_types:
            enabled_types = list(AlertType)

        return AlertPreferences(
            user_id=model.user_id,
            dream_job_threshold=model.dream_job_threshold,
            interview_reminder_hours=model.interview_reminder_hours,
            daily_digest=model.daily_digest,
            enabled_types=enabled_types,
        )
