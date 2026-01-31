"""Application status monitoring worker.

Standards: python_clean.mdc
- Periodic task for status checking
- Email notifications on status change
"""

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="app.workers.status_monitor.check_application_status")
def check_application_status() -> dict:
    """Check for application status updates.

    This task runs periodically to:
    1. Check for interview invites in user emails (future enhancement)
    2. Update application statuses based on portal checks
    3. Send notifications for status changes
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_check_status_async())
        return result
    finally:
        loop.close()


async def _check_status_async() -> dict:
    """Async status checking implementation."""
    from datetime import datetime, timedelta

    from app.config import get_settings
    from app.core.domain.application import ApplicationStatus
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.user import SQLUserRepository
    from app.infra.db.session import async_session_factory
    from app.infra.notifications.email import EmailService

    settings = get_settings()
    status_changes = 0
    notifications_sent = 0
    errors = 0

    # Initialize email service if API key is available
    email_service = None
    api_key = settings.sendgrid_api_key.get_secret_value()
    if api_key:
        email_service = EmailService(
            api_key=api_key,
            from_email=settings.sendgrid_from_email,
        )

    async with async_session_factory() as session:
        app_repo = SQLApplicationRepository(session=session)
        user_repo = SQLUserRepository(session=session)

        # Get applications that are pending or submitted (active)
        # Check applications submitted in the last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Get all applications that might need status updates
        applications = await app_repo.get_pending_status_check(
            statuses=[
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.PENDING,
            ],
            since=cutoff_date,
        )

        logger.info(
            "status_check_started",
            application_count=len(applications),
        )

        for application in applications:
            try:
                # In a full implementation, this would:
                # 1. Check the ATS portal for status changes
                # 2. Monitor user's email for interview invites (with user consent)
                # 3. Use web scraping to check application portals

                # For now, we'll check if the application needs attention
                # based on time since submission

                days_since_submission = 0
                if application.submitted_at:
                    days_since_submission = (
                        datetime.utcnow() - application.submitted_at
                    ).days

                # Mark as "no response" after 14 days with no update
                if (
                    days_since_submission > 14
                    and application.status == ApplicationStatus.SUBMITTED
                ):
                    old_status = application.status
                    application.status = ApplicationStatus.NO_RESPONSE
                    await app_repo.update(application)
                    status_changes += 1

                    # Send notification
                    if email_service:
                        try:
                            user = await user_repo.get_by_id(application.user_id)
                            if user:
                                await email_service.send_application_status_update(
                                    to=user.email,
                                    job_title=application.job_title or "Unknown",
                                    company=application.company or "Unknown",
                                    old_status=old_status.value,
                                    new_status=application.status.value,
                                )
                                notifications_sent += 1
                        except Exception as e:
                            logger.warning(
                                "notification_failed",
                                application_id=application.id,
                                error=str(e),
                            )

            except Exception as e:
                logger.warning(
                    "status_check_error",
                    application_id=application.id,
                    error=str(e),
                )
                errors += 1

        await session.commit()

    logger.info(
        "status_check_completed",
        status_changes=status_changes,
        notifications_sent=notifications_sent,
        errors=errors,
    )

    return {
        "status": "success",
        "status_changes": status_changes,
        "notifications_sent": notifications_sent,
        "errors": errors,
    }


@celery_app.task(name="app.workers.status_monitor.send_daily_summaries")
def send_daily_summaries() -> dict:
    """Send daily summary emails to users."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_send_summaries_async())
        return result
    finally:
        loop.close()


async def _send_summaries_async() -> dict:
    """Async daily summary implementation."""
    from datetime import datetime, timedelta

    from app.config import get_settings
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.user import SQLUserRepository
    from app.infra.db.session import async_session_factory
    from app.infra.notifications.email import EmailService

    settings = get_settings()
    summaries_sent = 0
    errors = 0

    # Initialize email service
    api_key = settings.sendgrid_api_key.get_secret_value()
    if not api_key:
        logger.warning("sendgrid_not_configured")
        return {"status": "skipped", "reason": "SendGrid not configured"}

    email_service = EmailService(
        api_key=api_key,
        from_email=settings.sendgrid_from_email,
    )

    yesterday = datetime.utcnow() - timedelta(days=1)

    async with async_session_factory() as session:
        user_repo = SQLUserRepository(session=session)
        app_repo = SQLApplicationRepository(session=session)

        # Get all active users (simplified - would need preference check)
        users = await user_repo.get_all_active()

        for user in users:
            try:
                # Get user's daily stats
                stats = await app_repo.get_daily_stats(
                    user_id=user.id,
                    date=yesterday,
                )

                # Only send if there's activity
                if stats["applications_submitted"] > 0 or stats["interviews"] > 0:
                    await email_service.send_daily_summary(
                        to=user.email,
                        date=yesterday,
                        applications_submitted=stats["applications_submitted"],
                        interviews_scheduled=stats["interviews"],
                        new_matches=stats["new_matches"],
                    )
                    summaries_sent += 1

            except Exception as e:
                logger.warning(
                    "summary_send_failed",
                    user_id=user.id,
                    error=str(e),
                )
                errors += 1

    logger.info(
        "daily_summaries_sent",
        count=summaries_sent,
        errors=errors,
    )

    return {
        "status": "success",
        "summaries_sent": summaries_sent,
        "errors": errors,
    }


# Register scheduled tasks
celery_app.conf.beat_schedule["check-status-daily"] = {
    "task": "app.workers.status_monitor.check_application_status",
    "schedule": 86400.0,  # Daily
}

celery_app.conf.beat_schedule["send-daily-summaries"] = {
    "task": "app.workers.status_monitor.send_daily_summaries",
    "schedule": 86400.0,  # Daily
}
