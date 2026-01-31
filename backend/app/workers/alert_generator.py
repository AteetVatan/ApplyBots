"""Alert generation worker for background processing.

Standards: python_clean.mdc
- Async operations via sync_to_async
- Structured logging
"""

import structlog
from celery import shared_task

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.workers.alert_generator.check_dream_jobs")
def check_dream_jobs(job_id: str) -> dict:
    """Check if a newly ingested job matches any user's dream job criteria.

    Called when a new job is ingested to find users who should be alerted.

    Args:
        job_id: ID of the newly ingested job

    Returns:
        Dict with count of alerts created
    """
    import asyncio

    async def _check():
        from app.config import get_settings
        from app.core.services.alerts import AlertService
        from app.core.services.matcher import MatchService
        from app.infra.db.repositories.alert import (
            SQLAlertPreferenceRepository,
            SQLAlertRepository,
        )
        from app.infra.db.repositories.job import SQLJobRepository
        from app.infra.db.repositories.resume import SQLResumeRepository
        from app.infra.db.session import async_session_factory

        settings = get_settings()
        alerts_created = 0

        async with async_session_factory() as session:
            job_repo = SQLJobRepository(session=session)
            resume_repo = SQLResumeRepository(session=session)
            alert_repo = SQLAlertRepository(session=session)
            pref_repo = SQLAlertPreferenceRepository(session=session)

            # Get the job
            job = await job_repo.get_by_id(job_id)
            if not job:
                logger.warning("dream_job_check_job_not_found", job_id=job_id)
                return {"alerts_created": 0}

            # Get all users with dream job alert preferences
            preferences = await pref_repo.get_users_with_dream_job_alerts(min_threshold=80)

            match_service = MatchService()
            alert_service = AlertService(
                alert_repo=alert_repo,
                preference_repo=pref_repo,
            )

            for pref in preferences:
                try:
                    # Get user's primary resume
                    resume = await resume_repo.get_primary(user_id=pref.user_id)
                    if not resume or not resume.parsed_data:
                        continue

                    # Calculate match score
                    score, _ = match_service.calculate_score(
                        resume=resume.parsed_data,
                        job=job,
                    )

                    # Check if score meets user's threshold
                    if score >= pref.dream_job_threshold:
                        await alert_service.notify_dream_job_match(
                            user_id=pref.user_id,
                            job_id=job.id,
                            job_title=job.title,
                            company=job.company,
                            match_score=score,
                        )
                        alerts_created += 1

                        logger.info(
                            "dream_job_alert_created",
                            user_id=pref.user_id,
                            job_id=job_id,
                            match_score=score,
                        )

                except Exception as e:
                    logger.warning(
                        "dream_job_check_user_error",
                        user_id=pref.user_id,
                        error=str(e),
                    )
                    continue

            await session.commit()

        return {"alerts_created": alerts_created}

    return asyncio.run(_check())


@celery_app.task(name="app.workers.alert_generator.check_application_milestones")
def check_application_milestones(user_id: str, campaign_id: str | None = None) -> dict:
    """Check if user has reached any application milestones.

    Args:
        user_id: User ID to check
        campaign_id: Optional campaign ID for campaign-specific milestones

    Returns:
        Dict with milestones reached
    """
    import asyncio

    async def _check():
        from app.core.services.alerts import AlertService
        from app.infra.db.repositories.alert import (
            SQLAlertPreferenceRepository,
            SQLAlertRepository,
        )
        from app.infra.db.repositories.application import SQLApplicationRepository
        from app.infra.db.session import async_session_factory

        milestones_reached = []

        async with async_session_factory() as session:
            app_repo = SQLApplicationRepository(session=session)
            alert_repo = SQLAlertRepository(session=session)
            pref_repo = SQLAlertPreferenceRepository(session=session)

            # Get application count
            applications = await app_repo.get_by_user_id(user_id)
            total_count = len(applications)

            # Check milestone thresholds
            milestone_thresholds = [10, 25, 50, 100]

            for threshold in milestone_thresholds:
                if total_count == threshold:
                    alert_service = AlertService(
                        alert_repo=alert_repo,
                        preference_repo=pref_repo,
                    )

                    if campaign_id:
                        await alert_service.notify_campaign_milestone(
                            user_id=user_id,
                            campaign_id=campaign_id,
                            campaign_name="Your Campaign",
                            milestone=f"applications_{threshold}",
                            value=threshold,
                        )
                    else:
                        await alert_service.create_alert(
                            user_id=user_id,
                            alert_type=alert_service._alert_repo.__class__.__name__,
                            title=f"Milestone: {threshold} Applications!",
                            message=f"You've submitted {threshold} applications! Keep going!",
                            data={"milestone": f"applications_{threshold}", "count": threshold},
                        )

                    milestones_reached.append(f"applications_{threshold}")
                    break

            await session.commit()

        return {"milestones": milestones_reached}

    return asyncio.run(_check())


