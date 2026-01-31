"""Job feedback service for learning from user rejections.

Standards: python_clean.mdc
- Uses ChromaDB for similarity matching
- Pattern learning from rejected jobs
"""

import structlog

from app.core.domain.job import Job
from app.core.ports.llm import LLMClient
from app.infra.vector.chroma_store import ChromaVectorStore

logger = structlog.get_logger(__name__)


def _get_user_rejected_collection(user_id: str) -> str:
    """Get collection name for user's rejected jobs."""
    return f"rejected_jobs_{user_id}"


class JobFeedbackService:
    """Learns from user job rejections to improve recommendations.

    Uses vector embeddings to find similar jobs and apply penalties
    to avoid recommending similar unwanted jobs.
    """

    # Similarity thresholds for penalties
    HIGH_SIMILARITY_THRESHOLD = 0.85
    MEDIUM_SIMILARITY_THRESHOLD = 0.70

    # Penalty factors (applied as multiplier reduction)
    HIGH_SIMILARITY_PENALTY = 0.50  # 50% score reduction
    MEDIUM_SIMILARITY_PENALTY = 0.25  # 25% score reduction

    def __init__(
        self,
        *,
        vector_store: ChromaVectorStore,
        llm_client: LLMClient,
    ) -> None:
        """Initialize job feedback service.

        Args:
            vector_store: ChromaDB vector store for similarity search
            llm_client: LLM client for generating embeddings
        """
        self._vector = vector_store
        self._llm = llm_client

    async def record_rejection(
        self,
        *,
        user_id: str,
        campaign_id: str,
        job: Job,
        reason: str | None = None,
    ) -> None:
        """Store rejected job embedding for similarity matching.

        Args:
            user_id: User who rejected the job
            campaign_id: Campaign the job was rejected from
            job: The rejected job
            reason: Optional rejection reason
        """
        # Build text representation for embedding
        job_text = self._build_job_text(job)
        collection = _get_user_rejected_collection(user_id)

        try:
            await self._vector.add_document(
                collection=collection,
                doc_id=job.id,
                text=job_text,
                metadata={
                    "campaign_id": campaign_id,
                    "company": job.company,
                    "title": job.title,
                    "reason": reason or "user_rejected",
                    "source": job.source.value,
                },
            )

            logger.info(
                "job_rejection_recorded",
                user_id=user_id,
                campaign_id=campaign_id,
                job_id=job.id,
                company=job.company,
                title=job.title,
            )

        except Exception as e:
            logger.warning(
                "job_rejection_record_failed",
                user_id=user_id,
                job_id=job.id,
                error=str(e),
            )

    async def get_similarity_penalty(
        self,
        *,
        user_id: str,
        job: Job,
    ) -> float:
        """Check if job is similar to rejected jobs, return penalty.

        Args:
            user_id: User to check rejections for
            job: Job to evaluate

        Returns:
            Penalty factor 0.0-1.0 (0.0 = no penalty, 0.5 = 50% penalty)
        """
        collection = _get_user_rejected_collection(user_id)
        job_text = self._build_job_text(job)

        try:
            # Check if collection exists and has documents
            count = await self._vector.get_collection_count(collection)
            if count == 0:
                return 0.0

            # Search for similar rejected jobs
            results = await self._vector.search(
                collection=collection,
                query_text=job_text,
                top_k=5,
            )

            if not results:
                return 0.0

            # Get highest similarity score
            top_score = results[0].score

            # Apply penalty based on similarity
            if top_score >= self.HIGH_SIMILARITY_THRESHOLD:
                logger.debug(
                    "high_similarity_penalty",
                    user_id=user_id,
                    job_id=job.id,
                    similarity=top_score,
                    penalty=self.HIGH_SIMILARITY_PENALTY,
                )
                return self.HIGH_SIMILARITY_PENALTY

            elif top_score >= self.MEDIUM_SIMILARITY_THRESHOLD:
                logger.debug(
                    "medium_similarity_penalty",
                    user_id=user_id,
                    job_id=job.id,
                    similarity=top_score,
                    penalty=self.MEDIUM_SIMILARITY_PENALTY,
                )
                return self.MEDIUM_SIMILARITY_PENALTY

            return 0.0

        except Exception as e:
            logger.warning(
                "similarity_penalty_check_failed",
                user_id=user_id,
                job_id=job.id,
                error=str(e),
            )
            return 0.0

    async def get_similar_rejected_jobs(
        self,
        *,
        user_id: str,
        job: Job,
        top_k: int = 5,
    ) -> list[dict]:
        """Get rejected jobs similar to the given job.

        Args:
            user_id: User to check rejections for
            job: Job to find similar rejections for
            top_k: Number of similar jobs to return

        Returns:
            List of similar rejected job metadata
        """
        collection = _get_user_rejected_collection(user_id)
        job_text = self._build_job_text(job)

        try:
            results = await self._vector.search(
                collection=collection,
                query_text=job_text,
                top_k=top_k,
            )

            return [
                {
                    "job_id": r.id,
                    "similarity": r.score,
                    "company": r.metadata.get("company"),
                    "title": r.metadata.get("title"),
                    "reason": r.metadata.get("reason"),
                }
                for r in results
            ]

        except Exception as e:
            logger.warning(
                "similar_jobs_search_failed",
                user_id=user_id,
                error=str(e),
            )
            return []

    async def calculate_adjusted_score(
        self,
        *,
        user_id: str,
        job: Job,
        base_score: int,
    ) -> int:
        """Calculate adjusted match score after applying feedback penalty.

        Args:
            user_id: User to check feedback for
            job: Job to score
            base_score: Original match score

        Returns:
            Adjusted score after penalty
        """
        penalty = await self.get_similarity_penalty(
            user_id=user_id,
            job=job,
        )

        if penalty == 0.0:
            return base_score

        adjusted = int(base_score * (1 - penalty))

        logger.debug(
            "score_adjusted",
            user_id=user_id,
            job_id=job.id,
            base_score=base_score,
            penalty=penalty,
            adjusted_score=adjusted,
        )

        return adjusted

    async def clear_user_feedback(self, user_id: str) -> None:
        """Clear all feedback data for a user.

        Args:
            user_id: User to clear feedback for
        """
        collection = _get_user_rejected_collection(user_id)

        try:
            await self._vector.delete_collection(collection)
            logger.info("user_feedback_cleared", user_id=user_id)
        except Exception as e:
            logger.warning(
                "user_feedback_clear_failed",
                user_id=user_id,
                error=str(e),
            )

    async def get_rejection_count(self, user_id: str) -> int:
        """Get count of rejected jobs for a user.

        Args:
            user_id: User to count rejections for

        Returns:
            Number of rejected jobs
        """
        collection = _get_user_rejected_collection(user_id)

        try:
            return await self._vector.get_collection_count(collection)
        except Exception as e:
            logger.warning("rejection_count_failed", user_id=user_id, error=str(e))
            return 0

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

        if description:
            parts.append(f"Description: {description}")

        return " | ".join(parts)
