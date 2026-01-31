"""Applications endpoints.

Standards: python_clean.mdc
- Thin controller layer
- Proper error handling
"""

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.domain.application import ApplicationStatus
from app.core.exceptions import PlanLimitExceededError
from app.schemas.application import (
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationSummaryResponse,
    ApproveRequest,
    AuditStepResponse,
    CreateApplicationRequest,
    EditApplicationRequest,
)

router = APIRouter()
logger = structlog.get_logger()


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ApplicationListResponse:
    """List user's applications."""
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository

    app_repo = SQLApplicationRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    # Parse status filter
    app_status = None
    if status_filter:
        try:
            app_status = ApplicationStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}",
            )

    offset = (page - 1) * limit
    applications = await app_repo.get_by_user_id(
        current_user.id,
        status=app_status,
        limit=limit + 1,
        offset=offset,
    )

    has_more = len(applications) > limit
    applications = applications[:limit]

    # Get job details for each application
    items = []
    for app in applications:
        job = await job_repo.get_by_id(app.job_id)
        if job:
            items.append(ApplicationSummaryResponse(
                id=app.id,
                job_id=app.job_id,
                job_title=job.title,
                company=job.company,
                status=app.status.value,
                match_score=app.match_score,
                created_at=app.created_at,
                submitted_at=app.submitted_at,
            ))

    # Get total count
    all_apps = await app_repo.get_by_user_id(current_user.id, status=app_status)
    total = len(all_apps)

    return ApplicationListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


@router.post("", response_model=ApplicationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: CreateApplicationRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> ApplicationDetailResponse:
    """Create a new application (add to review queue)."""
    from app.core.services.plan_gating import PlanGatingService
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.db.repositories.subscription import SQLSubscriptionRepository
    from app.infra.services.application_service import ApplicationService

    job_repo = SQLJobRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)
    app_repo = SQLApplicationRepository(session=db)
    sub_repo = SQLSubscriptionRepository(session=db)

    # Check plan limits
    subscription = await sub_repo.get_by_user_id(current_user.id)
    if subscription:
        gating = PlanGatingService()
        try:
            gating.check_daily_limit(subscription=subscription)
        except PlanLimitExceededError as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e),
            )

    # Get job
    job = await job_repo.get_by_id(request.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Get resume
    resume_id = request.resume_id
    if not resume_id:
        resume = await resume_repo.get_primary(user_id=current_user.id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No resume available. Please upload a resume first.",
            )
        resume_id = resume.id
    else:
        resume = await resume_repo.get_by_id(resume_id)
        if not resume or resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

    # Create application via service
    app_service = ApplicationService(
        application_repository=app_repo,
        job_repository=job_repo,
        resume_repository=resume_repo,
    )

    application = await app_service.create_application(
        user_id=current_user.id,
        job_id=request.job_id,
        resume_id=resume_id,
    )

    logger.info(
        "application_created",
        user_id=current_user.id,
        application_id=application.id,
        job_id=request.job_id,
    )

    return ApplicationDetailResponse(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=[],
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        error_message=application.error_message,
        job_title=job.title,
        company=job.company,
        job_url=job.url,
    )


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> ApplicationDetailResponse:
    """Get application details with audit trail."""
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.audit import SQLAuditRepository
    from app.infra.db.repositories.job import SQLJobRepository

    app_repo = SQLApplicationRepository(session=db)
    job_repo = SQLJobRepository(session=db)
    audit_repo = SQLAuditRepository(session=db)

    application = await app_repo.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    job = await job_repo.get_by_id(application.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Get audit trail
    audit_logs = await audit_repo.get_by_application_id(application_id)
    audit_trail = [
        AuditStepResponse(
            action=log.action,
            selector=log.metadata.get("selector") if log.metadata else None,
            success=log.success,
            error_message=log.error_message,
            screenshot_url=None,  # Would need presigned URL
            timestamp=log.created_at,
        )
        for log in audit_logs
    ]

    return ApplicationDetailResponse(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=audit_trail,
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        error_message=application.error_message,
        job_title=job.title,
        company=job.company,
        job_url=job.url,
    )


@router.post("/{application_id}/approve", response_model=ApplicationDetailResponse)
async def approve_application(
    application_id: str,
    request: ApproveRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ApplicationDetailResponse:
    """Approve and submit an application."""
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository

    # Try to import celery task, but continue without it if not available
    submit_application_task = None
    try:
        from app.workers.application_submitter import submit_application_task as task
        submit_application_task = task
    except ImportError:
        logger.warning("celery_not_available_for_submission", application_id=application_id)

    app_repo = SQLApplicationRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    application = await app_repo.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.status != ApplicationStatus.PENDING_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve application in status: {application.status.value}",
        )

    # Update with any overrides
    if request.cover_letter:
        application.cover_letter = request.cover_letter
    if request.answers:
        application.generated_answers.update(request.answers)

    application.status = ApplicationStatus.APPROVED
    await app_repo.update(application)

    # Queue submission task if available
    if submit_application_task:
        submit_application_task.delay(application_id=application_id)
        logger.info("application_submission_queued", application_id=application_id)
    else:
        logger.warning("application_submission_skipped_no_celery", application_id=application_id)

    logger.info(
        "application_approved",
        user_id=current_user.id,
        application_id=application_id,
    )

    job = await job_repo.get_by_id(application.job_id)

    return ApplicationDetailResponse(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=[],
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        error_message=application.error_message,
        job_title=job.title if job else "",
        company=job.company if job else "",
        job_url=job.url if job else "",
    )


@router.put("/{application_id}/edit", response_model=ApplicationDetailResponse)
async def edit_application(
    application_id: str,
    request: EditApplicationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ApplicationDetailResponse:
    """Edit application content before approval."""
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository

    app_repo = SQLApplicationRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    application = await app_repo.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if application.status not in [ApplicationStatus.PENDING_REVIEW, ApplicationStatus.MANUAL_NEEDED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit application in status: {application.status.value}",
        )

    # Update content
    if request.cover_letter is not None:
        application.cover_letter = request.cover_letter
    if request.answers is not None:
        application.generated_answers.update(request.answers)

    await app_repo.update(application)

    logger.info(
        "application_edited",
        user_id=current_user.id,
        application_id=application_id,
    )

    job = await job_repo.get_by_id(application.job_id)

    return ApplicationDetailResponse(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=[],
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        error_message=application.error_message,
        job_title=job.title if job else "",
        company=job.company if job else "",
        job_url=job.url if job else "",
    )


@router.post("/{application_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_application(
    application_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Reject/remove an application from the queue."""
    from app.infra.db.repositories.application import SQLApplicationRepository

    app_repo = SQLApplicationRepository(session=db)

    application = await app_repo.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application.status = ApplicationStatus.REJECTED
    await app_repo.update(application)

    logger.info(
        "application_rejected",
        user_id=current_user.id,
        application_id=application_id,
    )
