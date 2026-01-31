"""Answer learning service for personalized screening question answers.

Standards: python_clean.mdc
- Learns from user edits to improve future answers
- Uses vector similarity for few-shot example retrieval
- Stores edit history in PostgreSQL, embeddings in ChromaDB
"""

import re
from dataclasses import dataclass
from datetime import datetime

import structlog

from app.core.domain.job import Job
from app.core.ports.llm import LLMClient
from app.infra.vector.chroma_store import ChromaVectorStore

logger = structlog.get_logger(__name__)


def _get_user_answers_collection(user_id: str) -> str:
    """Get collection name for user's answer examples."""
    return f"user_answers_{user_id}"


@dataclass
class AnswerExample:
    """A user-edited answer example for few-shot learning."""

    question: str
    answer: str
    job_title: str
    job_company: str
    similarity_score: float


@dataclass
class AnswerStats:
    """Statistics about user's answer edits."""

    total_edits: int
    unique_questions: int
    last_edit_at: datetime | None


class AnswerLearningService:
    """Learns from user edits to screening question answers.

    Uses vector embeddings to find similar questions and retrieve
    user-preferred answer examples for few-shot prompting.
    """

    # Similarity threshold for considering examples relevant
    SIMILARITY_THRESHOLD = 0.65

    def __init__(
        self,
        *,
        vector_store: ChromaVectorStore,
        llm_client: LLMClient,
    ) -> None:
        """Initialize answer learning service.

        Args:
            vector_store: ChromaDB vector store for similarity search
            llm_client: LLM client for generating embeddings
        """
        self._vector = vector_store
        self._llm = llm_client

    async def record_edit(
        self,
        *,
        user_id: str,
        question: str,
        original_answer: str,
        edited_answer: str,
        job: Job,
    ) -> None:
        """Record a user's edit to a screening question answer.

        Args:
            user_id: User who edited the answer
            question: The screening question
            original_answer: AI-generated answer
            edited_answer: User's corrected answer
            job: The job being applied to
        """
        # Skip if no meaningful edit was made
        if self._normalize_text(original_answer) == self._normalize_text(edited_answer):
            logger.debug(
                "answer_edit_skipped_no_change",
                user_id=user_id,
                question=question[:50],
            )
            return

        collection = _get_user_answers_collection(user_id)
        normalized_question = self._normalize_question(question)
        doc_id = f"{user_id}_{hash(normalized_question)}"

        try:
            # Store in vector DB for similarity search
            await self._vector.add_document(
                collection=collection,
                doc_id=doc_id,
                text=normalized_question,
                metadata={
                    "question_original": question,
                    "edited_answer": edited_answer,
                    "job_title": job.title,
                    "job_company": job.company,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

            logger.info(
                "answer_edit_recorded",
                user_id=user_id,
                question=question[:50],
                job_title=job.title,
            )

        except Exception as e:
            logger.warning(
                "answer_edit_record_failed",
                user_id=user_id,
                question=question[:50],
                error=str(e),
            )

    async def get_similar_examples(
        self,
        *,
        user_id: str,
        question: str,
        top_k: int = 3,
    ) -> list[AnswerExample]:
        """Get similar question-answer examples from user's history.

        Args:
            user_id: User to get examples for
            question: Current question to find similar examples for
            top_k: Maximum number of examples to return

        Returns:
            List of similar answer examples, sorted by relevance
        """
        collection = _get_user_answers_collection(user_id)
        normalized_question = self._normalize_question(question)

        try:
            # Check if collection has any documents
            count = await self._vector.get_collection_count(collection)
            if count == 0:
                return []

            # Search for similar questions
            results = await self._vector.search(
                collection=collection,
                query_text=normalized_question,
                top_k=top_k,
            )

            examples: list[AnswerExample] = []
            for result in results:
                # Only include examples above similarity threshold
                if result.score < self.SIMILARITY_THRESHOLD:
                    continue

                examples.append(
                    AnswerExample(
                        question=result.metadata.get("question_original", ""),
                        answer=result.metadata.get("edited_answer", ""),
                        job_title=result.metadata.get("job_title", ""),
                        job_company=result.metadata.get("job_company", ""),
                        similarity_score=result.score,
                    )
                )

            logger.debug(
                "similar_examples_found",
                user_id=user_id,
                question=question[:50],
                examples_count=len(examples),
            )

            return examples

        except Exception as e:
            logger.warning(
                "similar_examples_search_failed",
                user_id=user_id,
                question=question[:50],
                error=str(e),
            )
            return []

    async def get_user_answer_stats(self, user_id: str) -> AnswerStats:
        """Get statistics about user's answer edit history.

        Args:
            user_id: User to get stats for

        Returns:
            AnswerStats with edit counts and last edit time
        """
        collection = _get_user_answers_collection(user_id)

        try:
            count = await self._vector.get_collection_count(collection)
            return AnswerStats(
                total_edits=count,
                unique_questions=count,  # Each doc is a unique question
                last_edit_at=None,  # Would need separate tracking
            )
        except Exception as e:
            logger.warning("answer_stats_failed", user_id=user_id, error=str(e))
            return AnswerStats(
                total_edits=0,
                unique_questions=0,
                last_edit_at=None,
            )

    async def clear_user_history(self, user_id: str) -> None:
        """Clear all answer learning data for a user.

        Args:
            user_id: User to clear data for
        """
        collection = _get_user_answers_collection(user_id)

        try:
            await self._vector.delete_collection(collection)
            logger.info("user_answer_history_cleared", user_id=user_id)
        except Exception as e:
            logger.warning(
                "user_answer_history_clear_failed",
                user_id=user_id,
                error=str(e),
            )

    def _normalize_question(self, question: str) -> str:
        """Normalize a question for consistent matching.

        Removes job-specific details to match similar question patterns.

        Args:
            question: Original question text

        Returns:
            Normalized question text
        """
        # Convert to lowercase
        normalized = question.lower().strip()

        # Remove common filler words that don't affect meaning
        filler_patterns = [
            r"\bplease\b",
            r"\bkindly\b",
            r"\bbriefly\b",
            r"\bin detail\b",
        ]
        for pattern in filler_patterns:
            normalized = re.sub(pattern, "", normalized)

        # Normalize whitespace
        normalized = " ".join(normalized.split())

        return normalized

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        return " ".join(text.lower().split())

    def format_few_shot_examples(
        self,
        examples: list[AnswerExample],
    ) -> str:
        """Format examples for injection into prompt.

        Args:
            examples: List of answer examples

        Returns:
            Formatted string for prompt injection
        """
        if not examples:
            return ""

        lines = [
            "SIMILAR QUESTIONS YOU'VE ANSWERED BEFORE (use as style guide):",
            "",
        ]

        for i, example in enumerate(examples, 1):
            lines.extend([
                f"Example {i}:",
                f"Question: {example.question}",
                f"Your preferred answer: {example.answer}",
                "---",
            ])

        return "\n".join(lines)
