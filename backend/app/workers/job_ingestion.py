"""Job ingestion worker tasks.

Standards: python_clean.mdc
- Async tasks with proper error handling
- Structured logging
- Embedding generation for semantic search
- Campaign-aware job processing with feedback penalties
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.campaign import CampaignJob, CampaignJobStatus, CampaignStatus
from app.core.domain.job import Job, JobRequirements, JobSource
from app.workers.celery_app import celery_app

logger = structlog.get_logger()

# Remotive API endpoint
REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"

# Collection name for job embeddings
JOBS_COLLECTION = "jobs"


@celery_app.task(name="app.workers.job_ingestion.ingest_jobs_task")
def ingest_jobs_task(user_id: str | None = None) -> dict:
    """Ingest jobs from external sources."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_ingest_jobs_async(user_id))
        return result
    finally:
        loop.close()


@celery_app.task(name="app.workers.job_ingestion.ingest_jobs_scheduled")
def ingest_jobs_scheduled() -> dict:
    """Scheduled job ingestion + campaign processing."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # First ingest new jobs from all sources
        ingest_result = loop.run_until_complete(_ingest_jobs_async(user_id=None))

        # Then process campaigns
        campaign_result = loop.run_until_complete(_process_all_campaigns_async())

        return {
            "status": "success",
            "ingestion": ingest_result,
            "campaigns": campaign_result,
        }
    finally:
        loop.close()


@celery_app.task(name="app.workers.job_ingestion.process_campaign_jobs")
def process_campaign_jobs(campaign_id: str) -> dict:
    """Process new jobs for a specific campaign."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_process_campaign_async(campaign_id))
        return result
    finally:
        loop.close()


@celery_app.task(name="app.workers.job_ingestion.reset_daily_usage")
def reset_daily_usage() -> dict:
    """Reset daily usage counters for all subscriptions."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_reset_usage_async())
        return result
    finally:
        loop.close()


async def _ingest_jobs_async(user_id: str | None) -> dict:
    """Async job ingestion from Remotive API with embedding generation."""
    from app.config import get_settings
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.session import async_session_factory
    from app.infra.llm.together_client import TogetherLLMClient
    from app.infra.vector.chroma_store import ChromaVectorStore

    settings = get_settings()
    jobs_added = 0
    jobs_updated = 0
    embeddings_generated = 0
    errors = 0

    # Initialize LLM client for embeddings (if API key available)
    llm_client = None
    vector_store = None
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

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(REMOTIVE_API_URL)
            response.raise_for_status()
            data = response.json()

        jobs_data = data.get("jobs", [])

        async with async_session_factory() as session:
            job_repo = SQLJobRepository(session=session)

            for job_data in jobs_data[:100]:  # Limit to 100 per ingestion
                try:
                    job = _parse_remotive_job(job_data)

                    existing = await job_repo.get_by_external_id(job.external_id)
                    if existing:
                        jobs_updated += 1
                        # Skip embedding generation for existing jobs
                        await job_repo.upsert(job)
                        continue

                    # Generate embedding for new jobs
                    if llm_client and job.description:
                        try:
                            # Create text for embedding: title + company + description
                            embed_text = f"{job.title} at {job.company}\n\n{job.description[:6000]}"
                            embedding = await llm_client.embed(text=embed_text)
                            job.embedding = embedding

                            # Store in vector database
                            if vector_store:
                                await vector_store.add_embedding(
                                    collection=JOBS_COLLECTION,
                                    doc_id=job.id,
                                    embedding=embedding,
                                    metadata={
                                        "title": job.title,
                                        "company": job.company,
                                        "source": job.source.value,
                                        "remote": job.remote,
                                    },
                                )

                            embeddings_generated += 1
                            logger.debug(
                                "job_embedding_generated",
                                job_id=job.id,
                                title=job.title,
                            )

                        except Exception as e:
                            logger.warning(
                                "job_embedding_failed",
                                job_id=job.id,
                                error=str(e),
                            )
                            # Continue without embedding

                    jobs_added += 1
                    await job_repo.upsert(job)

                except Exception as e:
                    logger.warning(
                        "job_parse_error",
                        error=str(e),
                        job_id=job_data.get("id"),
                    )
                    errors += 1

            await session.commit()

        logger.info(
            "job_ingestion_complete",
            jobs_added=jobs_added,
            jobs_updated=jobs_updated,
            embeddings_generated=embeddings_generated,
            errors=errors,
            user_id=user_id,
        )

        return {
            "status": "success",
            "jobs_added": jobs_added,
            "jobs_updated": jobs_updated,
            "embeddings_generated": embeddings_generated,
            "errors": errors,
        }

    except Exception as e:
        logger.error("job_ingestion_failed", error=str(e))
        return {"status": "error", "error": str(e)}


def _parse_remotive_job(data: dict) -> Job:
    """Parse Remotive API job data into Job domain model."""
    # Extract skills from tags
    tags = data.get("tags", [])

    # Parse salary if available
    salary_text = data.get("salary", "")
    salary_min, salary_max = _parse_salary(salary_text)

    return Job(
        id=str(uuid.uuid4()),
        external_id=f"remotive_{data.get('id', '')}",
        title=data.get("title", ""),
        company=data.get("company_name", ""),
        location=data.get("candidate_required_location", "Worldwide"),
        description=data.get("description", ""),
        url=data.get("url", ""),
        source=JobSource.REMOTIVE,
        salary_min=salary_min,
        salary_max=salary_max,
        remote=True,  # Remotive is all remote
        requirements=JobRequirements(
            required_skills=tags[:5],
            preferred_skills=tags[5:10] if len(tags) > 5 else [],
        ),
        posted_at=_parse_date(data.get("publication_date")),
        ingested_at=datetime.utcnow(),
    )


def _parse_salary(salary_text: str) -> tuple[int | None, int | None]:
    """Parse salary string into min/max values."""
    if not salary_text:
        return None, None

    import re

    # Look for numbers in the salary text
    numbers = re.findall(r"[\d,]+", salary_text.replace(",", ""))

    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    elif len(numbers) == 1:
        return int(numbers[0]), None

    return None, None


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse date string to datetime."""
    if not date_str:
        return None

    try:
        # Remotive uses ISO format
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception as e:
        logger.warning("date_parse_failed", date_str=date_str, error=str(e))
        return None


