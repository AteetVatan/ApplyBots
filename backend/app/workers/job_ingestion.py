"""Job ingestion worker tasks.

Standards: python_clean.mdc
- Async tasks with proper error handling
- Structured logging
"""

import uuid
from datetime import datetime

import httpx
import structlog

from app.core.domain.job import Job, JobRequirements, JobSource
from app.workers.celery_app import celery_app

logger = structlog.get_logger()

# Remotive API endpoint
REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


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
    """Scheduled job ingestion."""
    return ingest_jobs_task(user_id=None)


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
    """Async job ingestion from Remotive API."""
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.session import async_session_factory

    jobs_added = 0
    jobs_updated = 0
    errors = 0

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
                    else:
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
            errors=errors,
            user_id=user_id,
        )

        return {
            "status": "success",
            "jobs_added": jobs_added,
            "jobs_updated": jobs_updated,
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
    except Exception:
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
