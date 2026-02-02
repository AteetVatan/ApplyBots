"""Application submission worker tasks.

Standards: python_clean.mdc
- Async Playwright automation
- Proper error handling and audit logging
"""

import uuid
from datetime import datetime

import structlog

from app.core.domain.application import ApplicationStatus
from app.core.exceptions import CaptchaDetectedError, MFARequiredError
from app.workers.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="app.workers.application_submitter.submit_application_task")
def submit_application_task(application_id: str) -> dict:
    """Submit a single application via Playwright automation."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_submit_application_async(application_id))
        return result
    finally:
        loop.close()


@celery_app.task(name="app.workers.application_submitter.bulk_apply_task")
def bulk_apply_task(
    user_id: str,
    job_ids: list[str],
    resume_id: str | None = None,
    auto_submit: bool = False,
) -> dict:
    """Queue multiple applications."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            _bulk_apply_async(user_id, job_ids, resume_id, auto_submit)
        )
        return result
    finally:
        loop.close()


async def _submit_application_async(application_id: str) -> dict:
    """Async application submission."""
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.audit import AuditLog, SQLAuditRepository
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        app_repo = SQLApplicationRepository(session=session)
        job_repo = SQLJobRepository(session=session)
        audit_repo = SQLAuditRepository(session=session)

        application = await app_repo.get_by_id(application_id)
        if not application:
            return {"status": "error", "error": "Application not found"}

        job = await job_repo.get_by_id(application.job_id)
        if not job:
            return {"status": "error", "error": "Job not found"}

        # Update status to submitting
        application.status = ApplicationStatus.SUBMITTING
        await app_repo.update(application)
        await session.commit()

        # Log start
        await audit_repo.create(AuditLog(
            id=str(uuid.uuid4()),
            application_id=application_id,
            action="submission_started",
            metadata={"job_url": job.url},
            success=True,
            error_message=None,
            screenshot_s3_key=None,
            created_at=datetime.utcnow(),
        ))

        try:
            # Determine ATS type and submit
            result = await _submit_via_playwright(
                job_url=job.url,
                application=application,
                job=job,
                audit_repo=audit_repo,
            )

            if result["success"]:
                application.status = ApplicationStatus.SUBMITTED
                application.submitted_at = datetime.utcnow()
            elif result.get("manual_needed"):
                application.status = ApplicationStatus.MANUAL_NEEDED
                application.error_message = result.get("error")
            else:
                application.status = ApplicationStatus.FAILED
                application.error_message = result.get("error")

            await app_repo.update(application)
            await session.commit()

            # Log completion
            await audit_repo.create(AuditLog(
                id=str(uuid.uuid4()),
                application_id=application_id,
                action="submission_completed",
                metadata=result,
                success=result["success"],
                error_message=result.get("error"),
                screenshot_s3_key=None,
                created_at=datetime.utcnow(),
            ))
            await session.commit()

            # Send email notification if enabled (check campaign settings)
            if result["success"]:
                await _send_application_email_if_enabled(
                    session=session,
                    application=application,
                    job=job,
                )

            logger.info(
                "application_submitted",
                application_id=application_id,
                success=result["success"],
            )

            return result

        except CaptchaDetectedError as e:
            application.status = ApplicationStatus.MANUAL_NEEDED
            application.error_message = "CAPTCHA detected - manual intervention required"
            await app_repo.update(application)
            await session.commit()

            logger.warning("captcha_detected", application_id=application_id, url=e.url)

            return {"success": False, "manual_needed": True, "error": str(e)}

        except MFARequiredError as e:
            application.status = ApplicationStatus.MANUAL_NEEDED
            application.error_message = "MFA required - manual intervention required"
            await app_repo.update(application)
            await session.commit()

            logger.warning("mfa_required", application_id=application_id, url=e.url)

            return {"success": False, "manual_needed": True, "error": str(e)}

        except Exception as e:
            application.status = ApplicationStatus.FAILED
            application.error_message = str(e)
            await app_repo.update(application)
            await session.commit()

            logger.error("submission_failed", application_id=application_id, error=str(e))

            return {"success": False, "error": str(e)}


