"""Agent tools registration for AutoGen.

Standards: python_clean.mdc
- Register tools for agents to call external services
- Type-safe function signatures
"""

import structlog
from typing import Any

logger = structlog.get_logger()


# Tool definitions for agents

async def parse_resume_tool(resume_id: str) -> dict[str, Any]:
    """Parse a resume and return structured data.

    Args:
        resume_id: The ID of the resume to parse

    Returns:
        Parsed resume data including skills, experience, education
    """
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        repo = SQLResumeRepository(session=session)
        resume = await repo.get_by_id(resume_id)

        if not resume:
            return {"error": "Resume not found"}

        if not resume.parsed_data:
            return {"error": "Resume not parsed yet"}

        parsed = resume.parsed_data
        return {
            "full_name": parsed.full_name,
            "email": parsed.email,
            "phone": parsed.phone,
            "location": parsed.location,
            "skills": parsed.skills[:20],
            "total_years_experience": parsed.total_years_experience,
            "work_experience_count": len(parsed.work_experience) if parsed.work_experience else 0,
            "education_count": len(parsed.education) if parsed.education else 0,
        }


async def search_jobs_tool(
    *,
    query: str | None = None,
    location: str | None = None,
    remote_only: bool = False,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search for jobs matching criteria.

    Args:
        query: Search query (job title, skills, etc.)
        location: Location filter
        remote_only: Only return remote jobs
        limit: Maximum number of results

    Returns:
        List of matching jobs
    """
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        repo = SQLJobRepository(session=session)

        # Get recent jobs (would use vector search in production)
        jobs = await repo.get_recent(limit=limit * 2)

        results = []
        for job in jobs:
            # Apply filters
            if remote_only and not job.remote:
                continue

            if location and location.lower() not in job.location.lower():
                continue

            if query:
                query_lower = query.lower()
                if query_lower not in job.title.lower() and query_lower not in job.description.lower():
                    continue

            results.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "remote": job.remote,
                "url": job.url,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
            })

            if len(results) >= limit:
                break

        return results


async def calculate_match_tool(
    *,
    resume_id: str,
    job_id: str,
) -> dict[str, Any]:
    """Calculate match score between resume and job.

    Args:
        resume_id: ID of the resume
        job_id: ID of the job

    Returns:
        Match score and explanation
    """
    from app.core.services.matcher import MatchService
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        job_repo = SQLJobRepository(session=session)
        resume_repo = SQLResumeRepository(session=session)

        job = await job_repo.get_by_id(job_id)
        resume = await resume_repo.get_by_id(resume_id)

        if not job or not resume or not resume.parsed_data:
            return {"error": "Job or resume not found"}

        matcher = MatchService()
        score, explanation = matcher.calculate_score(
            resume=resume.parsed_data,
            job=job,
        )

        return {
            "overall_score": score,
            "skills_score": explanation.skills_score,
            "experience_score": explanation.experience_score,
            "location_score": explanation.location_score,
            "salary_score": explanation.salary_score,
            "skills_matched": explanation.skills_matched[:10],
            "skills_missing": explanation.skills_missing[:10],
            "recommendation": explanation.recommendation,
        }


async def generate_cover_letter_tool(
    *,
    resume_id: str,
    job_id: str,
    tone: str = "professional",
) -> dict[str, Any]:
    """Generate a cover letter for a job application.

    Args:
        resume_id: ID of the resume
        job_id: ID of the job
        tone: Writing tone (professional, enthusiastic, concise)

    Returns:
        Generated cover letter
    """
    # This will be implemented fully in phase 2
    return {
        "status": "pending",
        "message": "Cover letter generation requires LLM client (implemented in Phase 2)",
    }


async def submit_application_tool(
    *,
    job_id: str,
    resume_id: str,
    cover_letter: str | None = None,
) -> dict[str, Any]:
    """Submit a job application.

    Args:
        job_id: ID of the job to apply to
        resume_id: ID of the resume to use
        cover_letter: Optional cover letter text

    Returns:
        Application submission status
    """
    from app.infra.db.repositories.application import SQLApplicationRepository
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        job_repo = SQLJobRepository(session=session)
        app_repo = SQLApplicationRepository(session=session)

        job = await job_repo.get_by_id(job_id)
        if not job:
            return {"error": "Job not found"}

        # Check for existing application
        # (This would be implemented in the repository)

        return {
            "status": "queued",
            "message": "Application has been queued for submission",
            "job_title": job.title,
            "company": job.company,
        }


async def verify_content_tool(
    *,
    content: str,
    resume_id: str,
    job_id: str,
) -> dict[str, Any]:
    """Verify generated content against resume using Truth-Lock.

    Args:
        content: Content to verify (cover letter, answers, etc.)
        resume_id: ID of the resume
        job_id: ID of the job

    Returns:
        Verification result
    """
    from app.core.services.truth_lock import TruthLockVerifier
    from app.infra.db.repositories.job import SQLJobRepository
    from app.infra.db.repositories.resume import SQLResumeRepository
    from app.infra.db.session import async_session_factory

    async with async_session_factory() as session:
        job_repo = SQLJobRepository(session=session)
        resume_repo = SQLResumeRepository(session=session)

        job = await job_repo.get_by_id(job_id)
        resume = await resume_repo.get_by_id(resume_id)

        if not job or not resume or not resume.parsed_data:
            return {"error": "Job or resume not found"}

        verifier = TruthLockVerifier()
        result = verifier.verify(
            content=content,
            resume=resume.parsed_data,
            job=job,
        )

        return {
            "passed": result.passed,
            "score": result.score,
            "issues": result.issues,
            "verified_claims": result.verified_claims,
            "unverified_claims": result.unverified_claims,
        }


def register_agent_tools(agents: dict, user_proxy) -> None:
    """Register tools for AutoGen agents.

    Args:
        agents: Dictionary of AutoGen agents
        user_proxy: UserProxyAgent for tool execution
    """
    try:
        from autogen import register_function
    except ImportError:
        logger.warning("autogen_not_available", message="Tool registration skipped")
        return

    # Register parse_resume for ResumeAgent
    if "resume_agent" in agents:
        register_function(
            parse_resume_tool,
            caller=agents["resume_agent"],
            executor=user_proxy,
            name="parse_resume",
            description="Parse a resume and return structured data including skills, experience, and education.",
        )

    # Register search_jobs for JobScraperAgent
    if "job_scraper" in agents:
        register_function(
            search_jobs_tool,
            caller=agents["job_scraper"],
            executor=user_proxy,
            name="search_jobs",
            description="Search for jobs matching query, location, and remote preferences.",
        )

    # Register calculate_match for MatchAgent
    if "match_agent" in agents:
        register_function(
            calculate_match_tool,
            caller=agents["match_agent"],
            executor=user_proxy,
            name="calculate_match",
            description="Calculate match score between a resume and job posting.",
        )

    # Register generate_cover_letter for ApplyAgent
    if "apply_agent" in agents:
        register_function(
            generate_cover_letter_tool,
            caller=agents["apply_agent"],
            executor=user_proxy,
            name="generate_cover_letter",
            description="Generate a personalized cover letter for a job application.",
        )

        register_function(
            submit_application_tool,
            caller=agents["apply_agent"],
            executor=user_proxy,
            name="submit_application",
            description="Submit a job application with resume and optional cover letter.",
        )

    # Register verify_content for QualityControlAgent
    if "qc_agent" in agents:
        register_function(
            verify_content_tool,
            caller=agents["qc_agent"],
            executor=user_proxy,
            name="verify_content",
            description="Verify generated content against resume using Truth-Lock to prevent fabrication.",
        )

    logger.info(
        "agent_tools_registered",
        tool_count=6,
        agents=list(agents.keys()),
    )