async def _reset_usage_async() -> dict:
    """Reset daily usage counters."""
    from app.infra.db.repositories.subscription import SQLSubscriptionRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        sub_repo = SQLSubscriptionRepository(session=session)
        count = await sub_repo.reset_daily_usage()
        await session.commit()

    logger.info("daily_usage_reset", count=count)

    return {"status": "success", "reset_count": count}


async def _process_all_campaigns_async() -> dict:
    """Process jobs for all active campaigns."""
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.session import async_session_factory

    campaigns_processed = 0
    jobs_matched = 0
    applications_queued = 0
    errors = 0

    async with async_session_factory() as session:
        campaign_repo = SQLCampaignRepository(session=session)

        # Get all active campaigns
        campaigns = await campaign_repo.get_active_campaigns()

        for campaign in campaigns:
            try:
                result = await _process_single_campaign(
                    campaign_id=campaign.id,
                    session=session,
                )
                campaigns_processed += 1
                jobs_matched += result.get("jobs_matched", 0)
                applications_queued += result.get("applications_queued", 0)
            except Exception as e:
                logger.warning(
                    "campaign_processing_error",
                    campaign_id=campaign.id,
                    error=str(e),
                )
                errors += 1

        await session.commit()

    logger.info(
        "all_campaigns_processed",
        campaigns_processed=campaigns_processed,
        jobs_matched=jobs_matched,
        applications_queued=applications_queued,
        errors=errors,
    )

    return {
        "campaigns_processed": campaigns_processed,
        "jobs_matched": jobs_matched,
        "applications_queued": applications_queued,
        "errors": errors,
    }


async def _process_campaign_async(campaign_id: str) -> dict:
    """Process jobs for a specific campaign."""
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        result = await _process_single_campaign(
            campaign_id=campaign_id,
            session=session,
        )
        await session.commit()

    return result


