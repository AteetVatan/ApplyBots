"""Applications endpoints.

Standards: python_clean.mdc
- Thin controller layer
- Proper error handling
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.domain.application import ApplicationStage, ApplicationStatus

if TYPE_CHECKING:
    from app.config import Settings
    from app.core.domain.job import Job
from app.core.exceptions import PlanLimitExceededError
from app.schemas.application import (
    AddNoteRequest,
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationSummaryResponse,
    ApproveRequest,
    AuditStepResponse,
    CreateApplicationRequest,
    EditApplicationRequest,
    GroupedApplicationsResponse,
    NoteResponse,
    StageItemsResponse,
    UpdateStageRequest,
)

router = APIRouter()
logger = structlog.get_logger()


async def _record_answer_edits_for_learning(
    *,
    user_id: str,
    original_answers: dict[str, str],
    edited_answers: dict[str, str],
    job: "Job",
    settings: "Settings",
) -> None:
    """Record answer edits to train the copilot.

    Non-blocking: failures are logged but don't affect the request.
    """
    from app.core.domain.job import Job
    from app.config import Settings
    from app.core.services.answer_learning import AnswerLearningService
    from app.infra.llm.together_client import TogetherLLMClient
    from app.infra.vector.chroma_store import ChromaVectorStore

    try:
        # Initialize services
        llm_client = TogetherLLMClient(api_key=settings.together_api_key)
        vector_store = ChromaVectorStore(
            host=settings.chroma_host,
            port=settings.chroma_port,
            llm_client=llm_client,
        )
        learning_service = AnswerLearningService(
            vector_store=vector_store,
            llm_client=llm_client,
        )

        # Record each edited answer
        for question, edited_answer in edited_answers.items():
            original_answer = original_answers.get(question, "")

            # Skip if no original answer (new question) or no change
            if not original_answer:
                continue

            await learning_service.record_edit(
                user_id=user_id,
                question=question,
                original_answer=original_answer,
                edited_answer=edited_answer,
                job=job,
            )

        logger.debug(
            "answer_edits_recorded_for_learning",
            user_id=user_id,
            edits_count=len(edited_answers),
        )

    except Exception as e:
        # Non-blocking: log error but don't fail the request
        logger.warning(
            "answer_learning_record_failed",
            user_id=user_id,
            error=str(e),
        )


def _notes_to_response(notes: list) -> list[NoteResponse]:
    """Convert domain notes to response format."""
    return [
        NoteResponse(id=n.id, content=n.content, created_at=n.created_at)
        for n in notes
    ]


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
                stage=app.stage.value,
                match_score=app.match_score,
                notes=_notes_to_response(app.notes),
                created_at=app.created_at,
                submitted_at=app.submitted_at,
                stage_updated_at=app.stage_updated_at,
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


@router.get("/grouped", response_model=GroupedApplicationsResponse)
async def get_grouped_applications(
    current_user: CurrentUser,
    db: DBSession,
    search: str | None = Query(None),
) -> GroupedApplicationsResponse:
    """Get applications grouped by stage for Kanban view."""
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository

    app_repo = SQLApplicationRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    grouped = await app_repo.get_grouped_by_stage(current_user.id, search=search)

    # Build response with job details
    stages_response: dict[str, StageItemsResponse] = {}
    total = 0

    for stage, apps in grouped.items():
        items = []
        for app in apps:
            job = await job_repo.get_by_id(app.job_id)
            if job:
                # Apply search filter if provided
                if search:
                    search_lower = search.lower()
                    if (
                        search_lower not in job.title.lower()
                        and search_lower not in job.company.lower()
                    ):
                        continue

                items.append(ApplicationSummaryResponse(
                    id=app.id,
                    job_id=app.job_id,
                    job_title=job.title,
                    company=job.company,
                    status=app.status.value,
                    stage=app.stage.value,
                    match_score=app.match_score,
                    notes=_notes_to_response(app.notes),
                    created_at=app.created_at,
                    submitted_at=app.submitted_at,
                    stage_updated_at=app.stage_updated_at,
                ))

        stages_response[stage.value] = StageItemsResponse(items=items, count=len(items))
        total += len(items)

    return GroupedApplicationsResponse(stages=stages_response, total=total)


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
        stage=application.stage.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        notes=_notes_to_response(application.notes),
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=[],
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        stage_updated_at=application.stage_updated_at,
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
        stage=application.stage.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        notes=_notes_to_response(application.notes),
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=audit_trail,
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        stage_updated_at=application.stage_updated_at,
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
        stage=application.stage.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        notes=_notes_to_response(application.notes),
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=[],
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        stage_updated_at=application.stage_updated_at,
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
    settings: AppSettings,
) -> ApplicationDetailResponse:
    """Edit application content before approval.

    Edits to screening question answers are recorded for copilot learning.
    """
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

    # Get job for learning context
    job = await job_repo.get_by_id(application.job_id)

    # Store original answers for learning before updating
    original_answers = dict(application.generated_answers) if application.generated_answers else {}

    # Update content
    if request.cover_letter is not None:
        application.cover_letter = request.cover_letter
    if request.answers is not None:
        application.generated_answers.update(request.answers)

    await app_repo.update(application)

    # Record answer edits for copilot learning (async, non-blocking)
    if request.answers and job:
        await _record_answer_edits_for_learning(
            user_id=current_user.id,
            original_answers=original_answers,
            edited_answers=request.answers,
            job=job,
            settings=settings,
        )

    logger.info(
        "application_edited",
        user_id=current_user.id,
        application_id=application_id,
        answers_edited=bool(request.answers),
    )

    return ApplicationDetailResponse(
        id=application.id,
        user_id=application.user_id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status=application.status.value,
        stage=application.stage.value,
        match_score=application.match_score,
        match_explanation=None,
        cover_letter=application.cover_letter,
        generated_answers=application.generated_answers,
        notes=_notes_to_response(application.notes),
        qc_approved=application.qc_approved,
        qc_feedback=application.qc_feedback,
        audit_trail=[],
        created_at=application.created_at,
        submitted_at=application.submitted_at,
        stage_updated_at=application.stage_updated_at,
        error_message=application.error_message,
        job_title=job.title if job else "",
        company=job.company if job else "",
        job_url=job.url if job else "",
    )


@router.patch("/{application_id}/stage", response_model=ApplicationSummaryResponse)
async def update_application_stage(
    application_id: str,
    request: UpdateStageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ApplicationSummaryResponse:
    """Update application stage (for Kanban drag-drop)."""
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

    try:
        new_stage = ApplicationStage(request.stage)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stage: {request.stage}",
        )

    updated = await app_repo.update_stage(application_id, stage=new_stage)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update stage",
        )

    job = await job_repo.get_by_id(updated.job_id)

    logger.info(
        "application_stage_updated",
        user_id=current_user.id,
        application_id=application_id,
        new_stage=request.stage,
    )

    return ApplicationSummaryResponse(
        id=updated.id,
        job_id=updated.job_id,
        job_title=job.title if job else "",
        company=job.company if job else "",
        status=updated.status.value,
        stage=updated.stage.value,
        match_score=updated.match_score,
        notes=_notes_to_response(updated.notes),
        created_at=updated.created_at,
        submitted_at=updated.submitted_at,
        stage_updated_at=updated.stage_updated_at,
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


@router.post("/{application_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    application_id: str,
    request: AddNoteRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> NoteResponse:
    """Add a note to an application."""
    from app.infra.db.repositories.application import SQLApplicationRepository

    app_repo = SQLApplicationRepository(session=db)

    application = await app_repo.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    note = await app_repo.add_note(
        application_id,
        note_id=str(uuid.uuid4()),
        content=request.content,
    )

    logger.info(
        "application_note_added",
        user_id=current_user.id,
        application_id=application_id,
        note_id=note.id,
    )

    return NoteResponse(id=note.id, content=note.content, created_at=note.created_at)


@router.delete("/{application_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    application_id: str,
    note_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Delete a note from an application."""
    from app.infra.db.repositories.application import SQLApplicationRepository

    app_repo = SQLApplicationRepository(session=db)

    application = await app_repo.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Check note belongs to this application
    note_found = any(n.id == note_id for n in application.notes)
    if not note_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    deleted = await app_repo.delete_note(note_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note",
        )

    logger.info(
        "application_note_deleted",
        user_id=current_user.id,
        application_id=application_id,
        note_id=note_id,
    )