async def _submit_via_playwright(
    job_url: str,
    application,
    job,
    audit_repo,
) -> dict:
    """Submit application using Playwright automation with ATS adapters.

    Uses ATS-specific adapters (Greenhouse, Lever) for form filling.
    Falls back to manual submission needed if ATS not supported.
    """
    from playwright.async_api import async_playwright

    from app.config import get_settings
    from app.core.ports.ats import ApplicationData
    from app.infra.ats_adapters.greenhouse import GreenhouseAdapter
    from app.infra.ats_adapters.lever import LeverAdapter
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.db.session import async_session_factory
    from app.infra.storage.s3 import S3Storage

    settings = get_settings()
    storage = S3Storage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key.get_secret_value(),
        secret_key=settings.s3_secret_key.get_secret_value(),
        bucket=settings.s3_bucket,
        region=settings.s3_region,
    )

    # Initialize available ATS adapters
    adapters = [
        GreenhouseAdapter(storage=storage, application_id=application.id),
        LeverAdapter(storage=storage, application_id=application.id),
    ]

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            page = await context.new_page()

            # Navigate to job URL
            await page.goto(job_url, wait_until="networkidle", timeout=30000)

            # Log page loaded
            await audit_repo.create(AuditLog(
                id=str(uuid.uuid4()),
                application_id=application.id,
                action="page_loaded",
                metadata={"url": page.url, "title": await page.title()},
                success=True,
                error_message=None,
                screenshot_s3_key=None,
                created_at=datetime.utcnow(),
            ))

            # Detect which ATS to use
            adapter = None
            for a in adapters:
                if await a.detect(url=page.url):
                    adapter = a
                    logger.info(
                        "ats_detected",
                        ats=a.name,
                        application_id=application.id,
                    )
                    break

            if not adapter:
                # No supported ATS detected - requires manual submission
                await browser.close()
                return {
                    "success": False,
                    "manual_needed": True,
                    "error": f"Unsupported ATS: {page.url}",
                }

            # Check for blockers (CAPTCHA, MFA)
            await adapter.check_blockers(page=page)

            # Prepare application data
            async with async_session_factory() as session:
                resume_repo = SQLResumeRepository(session=session)
                profile_repo = SQLProfileRepository(session=session)

                resume = await resume_repo.get_by_id(application.resume_id)
                profile = await profile_repo.get_by_user_id(application.user_id)

                if not resume:
                    await browser.close()
                    return {"success": False, "error": "Resume not found"}

                # Download resume file for upload
                resume_bytes = await storage.download(key=resume.s3_key)
                resume_path = f"/tmp/{application.id}_resume.pdf"

                with open(resume_path, "wb") as f:
                    f.write(resume_bytes)

                # Build application data
                parsed = resume.parsed_data
                app_data = ApplicationData(
                    first_name=_extract_first_name(parsed.full_name) if parsed else "",
                    last_name=_extract_last_name(parsed.full_name) if parsed else "",
                    email=parsed.email if parsed else (profile.email if profile else ""),
                    phone=parsed.phone if parsed else (profile.phone if profile else ""),
                    location=parsed.location if parsed else (profile.location if profile else ""),
                    resume_path=resume_path,
                    linkedin_url=profile.linkedin_url if profile else None,
                    portfolio_url=profile.portfolio_url if profile else None,
                    cover_letter=application.cover_letter,
                    answers=application.generated_answers or {},
                )

            # Fill the form
            await adapter.fill_form(page=page, data=app_data)

            # Log form filled
            await audit_repo.create(AuditLog(
                id=str(uuid.uuid4()),
                application_id=application.id,
                action="form_filled",
                metadata={"ats": adapter.name},
                success=True,
                error_message=None,
                screenshot_s3_key=None,
                created_at=datetime.utcnow(),
            ))

            # Submit the application
            result = await adapter.submit(page=page)

            # Store final screenshot
            if adapter.get_screenshots():
                await audit_repo.create(AuditLog(
                    id=str(uuid.uuid4()),
                    application_id=application.id,
                    action="submission_screenshot",
                    metadata={"screenshots": adapter.get_screenshots()},
                    success=True,
                    error_message=None,
                    screenshot_s3_key=adapter.get_screenshots()[-1],
                    created_at=datetime.utcnow(),
                ))

            await browser.close()

            return {
                "success": result.success,
                "confirmation_id": result.confirmation_id,
                "audit_trail": [
                    {
                        "action": step.action,
                        "success": step.success,
                        "timestamp": step.timestamp.isoformat(),
                    }
                    for step in adapter.get_audit_trail()
                ],
                "screenshots": adapter.get_screenshots(),
            }

    except CaptchaDetectedError:
        raise
    except MFARequiredError:
        raise
    except Exception as e:
        logger.error("playwright_submission_error", error=str(e), exc_info=True)
        return {"success": False, "error": str(e)}