async def _process_single_campaign(
    campaign_id: str,
    session,
) -> dict:
    """Process a single campaign - find matching jobs and optionally auto-apply.

    Args:
        campaign_id: Campaign to process
        session: Database session

    Returns:
        Processing results
    """
    from app.config import get_settings
    from app.core.services.job_feedback import JobFeedbackService
    from app.core.services.matcher import MatchService
    from app.infra.db.repositories.campaign import SQLCampaignRepository
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.llm.together_client import TogetherLLMClient
    from app.infra.vector.chroma_store import ChromaVectorStore

    settings = get_settings()
    campaign_repo = SQLCampaignRepository(session=session)
    job_repo = SQLJobRepository(session=session)
    resume_repo = SQLResumeRepository(session=session)
    match_service = MatchService()

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    if campaign.status != CampaignStatus.ACTIVE:
        return {"error": "Campaign not active", "status": campaign.status.value}

    # Get resume for this campaign
    resume = await resume_repo.get_by_id(campaign.resume_id)
    if not resume or not resume.parsed_data:
        return {"error": "Resume not found or not parsed"}

    # Initialize feedback service for pattern learning
    feedback_service = None
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

    # Check daily limit
    applied_today = await campaign_repo.count_applied_today(campaign_id)
    remaining_today = campaign.daily_limit - applied_today

    if remaining_today <= 0:
        logger.info(
            "campaign_daily_limit_reached",
            campaign_id=campaign_id,
            daily_limit=campaign.daily_limit,
        )
        return {"jobs_matched": 0, "applications_queued": 0, "reason": "daily_limit_reached"}

    # Find matching jobs using campaign criteria
    jobs = await job_repo.find_matching(
        user_id=campaign.user_id,
        limit=remaining_today * 2,  # Get extra for filtering
        negative_keywords=campaign.negative_keywords,
    )

    jobs_matched = 0
    applications_queued = 0

    for job in jobs:
        # Check if job already in campaign
        exists = await campaign_repo.job_exists_in_campaign(campaign_id, job.id)
        if exists:
            continue

        # Check role match
        if campaign.target_roles:
            role_match = any(
                role.lower() in job.title.lower()
                for role in campaign.target_roles
            )
            if not role_match:
                continue

        # Check location match
        if campaign.target_locations and not campaign.remote_only:
            location_match = any(
                loc.lower() in (job.location or "").lower()
                for loc in campaign.target_locations
            )
            if not location_match and not job.remote:
                continue

        # Check remote preference
        if campaign.remote_only and not job.remote:
            continue

        # Check salary
        if campaign.salary_min and job.salary_max:
            if job.salary_max < campaign.salary_min:
                continue

        # Calculate match score
        base_score, _ = match_service.calculate_score(
            resume=resume.parsed_data,
            job=job,
            preferences=None,
        )

        # Apply feedback penalty if available
        adjusted_score = base_score
        if feedback_service:
            adjusted_score = await feedback_service.calculate_adjusted_score(
                user_id=campaign.user_id,
                job=job,
                base_score=base_score,
            )

        # Check minimum score
        if adjusted_score < campaign.min_match_score:
            continue

        # Add job to campaign
        campaign_job = CampaignJob(
            campaign_id=campaign_id,
            job_id=job.id,
            match_score=base_score,
            adjusted_score=adjusted_score,
            status=CampaignJobStatus.PENDING,
        )
        await campaign_repo.add_job(campaign_job)
        jobs_matched += 1

        # Auto-apply if enabled
        if campaign.auto_apply and applications_queued < remaining_today:
            # Update status to applied
            await campaign_repo.update_job_status(
                campaign_id,
                job.id,
                status=CampaignJobStatus.APPLIED,
            )

            # Queue application submission
            from app.workers.application_submitter import bulk_apply_task

            bulk_apply_task.delay(
                user_id=campaign.user_id,
                job_ids=[job.id],
                resume_id=campaign.resume_id,
                auto_submit=True,
            )

            applications_queued += 1

        # Stop if we've reached daily limit
        if applications_queued >= remaining_today:
            break

    # Update campaign stats
    await campaign_repo.increment_stats(
        campaign_id,
        jobs_found=jobs_matched,
        jobs_applied=applications_queued,
    )

    logger.info(
        "campaign_processed",
        campaign_id=campaign_id,
        campaign_name=campaign.name,
        jobs_matched=jobs_matched,
        applications_queued=applications_queued,
        auto_apply=campaign.auto_apply,
    )

    return {
        "jobs_matched": jobs_matched,
        "applications_queued": applications_queued,
    }
