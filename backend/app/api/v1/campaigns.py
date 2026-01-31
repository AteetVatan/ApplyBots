"""Campaign (Copilot) API endpoints.

Standards: python_clean.mdc
- Thin controller layer
- Query parameter validation
"""

import uuid

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.core.domain.campaign import Campaign, CampaignJobStatus, CampaignStatus
from app.schemas.campaign import (
    CampaignCreate,
    CampaignJobListResponse,
    CampaignJobResponse,
    CampaignListResponse,
    CampaignResponse,
    CampaignStats,
    CampaignUpdate,
    RejectJobRequest,
)

router = APIRouter()
logger = structlog.get_logger()


def _campaign_to_response(campaign: Campaign) -> CampaignResponse:
    """Convert domain campaign to response model."""
    return CampaignResponse(
        id=campaign.id,
        user_id=campaign.user_id,
        name=campaign.name,
        resume_id=campaign.resume_id,
        target_roles=campaign.target_roles,
        target_locations=campaign.target_locations,
        target_countries=campaign.target_countries,
        target_companies=campaign.target_companies,
        remote_only=campaign.remote_only,
        salary_min=campaign.salary_min,
        salary_max=campaign.salary_max,
        negative_keywords=campaign.negative_keywords,
        auto_apply=campaign.auto_apply,
        daily_limit=campaign.daily_limit,
        min_match_score=campaign.min_match_score,
        send_per_app_email=campaign.send_per_app_email,
        cover_letter_template=campaign.cover_letter_template,
        status=campaign.status.value,
        stats=CampaignStats(
            jobs_found=campaign.jobs_found,
            jobs_applied=campaign.jobs_applied,
            interviews=campaign.interviews,
            offers=campaign.offers,
        ),
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        completed_at=campaign.completed_at,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    request: CampaignCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignResponse:
    """Create a new campaign (copilot)."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.repositories.resume import SQLResumeRepository

    campaign_repo = SQLCampaignRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)

    # Verify resume belongs to user
    resume = await resume_repo.get_by_id(request.resume_id)
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    campaign = Campaign(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=request.name,
        resume_id=request.resume_id,
        target_roles=request.target_roles,
        target_locations=request.target_locations,
        target_countries=request.target_countries,
        target_companies=request.target_companies,
        remote_only=request.remote_only,
        salary_min=request.salary_min,
        salary_max=request.salary_max,
        negative_keywords=request.negative_keywords,
        auto_apply=request.auto_apply,
        daily_limit=request.daily_limit,
        min_match_score=request.min_match_score,
        send_per_app_email=request.send_per_app_email,
        cover_letter_template=request.cover_letter_template,
        status=CampaignStatus.ACTIVE,
    )

    created = await campaign_repo.create(campaign)
    await db.commit()

    logger.info(
        "campaign_created",
        user_id=current_user.id,
        campaign_id=created.id,
        name=created.name,
    )

    return _campaign_to_response(created)


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> CampaignListResponse:
    """List user's campaigns."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository

    campaign_repo = SQLCampaignRepository(session=db)

    # Parse status filter
    campaign_status = None
    if status_filter:
        try:
            campaign_status = CampaignStatus(status_filter)
        except ValueError:
            pass

    offset = (page - 1) * limit
    campaigns = await campaign_repo.get_by_user_id(
        current_user.id,
        status=campaign_status,
        limit=limit + 1,
        offset=offset,
    )

    has_more = len(campaigns) > limit
    campaigns = campaigns[:limit]

    return CampaignListResponse(
        campaigns=[_campaign_to_response(c) for c in campaigns],
        total=len(campaigns),
        has_more=has_more,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignResponse:
    """Get campaign details."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository

    campaign_repo = SQLCampaignRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    return _campaign_to_response(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    request: CampaignUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignResponse:
    """Update campaign settings."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.repositories.resume import SQLResumeRepository

    campaign_repo = SQLCampaignRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # If changing resume, verify it belongs to user
    if request.resume_id:
        resume = await resume_repo.get_by_id(request.resume_id)
        if not resume or resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )
        campaign.resume_id = request.resume_id

    # Update fields
    if request.name is not None:
        campaign.name = request.name
    if request.target_roles is not None:
        campaign.target_roles = request.target_roles
    if request.target_locations is not None:
        campaign.target_locations = request.target_locations
    if request.target_countries is not None:
        campaign.target_countries = request.target_countries
    if request.target_companies is not None:
        campaign.target_companies = request.target_companies
    if request.remote_only is not None:
        campaign.remote_only = request.remote_only
    if request.salary_min is not None:
        campaign.salary_min = request.salary_min
    if request.salary_max is not None:
        campaign.salary_max = request.salary_max
    if request.negative_keywords is not None:
        campaign.negative_keywords = request.negative_keywords
    if request.auto_apply is not None:
        campaign.auto_apply = request.auto_apply
    if request.daily_limit is not None:
        campaign.daily_limit = request.daily_limit
    if request.min_match_score is not None:
        campaign.min_match_score = request.min_match_score
    if request.send_per_app_email is not None:
        campaign.send_per_app_email = request.send_per_app_email
    if request.cover_letter_template is not None:
        campaign.cover_letter_template = request.cover_letter_template

    updated = await campaign_repo.update(campaign)
    await db.commit()

    logger.info(
        "campaign_updated",
        user_id=current_user.id,
        campaign_id=campaign_id,
    )

    return _campaign_to_response(updated)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Delete a campaign."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository

    campaign_repo = SQLCampaignRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    await campaign_repo.delete(campaign_id)
    await db.commit()

    logger.info(
        "campaign_deleted",
        user_id=current_user.id,
        campaign_id=campaign_id,
    )


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignResponse:
    """Pause a campaign's auto-apply."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository

    campaign_repo = SQLCampaignRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is not active",
        )

    updated = await campaign_repo.update_status(
        campaign_id,
        status=CampaignStatus.PAUSED,
    )
    await db.commit()

    logger.info(
        "campaign_paused",
        user_id=current_user.id,
        campaign_id=campaign_id,
    )

    return _campaign_to_response(updated)


@router.post("/{campaign_id}/resume", response_model=CampaignResponse)
async def resume_campaign(
    campaign_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignResponse:
    """Resume a paused campaign."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository

    campaign_repo = SQLCampaignRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    if campaign.status != CampaignStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is not paused",
        )

    updated = await campaign_repo.update_status(
        campaign_id,
        status=CampaignStatus.ACTIVE,
    )
    await db.commit()

    logger.info(
        "campaign_resumed",
        user_id=current_user.id,
        campaign_id=campaign_id,
    )

    return _campaign_to_response(updated)


