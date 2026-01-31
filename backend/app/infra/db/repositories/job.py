"""Job repository implementation."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.job import Job, JobRequirements, JobSource
from app.infra.db.models import JobModel


class SQLJobRepository:
    """SQLAlchemy implementation of JobRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, job_id: str) -> Job | None:
        """Get job by ID."""
        result = await self._session.get(JobModel, job_id)
        return self._to_domain(result) if result else None

    async def get_by_external_id(self, external_id: str) -> Job | None:
        """Get job by external ID (for deduplication)."""
        stmt = select(JobModel).where(JobModel.external_id == external_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_matching(
        self,
        *,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Job]:
        """Find jobs matching user preferences."""
        # For now, return recent jobs - matching would use vector search
        stmt = (
            select(JobModel)
            .order_by(JobModel.ingested_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, job: Job) -> Job:
        """Create a new job."""
        model = JobModel(
            id=job.id,
            external_id=job.external_id,
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            url=job.url,
            source=job.source,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            remote=job.remote,
            requirements=self._requirements_to_dict(job.requirements),
            embedding=job.embedding,
            posted_at=job.posted_at,
            ingested_at=job.ingested_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def upsert(self, job: Job) -> Job:
        """Create or update a job."""
        existing = await self.get_by_external_id(job.external_id)
        if existing:
            # Update existing job
            model = await self._session.get(JobModel, existing.id)
            if model:
                model.title = job.title
                model.company = job.company
                model.location = job.location
                model.description = job.description
                model.url = job.url
                model.salary_min = job.salary_min
                model.salary_max = job.salary_max
                model.remote = job.remote
                model.requirements = self._requirements_to_dict(job.requirements)
                model.embedding = job.embedding
                await self._session.flush()
                return self._to_domain(model)
        return await self.create(job)

    async def count(self) -> int:
        """Count total jobs."""
        stmt = select(func.count()).select_from(JobModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _to_domain(self, model: JobModel) -> Job:
        """Convert ORM model to domain entity."""
        req_dict = model.requirements or {}
        requirements = JobRequirements(
            required_skills=req_dict.get("required_skills", []),
            preferred_skills=req_dict.get("preferred_skills", []),
            experience_years_min=req_dict.get("experience_years_min"),
            experience_years_max=req_dict.get("experience_years_max"),
            education_level=req_dict.get("education_level"),
            certifications=req_dict.get("certifications", []),
        )
        return Job(
            id=model.id,
            external_id=model.external_id,
            title=model.title,
            company=model.company,
            location=model.location,
            description=model.description,
            url=model.url,
            source=model.source,
            salary_min=model.salary_min,
            salary_max=model.salary_max,
            salary_currency=model.salary_currency,
            remote=model.remote,
            requirements=requirements,
            embedding=model.embedding,
            posted_at=model.posted_at,
            ingested_at=model.ingested_at,
        )

    def _requirements_to_dict(self, requirements: JobRequirements) -> dict:
        """Convert JobRequirements to dict for JSON storage."""
        return {
            "required_skills": requirements.required_skills,
            "preferred_skills": requirements.preferred_skills,
            "experience_years_min": requirements.experience_years_min,
            "experience_years_max": requirements.experience_years_max,
            "education_level": requirements.education_level,
            "certifications": requirements.certifications,
        }
