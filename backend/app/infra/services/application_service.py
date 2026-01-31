"""Application processing service.

Standards: python_clean.mdc
- Coordinates matching and content generation
"""

import uuid
from datetime import datetime

from app.core.domain.application import Application, ApplicationStatus
from app.core.ports.repositories import ApplicationRepository, JobRepository, ResumeRepository
from app.core.services.matcher import MatchService


class ApplicationService:
    """Service for creating and processing job applications."""

    def __init__(
        self,
        *,
        application_repository: ApplicationRepository,
        job_repository: JobRepository,
        resume_repository: ResumeRepository,
    ) -> None:
        self._app_repo = application_repository
        self._job_repo = job_repository
        self._resume_repo = resume_repository
        self._match_service = MatchService()

    async def create_application(
        self,
        *,
        user_id: str,
        job_id: str,
        resume_id: str,
    ) -> Application:
        """Create a new application with match scoring."""
        # Get job and resume
        job = await self._job_repo.get_by_id(job_id)
        resume = await self._resume_repo.get_by_id(resume_id)

        if not job or not resume:
            raise ValueError("Job or resume not found")

        # Calculate match score
        match_score = 0
        if resume.parsed_data:
            score, _ = self._match_service.calculate_score(
                resume=resume.parsed_data,
                job=job,
            )
            match_score = score

        # Create application
        application = Application(
            id=str(uuid.uuid4()),
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=ApplicationStatus.PENDING_REVIEW,
            match_score=match_score,
            created_at=datetime.utcnow(),
        )

        return await self._app_repo.create(application)
