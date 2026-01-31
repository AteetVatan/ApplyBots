"""Job preference learning service.

Standards: python_clean.mdc
- Learns from jobs users apply to
- Boosts similar job recommendations
- Uses vector similarity for preference matching
"""

from dataclasses import dataclass
from datetime import datetime

import structlog

from app.core.domain.job import Job
from app.core.ports.llm import LLMClient
from app.infra.vector.chroma_store import ChromaVectorStore

logger = structlog.get_logger(__name__)


def _get_user_applied_collection(user_id: str) -> str:
    """Get collection name for user's applied jobs."""
    return f"applied_jobs_{user_id}"


@dataclass
class SimilarAppliedJob:
    """A job similar to ones the user has applied to."""

    job_id: str
    title: str
    company: str
    similarity_score: float
    applied_at: str


class JobPreferenceService:
    """Learns from user job applications to improve recommendations.

    Uses vector embeddings to find jobs similar to those the user
    has applied to and boosts their match scores.
    """

    # Similarity thresholds for boosts
    HIGH_SIMILARITY_THRESHOLD = 0.80
    MEDIUM_SIMILARITY_THRESHOLD = 0.65

    # Boost factors (added to match score)
    HIGH_SIMILARITY_BOOST = 15  # +15 points for very similar jobs
    MEDIUM_SIMILARITY_BOOST = 8  # +8 points for moderately similar

    def __init__(
        self,
        *,
        vector_store: ChromaVectorStore,
        llm_client: LLMClient,
    ) -> None:
        """Initialize job preference service.

        Args:
            vector_store: ChromaDB vector store for similarity search
            llm_client: LLM client for generating embeddings
        """
        self._vector = vector_store
        self._llm = llm_client

    async def record_application(
        self,
        *,
        user_id: str,
        job: Job,
    ) -> None:
        """Record a job application to learn user preferences.

        Args:
            user_id: User who applied to the job
            job: The job applied to
        """
        collection = _get_user_applied_collection(user_id)
        job_text = self._build_job_text(job)

        try:
            await self._vector.add_document(
                collection=collection,
                doc_id=job.id,
                text=job_text,
                metadata={
                    "job_id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location or "",
                    "applied_at": datetime.utcnow().isoformat(),
                },
            )

            logger.info(
                "job_application_recorded",
                user_id=user_id,
                job_id=job.id,
                title=job.title,
                company=job.company,
            )

        except Exception as e:
            logger.warning(
                "job_application_record_failed",
                user_id=user_id,
                job_id=job.id,
                error=str(e),
            )

    async def get_preference_boost(
        self,
        *,
        user_id: str,
        job: Job,
    ) -> int:
        """Calculate preference boost for a job based on applied job similarity.

        Args:
            user_id: User to calculate boost for
            job: Job to evaluate

        Returns:
            Boost value (0, 8, or 15) to add to match score
        """
        collection = _get_user_applied_collection(user_id)
        job_text = self._build_job_text(job)

        try:
            # Check if user has any applied jobs
            count = await self._vector.get_collection_count(collection)
            if count == 0:
                return 0

            # Search for similar applied jobs
            results = await self._vector.search(
                collection=collection,
                query_text=job_text,
                top_k=5,
            )

            if not results:
                return 0

            # Get highest similarity score
            top_score = results[0].score

            # Apply boost based on similarity
            if top_score >= self.HIGH_SIMILARITY_THRESHOLD:
                logger.debug(
                    "high_preference_boost",
                    user_id=user_id,
                    job_id=job.id,
                    similarity=top_score,
                    boost=self.HIGH_SIMILARITY_BOOST,
                )
                return self.HIGH_SIMILARITY_BOOST

            elif top_score >= self.MEDIUM_SIMILARITY_THRESHOLD:
                logger.debug(
                    "medium_preference_boost",
                    user_id=user_id,
                    job_id=job.id,
                    similarity=top_score,
                    boost=self.MEDIUM_SIMILARITY_BOOST,
                )
                return self.MEDIUM_SIMILARITY_BOOST

            return 0

        except Exception as e:
            logger.warning(
                "preference_boost_check_failed",
                user_id=user_id,
                job_id=job.id,
                error=str(e),
            )
            return 0

    async def get_similar_applied_jobs(
        self,
        *,
        user_id: str,
        job: Job,
        top_k: int = 5,
    ) -> list[SimilarAppliedJob]:
        """Get applied jobs similar to the given job.

        Args:
            user_id: User to get applied jobs for
            job: Job to find similar applied jobs for
            top_k: Number of similar jobs to return

        Returns:
            List of similar applied jobs
        """
        collection = _get_user_applied_collection(user_id)
        job_text = self._build_job_text(job)

        try:
            results = await self._vector.search(
                collection=collection,
                query_text=job_text,
                top_k=top_k,
            )

            return [
                SimilarAppliedJob(
                    job_id=r.metadata.get("job_id", r.id),
                    title=r.metadata.get("title", ""),
                    company=r.metadata.get("company", ""),
                    similarity_score=r.score,
                    applied_at=r.metadata.get("applied_at", ""),
                )
                for r in results
            ]

        except Exception as e:
            logger.warning(
                "similar_applied_jobs_search_failed",
                user_id=user_id,
                error=str(e),
            )
            return []

    async def get_applied_count(self, user_id: str) -> int:
        """Get the number of jobs the user has applied to.

        Args:
            user_id: User to count applications for

        Returns:
            Number of applied jobs in the learning collection
        """
        collection = _get_user_applied_collection(user_id)

        try:
            return await self._vector.get_collection_count(collection)
        except Exception as e:
            logger.warning("applied_count_failed", user_id=user_id, error=str(e))
            return 0

    async def clear_user_preferences(self, user_id: str) -> None:
        """Clear all preference data for a user.

        Args:
            user_id: User to clear preferences for
        """
        collection = _get_user_applied_collection(user_id)

        try:
            await self._vector.delete_collection(collection)
            logger.info("user_preferences_cleared", user_id=user_id)
        except Exception as e:
            logger.warning(
                "user_preferences_clear_failed",
                user_id=user_id,
                error=str(e),
            )

    def _build_job_text(self, job: Job) -> str:
        """Build text representation of job for embedding.

        Args:
            job: Job to convert to text

        Returns:
            Text suitable for embedding
        """
        # Combine title, company, and truncated description
        description = job.description[:500] if job.description else ""

        parts = [
            f"Title: {job.title}",
            f"Company: {job.company}",
        ]

        if job.location:
            parts.append(f"Location: {job.location}")

        # Include required skills if available
        if job.requirements and job.requirements.required_skills:
            skills = ", ".join(job.requirements.required_skills[:10])
            parts.append(f"Required Skills: {skills}")

        if description:
            parts.append(f"Description: {description}")

        return " | ".join(parts)