@router.get("/{campaign_id}/jobs", response_model=CampaignJobListResponse)
async def get_campaign_jobs(
    campaign_id: str,
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> CampaignJobListResponse:
    """Get jobs found for a campaign."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.repositories.job import SQLJobRepository

    campaign_repo = SQLCampaignRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # Parse status filter
    job_status = None
    if status_filter:
        try:
            job_status = CampaignJobStatus(status_filter)
        except ValueError:
            pass

    offset = (page - 1) * limit
    campaign_jobs = await campaign_repo.get_campaign_jobs(
        campaign_id,
        status=job_status,
        limit=limit + 1,
        offset=offset,
    )

    has_more = len(campaign_jobs) > limit
    campaign_jobs = campaign_jobs[:limit]

    # Fetch job details
    job_responses = []
    for cj in campaign_jobs:
        job = await job_repo.get_by_id(cj.job_id)
        job_responses.append(
            CampaignJobResponse(
                campaign_id=cj.campaign_id,
                job_id=cj.job_id,
                match_score=cj.match_score,
                adjusted_score=cj.adjusted_score,
                status=cj.status.value,
                rejection_reason=cj.rejection_reason,
                created_at=cj.created_at,
                applied_at=cj.applied_at,
                rejected_at=cj.rejected_at,
                job_title=job.title if job else None,
                company=job.company if job else None,
                location=job.location if job else None,
                job_url=job.url if job else None,
            )
        )

    return CampaignJobListResponse(
        jobs=job_responses,
        total=len(job_responses),
        has_more=has_more,
    )


@router.post(
    "/{campaign_id}/jobs/{job_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reject_campaign_job(
    campaign_id: str,
    job_id: str,
    request: RejectJobRequest,
    current_user: CurrentUser,
    db: DBSession,
    settings: AppSettings,
) -> None:
    """Reject a job from a campaign (triggers learning)."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.repositories.job import SQLJobRepository

    campaign_repo = SQLCampaignRepository(session=db)
    job_repo = SQLJobRepository(session=db)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    campaign_job = await campaign_repo.get_campaign_job(campaign_id, job_id)
    if not campaign_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in campaign",
        )

    # Update status to rejected
    await campaign_repo.update_job_status(
        campaign_id,
        job_id,
        status=CampaignJobStatus.REJECTED,
        rejection_reason=request.reason,
    )

    # Trigger feedback learning (done in background)
    job = await job_repo.get_by_id(job_id)
    if job:
        # Import here to avoid circular imports
        from app.core.services.job_feedback import JobFeedbackService
        from app.infra.llm.together_client import TogetherLLMClient
        from app.infra.vector.chroma_store import ChromaVectorStore

        api_key = settings.together_api_key.get_secret_value()
        if api_key:
            llm_client = TogetherLLMClient(
                api_key=api_key,
                base_url=settings.together_api_base,
            )
            vector_store = ChromaVectorStore(
                host=settings.chroma_host,
                port=settings.chroma_port,
                llm_client=llm_client,
            )
            feedback_service = JobFeedbackService(
                vector_store=vector_store,
                llm_client=llm_client,
            )

            await feedback_service.record_rejection(
                user_id=current_user.id,
                campaign_id=campaign_id,
                job=job,
                reason=request.reason,
            )

    await db.commit()

    logger.info(
        "campaign_job_rejected",
        user_id=current_user.id,
        campaign_id=campaign_id,
        job_id=job_id,
        reason=request.reason,
    )
