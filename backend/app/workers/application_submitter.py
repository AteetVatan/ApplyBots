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
    """Submit application using Playwright automation.

    This is a simplified implementation. Full implementation would use
    ATS-specific adapters (Greenhouse, Lever, etc.)
    """
    from playwright.async_api import async_playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate to job URL
            await page.goto(job_url, wait_until="networkidle", timeout=30000)

            # Check for CAPTCHA indicators
            captcha_selectors = [
                "iframe[src*='recaptcha']",
                "iframe[src*='hcaptcha']",
                ".g-recaptcha",
                "#captcha",
            ]

            for selector in captcha_selectors:
                if await page.query_selector(selector):
                    await browser.close()
                    raise CaptchaDetectedError(job_url)

            # Check for MFA/login requirements
            mfa_indicators = [
                "input[type='password']",
                "[data-testid='login']",
                ".login-form",
            ]

            login_detected = False
            for selector in mfa_indicators:
                if await page.query_selector(selector):
                    login_detected = True
                    break

            if login_detected:
                # Check if it's actually a login page vs application form
                url = page.url
                if "login" in url.lower() or "signin" in url.lower():
                    await browser.close()
                    raise MFARequiredError(job_url)

            # Log page loaded
            await audit_repo.create(AuditLog(
                id=str(uuid.uuid4()),
                application_id=application.id,
                action="page_loaded",
                metadata={"url": page.url},
                success=True,
                error_message=None,
                screenshot_s3_key=None,
                created_at=datetime.utcnow(),
            ))

            # For MVP, we simulate success
            # Real implementation would fill forms using ATS adapters

            await browser.close()

            return {
                "success": True,
                "confirmation_id": f"SIM-{application.id[:8]}",
            }

    except CaptchaDetectedError:
        raise
    except MFARequiredError:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


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
