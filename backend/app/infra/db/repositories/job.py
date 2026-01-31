"""Job repository implementation.

Standards: python_clean.mdc
- Vector similarity search for semantic matching
- Supports keyword and learned recommendation modes
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.campaign import RecommendationMode
from app.core.domain.job import Job, JobRequirements, JobSource
from app.core.ports.vector_store import VectorStore
from app.infra.db.models import JobModel

# Collection name for job embeddings
JOBS_COLLECTION = "jobs"


class SQLJobRepository:
    """SQLAlchemy implementation of JobRepository."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        vector_store: VectorStore | None = None,
    ) -> None:
        self._session = session
        self._vector_store = vector_store

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
        resume_embedding: list[float] | None = None,
        negative_keywords: list[str] | None = None,
        recommendation_mode: RecommendationMode = RecommendationMode.KEYWORD,
        applied_jobs_embedding: list[float] | None = None,
    ) -> list[Job]:
        """Find jobs matching user preferences.

        Uses different strategies based on recommendation mode:
        - KEYWORD: Traditional keyword/filter matching with resume similarity
        - LEARNED: Uses applied jobs embedding for preference-based search

        Args:
            user_id: User ID for preference lookup
            limit: Maximum number of results
            offset: Pagination offset
            resume_embedding: User's resume embedding for semantic search
            negative_keywords: Keywords to exclude from results
            recommendation_mode: Mode determining search strategy
            applied_jobs_embedding: Centroid embedding of applied jobs (for LEARNED mode)

        Returns:
            List of matching jobs, sorted by relevance
        """
        # Determine which embedding to use based on mode
        search_embedding = None

        if recommendation_mode == RecommendationMode.LEARNED and applied_jobs_embedding:
            # LEARNED mode: use applied jobs embedding for personalized recommendations
            search_embedding = applied_jobs_embedding
        elif resume_embedding:
            # KEYWORD mode or fallback: use resume embedding
            search_embedding = resume_embedding

        # If vector store is available and we have an embedding, use semantic search
        if self._vector_store and search_embedding:
            jobs = await self._find_matching_semantic(
                embedding=search_embedding,
                limit=limit * 2,  # Get extra to account for filtering
                offset=offset,
            )
        else:
            # Fallback to recent jobs
            jobs = await self.get_recent(limit=limit * 2, offset=offset)

        # Apply negative keywords filter
        if negative_keywords:
            jobs = self._filter_negative_keywords(jobs=jobs, keywords=negative_keywords)

        # Return requested limit
        return jobs[:limit]

    def _filter_negative_keywords(
        self,
        *,
        jobs: list[Job],
        keywords: list[str],
    ) -> list[Job]:
        """Filter out jobs containing negative keywords.

        Args:
            jobs: List of jobs to filter
            keywords: Keywords to exclude

        Returns:
            Filtered list of jobs
        """
        if not keywords:
            return jobs

        # Normalize keywords for comparison
        keywords_lower = [kw.lower().strip() for kw in keywords if kw.strip()]

        filtered_jobs = []
        for job in jobs:
            # Check title, company, and description
            title_lower = job.title.lower()
            company_lower = job.company.lower()
            desc_lower = job.description.lower() if job.description else ""

            # Check if any negative keyword is present
            has_negative = False
            for kw in keywords_lower:
                if (
                    kw in title_lower
                    or kw in company_lower
                    or kw in desc_lower
                ):
                    has_negative = True
                    break

            if not has_negative:
                filtered_jobs.append(job)

        return filtered_jobs

    async def _find_matching_semantic(
        self,
        *,
        embedding: list[float],
        limit: int,
        offset: int,
    ) -> list[Job]:
        """Find matching jobs using vector similarity search.

        Args:
            embedding: Query embedding (from resume)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Jobs sorted by semantic similarity
        """
        # Search vector store for similar jobs
        # Request more results to account for offset
        search_results = await self._vector_store.search_by_embedding(
            collection=JOBS_COLLECTION,
            embedding=embedding,
            top_k=limit + offset,
        )

        if not search_results:
            return await self.get_recent(limit=limit, offset=offset)

        # Get job IDs from search results (applying offset)
        job_ids = [result.id for result in search_results[offset : offset + limit]]

        if not job_ids:
            return []

        # Fetch jobs from database
        jobs = await self._get_by_ids(job_ids)

        # Preserve order from vector search (by similarity score)
        id_to_job = {job.id: job for job in jobs}
        ordered_jobs = [id_to_job[job_id] for job_id in job_ids if job_id in id_to_job]

        return ordered_jobs

    async def _get_by_ids(self, job_ids: list[str]) -> list[Job]:
        """Get multiple jobs by their IDs.

        Args:
            job_ids: List of job IDs

        Returns:
            List of jobs
        """
        if not job_ids:
            return []

        stmt = select(JobModel).where(JobModel.id.in_(job_ids))
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_recent(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Job]:
        """Get recently ingested jobs.

        Args:
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Recent jobs sorted by ingestion date
        """
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