@celery_app.task(name="app.workers.alert_generator.send_interview_reminders")
def send_interview_reminders() -> dict:
    """Send interview reminders to users with upcoming interviews.

    Should be scheduled to run periodically (e.g., every hour).

    Returns:
        Dict with count of reminders sent
    """
    import asyncio
    from datetime import datetime, timedelta

    async def _send():
        from app.core.domain.application import ApplicationStage
        from app.core.services.alerts import AlertService
        from app.infra.db.repositories.alert import (
            SQLAlertPreferenceRepository,
            SQLAlertRepository,
        )
        from app.infra.db.repositories.application import SQLApplicationRepository
        from app.infra.db.session import async_session_factory

        reminders_sent = 0

        async with async_session_factory() as session:
            app_repo = SQLApplicationRepository(session=session)
            alert_repo = SQLAlertRepository(session=session)
            pref_repo = SQLAlertPreferenceRepository(session=session)

            alert_service = AlertService(
                alert_repo=alert_repo,
                preference_repo=pref_repo,
            )

            # Get all users with alert preferences
            preferences = await pref_repo.get_users_with_dream_job_alerts(min_threshold=0)

            for pref in preferences:
                try:
                    # Get applications in interview stage
                    applications = await app_repo.get_by_user_id(pref.user_id)
                    interviewing = [
                        a for a in applications
                        if a.stage == ApplicationStage.INTERVIEWING
                    ]

                    # This is a simplified check - in production you'd have
                    # interview datetime stored and check against that
                    for app in interviewing:
                        if app.stage_updated_at:
                            hours_since_update = (
                                datetime.utcnow() - app.stage_updated_at
                            ).total_seconds() / 3600

                            # Send reminder if stage updated recently (mock interview timing)
                            if hours_since_update >= (pref.interview_reminder_hours - 1):
                                await alert_service.notify_interview_reminder(
                                    user_id=pref.user_id,
                                    application_id=app.id,
                                    job_title=app.job_id,  # Would need job lookup
                                    company="Company",  # Would need job lookup
                                    interview_time=datetime.utcnow() + timedelta(hours=1),
                                )
                                reminders_sent += 1

                except Exception as e:
                    logger.warning(
                        "interview_reminder_error",
                        user_id=pref.user_id,
                        error=str(e),
                    )
                    continue

            await session.commit()

        return {"reminders_sent": reminders_sent}

    return asyncio.run(_send())


@celery_app.task(name="app.workers.alert_generator.cleanup_old_alerts")
def cleanup_old_alerts(days: int = 30) -> dict:
    """Clean up old read alerts.

    Args:
        days: Delete read alerts older than this many days

    Returns:
        Dict with count of deleted alerts
    """
    import asyncio
    from datetime import datetime, timedelta

    async def _cleanup():
        from app.infra.db.repositories.alert import SQLAlertRepository
        from app.infra.db.session import async_session_factory

        async with async_session_factory() as session:
            alert_repo = SQLAlertRepository(session=session)

            cutoff = datetime.utcnow() - timedelta(days=days)
            deleted = await alert_repo.delete_old_alerts(
                older_than=cutoff,
                read_only=True,
            )

            await session.commit()

            logger.info("old_alerts_cleaned", deleted_count=deleted, days=days)

            return {"deleted": deleted}

    return asyncio.run(_cleanup())