def _extract_first_name(full_name: str | None) -> str:
    """Extract first name from full name."""
    if not full_name:
        return ""
    parts = full_name.strip().split()
    return parts[0] if parts else ""


def _extract_last_name(full_name: str | None) -> str:
    """Extract last name from full name."""
    if not full_name:
        return ""
    parts = full_name.strip().split()
    return parts[-1] if len(parts) > 1 else ""


async def _bulk_apply_async(
    user_id: str,
    job_ids: list[str],
    resume_id: str | None,
    auto_submit: bool,
) -> dict:
    """Create applications for multiple jobs."""
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.db.session import async_session_factory
    from app.infra.services.application_service import ApplicationService
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository

    created = 0
    errors = 0

    async with async_session_factory() as session:
        app_repo = SQLApplicationRepository(session=session)
        job_repo = SQLJobRepository(session=session)
        resume_repo = SQLResumeRepository(session=session)

        app_service = ApplicationService(
            application_repository=app_repo,
            job_repository=job_repo,
            resume_repository=resume_repo,
        )

        # Get resume
        if resume_id:
            resume = await resume_repo.get_by_id(resume_id)
        else:
            resume = await resume_repo.get_primary(user_id=user_id)

        if not resume:
            return {"status": "error", "error": "No resume available"}

        for job_id in job_ids:
            try:
                application = await app_service.create_application(
                    user_id=user_id,
                    job_id=job_id,
                    resume_id=resume.id,
                )
                created += 1

                # Auto-submit if requested
                if auto_submit:
                    application.status = ApplicationStatus.APPROVED
                    await app_repo.update(application)
                    submit_application_task.delay(application_id=application.id)

            except Exception as e:
                logger.warning("bulk_apply_error", job_id=job_id, error=str(e))
                errors += 1

        await session.commit()

    logger.info(
        "bulk_apply_complete",
        user_id=user_id,
        created=created,
        errors=errors,
        auto_submit=auto_submit,
    )

    return {
        "status": "success",
        "created": created,
        "errors": errors,
    }


# Import for type hints
from app.infra.db.repositories.audit import AuditLog


async def _send_application_email_if_enabled(
    session,
    application,
    job,
) -> None:
    """Send application email if campaign allows it or no campaign.

    By default, no email per application is sent (per product requirement).
    Email is only sent if campaign.send_per_app_email is True.
    """
    from app.config import get_settings
    from app.infra.db.models import CampaignJobModel
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.repositories.user import SQLUserRepository
    from app.infra.notifications.email import EmailService
    from sqlalchemy import select

    settings = get_settings()

    # Check if email service is configured
    sendgrid_key = settings.sendgrid_api_key.get_secret_value()
    if not sendgrid_key:
        return

    # Check if this job is part of any campaign
    stmt = select(CampaignJobModel).where(
        CampaignJobModel.job_id == application.job_id
    )
    result = await session.execute(stmt)
    campaign_job = result.scalar_one_or_none()

    should_send_email = False

    if campaign_job:
        # Job is part of a campaign - check campaign settings
        campaign_repo = SQLCampaignRepository(session=session)
        campaign = await campaign_repo.get_by_id(campaign_job.campaign_id)

        if campaign and campaign.send_per_app_email:
            should_send_email = True
            logger.debug(
                "email_enabled_by_campaign",
                campaign_id=campaign.id,
                application_id=application.id,
            )
    else:
        # Not part of any campaign - check if it's a manual application
        # For manual applications (not via campaign), don't send email by default
        # This matches the product behavior: "do not expect email confirmation"
        should_send_email = False

    if not should_send_email:
        logger.debug(
            "email_skipped",
            application_id=application.id,
            reason="per_app_email_disabled",
        )
        return

    # Send the email
    try:
        user_repo = SQLUserRepository(session=session)
        user = await user_repo.get_by_id(application.user_id)

        if user:
            email_service = EmailService(
                api_key=sendgrid_key,
                from_email=settings.sendgrid_from_email,
            )

            await email_service.send_application_submitted(
                to=user.email,
                job_title=job.title,
                company=job.company,
                application_id=application.id,
            )

            logger.info(
                "application_email_sent",
                application_id=application.id,
                user_id=user.id,
            )

    except Exception as e:
        logger.warning(
            "application_email_failed",
            application_id=application.id,
            error=str(e),
        )
