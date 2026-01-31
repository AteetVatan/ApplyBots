"""Jobs endpoints.

Standards: python_clean.mdc
- Thin controller layer
- Query parameter validation
"""

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AppSettings, CurrentUser, DBSession
from app.schemas.job import (
    JobDetailResponse,
    JobListResponse,
    JobRequirementsResponse,
    JobSummaryResponse,
    MatchAnalysis,
)

router = APIRouter()
logger = structlog.get_logger()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    query: str | None = None,
    location: str | None = None,
    remote_only: bool = False,
    salary_min: int | None = Query(None, ge=0),
    min_match_score: int | None = Query(None, ge=0, le=100),
) -> JobListResponse:
    """List jobs matching user preferences."""
    from app.core.services.matcher import MatchService
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.resume import SQLResumeRepository

    job_repo = SQLJobRepository(session=db)
    profile_repo = SQLProfileRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)

    # Get user's profile and primary resume
    profile = await profile_repo.get_by_user_id(current_user.id)
    resume = await resume_repo.get_primary(user_id=current_user.id)

    # Get jobs with filters
    offset = (page - 1) * limit
    jobs = await job_repo.find_matching(
        user_id=current_user.id,
        limit=limit + 1,  # Fetch one extra to check has_more
        offset=offset,
    )

    has_more = len(jobs) > limit
    jobs = jobs[:limit]

    # Calculate match scores if resume available
    match_service = MatchService()
    items = []

    for job in jobs:
        match_score = None
        if resume and resume.parsed_data:
            score, _ = match_service.calculate_score(
                resume=resume.parsed_data,
                job=job,
                preferences=profile.preferences if profile else None,
            )
            match_score = score

            # Filter by min match score
            if min_match_score and match_score < min_match_score:
                continue

        items.append(JobSummaryResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            remote=job.remote,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            match_score=match_score,
            posted_at=job.posted_at,
        ))

    total = await job_repo.count()

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> JobDetailResponse:
    """Get job details with match score."""
    from app.core.services.matcher import MatchService
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.resume import SQLResumeRepository

    job_repo = SQLJobRepository(session=db)
    profile_repo = SQLProfileRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)

    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Calculate match score
    profile = await profile_repo.get_by_user_id(current_user.id)
    resume = await resume_repo.get_primary(user_id=current_user.id)

    match_score = None
    if resume and resume.parsed_data:
        match_service = MatchService()
        score, _ = match_service.calculate_score(
            resume=resume.parsed_data,
            job=job,
            preferences=profile.preferences if profile else None,
        )
        match_score = score

    return JobDetailResponse(
        id=job.id,
        external_id=job.external_id,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        url=job.url,
        source=job.source.value,
        remote=job.remote,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        requirements=JobRequirementsResponse(
            required_skills=job.requirements.required_skills,
            preferred_skills=job.requirements.preferred_skills,
            experience_years_min=job.requirements.experience_years_min,
            experience_years_max=job.requirements.experience_years_max,
            education_level=job.requirements.education_level,
        ),
        match_score=match_score,
        posted_at=job.posted_at,
        ingested_at=job.ingested_at,
    )


@router.get("/{job_id}/match", response_model=MatchAnalysis)
async def get_match_analysis(
    job_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> MatchAnalysis:
    """Get detailed match analysis for a job."""
    from app.core.services.matcher import MatchService
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.profile import SQLProfileRepository
    from app.infra.db.repositories.resume import SQLResumeRepository

    job_repo = SQLJobRepository(session=db)
    profile_repo = SQLProfileRepository(session=db)
    resume_repo = SQLResumeRepository(session=db)

    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    resume = await resume_repo.get_primary(user_id=current_user.id)
    if not resume or not resume.parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume uploaded. Please upload a resume first.",
        )

    profile = await profile_repo.get_by_user_id(current_user.id)

    match_service = MatchService()
    score, explanation = match_service.calculate_score(
        resume=resume.parsed_data,
        job=job,
        preferences=profile.preferences if profile else None,
    )

    return MatchAnalysis(
        overall_score=score,
        skills_score=explanation.skills_score,
        skills_matched=explanation.skills_matched,
        skills_missing=explanation.skills_missing,
        experience_score=explanation.experience_score,
        experience_gap=explanation.experience_gap,
        location_score=explanation.location_score,
        location_match=explanation.location_match,
        salary_score=explanation.salary_score,
        salary_in_range=explanation.salary_in_range,
        culture_score=explanation.culture_score,
        recommendation=explanation.overall_recommendation,
    )


@router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_jobs(
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, str]:
    """Trigger job ingestion from external sources."""
    try:
        from app.workers.job_ingestion import ingest_jobs_task

        # Queue the job ingestion task
        ingest_jobs_task.delay(user_id=current_user.id)

        logger.info("job_refresh_triggered", user_id=current_user.id)

        return {"status": "Job refresh queued"}
    except ImportError as e:
        logger.warning("celery_not_available", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background job service is not available. Please try again later.",
        )
