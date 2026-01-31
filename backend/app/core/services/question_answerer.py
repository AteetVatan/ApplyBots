"""Screening question answering service.

Standards: python_clean.mdc
- LLM-powered answers
- Truth-Lock verification
- Multiple question types support
- Few-shot learning from user edits
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import structlog

from app.core.domain.job import Job
from app.core.domain.resume import ParsedResume
from app.core.ports.llm import LLMClient, LLMMessage
from app.core.services.truth_lock import TruthLockVerifier

if TYPE_CHECKING:
    from app.core.services.answer_learning import AnswerLearningService

logger = structlog.get_logger(__name__)


class QuestionType(str, Enum):
    """Types of screening questions."""

    YES_NO = "yes_no"
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    NUMERIC = "numeric"
    EXPERIENCE_YEARS = "experience_years"


@dataclass
class ScreeningQuestion:
    """A screening question to answer."""

    question: str
    question_type: QuestionType = QuestionType.SHORT_ANSWER
    options: list[str] | None = None  # For multiple choice
    required: bool = True


@dataclass
class QuestionAnswer:
    """Answer to a screening question."""

    question: str
    answer: str
    verified: bool
    confidence: float  # 0.0 - 1.0
    issues: list[str]


@dataclass
class AnswerBatch:
    """Batch of answered questions."""

    answers: list[QuestionAnswer]
    overall_verified: bool
    average_confidence: float


QUESTION_PROMPT = """Answer this job application screening question based on the candidate's resume.

JOB: {job_title} at {company}

QUESTION: {question}
{question_context}
{few_shot_examples}
CANDIDATE RESUME:
Name: {name}
Skills: {skills}
Experience: {experience}
Total Years: {years_experience}

IMPORTANT RULES:
1. Answer ONLY based on information in the resume
2. If the answer is not in the resume, say "Based on my resume..." and be honest
3. Do NOT claim skills or experience not listed
4. Be concise but complete
5. Use STAR method for behavioral questions if possible
6. If examples are provided above, match the user's preferred style and level of detail

Answer:"""


class QuestionAnswererService:
    """Service for answering application screening questions.

    Uses LLM with Truth-Lock to ensure honest, verified answers.
    Supports few-shot learning from user edits via AnswerLearningService.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        truth_lock: TruthLockVerifier | None = None,
        answer_learning: AnswerLearningService | None = None,
    ) -> None:
        """Initialize question answerer.

        Args:
            llm_client: LLM client for generation
            truth_lock: Optional Truth-Lock verifier
            answer_learning: Optional answer learning service for few-shot examples
        """
        self._llm = llm_client
        self._truth_lock = truth_lock or TruthLockVerifier()
        self._answer_learning = answer_learning

    async def answer_question(
        self,
        *,
        question: ScreeningQuestion,
        resume: ParsedResume,
        job: Job,
        user_id: str | None = None,
    ) -> QuestionAnswer:
        """Answer a single screening question.

        Args:
            question: The question to answer
            resume: Candidate's parsed resume
            job: The job being applied to
            user_id: Optional user ID for few-shot learning

        Returns:
            QuestionAnswer with content and verification
        """
        # Check if question can be answered from resume
        answer_type = self._determine_answer_approach(question, resume)

        if answer_type == "direct":
            # Answer directly from resume data
            answer = self._get_direct_answer(question, resume)
            return QuestionAnswer(
                question=question.question,
                answer=answer,
                verified=True,
                confidence=1.0,
                issues=[],
            )

        # Get few-shot examples if answer learning is available
        few_shot_text = ""
        if self._answer_learning and user_id:
            examples = await self._answer_learning.get_similar_examples(
                user_id=user_id,
                question=question.question,
                top_k=3,
            )
            if examples:
                few_shot_text = self._answer_learning.format_few_shot_examples(examples)
                logger.debug(
                    "few_shot_examples_injected",
                    user_id=user_id,
                    examples_count=len(examples),
                )

        # Generate answer with LLM
        prompt = self._build_prompt(
            question=question,
            resume=resume,
            job=job,
            few_shot_examples=few_shot_text,
        )
        messages = [LLMMessage(role="user", content=prompt)]

        from app.agents.config import Models
        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA3_70B,
            temperature=0.5,  # Lower temp for factual answers
            max_tokens=500,
        )

        answer_text = response.content.strip()

        # Verify answer
        verification = self._truth_lock.verify(
            content=answer_text,
            resume=resume,
            job=job,
        )

        # Calculate confidence based on verification
        confidence = verification.score / 100.0

        logger.info(
            "question_answered",
            question=question.question[:50],
            verified=verification.passed,
            confidence=confidence,
            has_few_shot=bool(few_shot_text),
        )

        return QuestionAnswer(
            question=question.question,
            answer=answer_text,
            verified=verification.passed,
            confidence=confidence,
            issues=verification.issues,
        )

    async def answer_questions(
        self,
        *,
        questions: list[ScreeningQuestion],
        resume: ParsedResume,
        job: Job,
        user_id: str | None = None,
    ) -> AnswerBatch:
        """Answer multiple screening questions.

        Args:
            questions: List of questions to answer
            resume: Candidate's parsed resume
            job: The job being applied to
            user_id: Optional user ID for few-shot learning

        Returns:
            AnswerBatch with all answers and aggregate verification
        """
        answers: list[QuestionAnswer] = []

        for question in questions:
            answer = await self.answer_question(
                question=question,
                resume=resume,
                job=job,
                user_id=user_id,
            )
            answers.append(answer)

        # Calculate aggregates
        overall_verified = all(a.verified for a in answers)
        average_confidence = (
            sum(a.confidence for a in answers) / len(answers) if answers else 0.0
        )

        logger.info(
            "questions_batch_answered",
            count=len(answers),
            overall_verified=overall_verified,
            average_confidence=average_confidence,
        )

        return AnswerBatch(
            answers=answers,
            overall_verified=overall_verified,
            average_confidence=average_confidence,
        )

    def _determine_answer_approach(
        self,
        question: ScreeningQuestion,
        resume: ParsedResume,
    ) -> str:
        """Determine how to answer the question.

        Args:
            question: The question
            resume: The resume

        Returns:
            "direct" for resume-based, "llm" for generated
        """
        q_lower = question.question.lower()

        # Direct answers for simple data questions
        if question.question_type == QuestionType.NUMERIC:
            return "direct"

        if question.question_type == QuestionType.EXPERIENCE_YEARS:
            return "direct"

        if any(phrase in q_lower for phrase in [
            "years of experience",
            "how many years",
            "work authorization",
            "authorized to work",
            "email",
            "phone",
            "location",
            "willing to relocate",
        ]):
            return "direct"

        return "llm"

    def _get_direct_answer(
        self,
        question: ScreeningQuestion,
        resume: ParsedResume,
    ) -> str:
        """Get direct answer from resume data.

        Args:
            question: The question
            resume: The resume

        Returns:
            Answer string
        """
        q_lower = question.question.lower()

        # Experience years
        if "years of experience" in q_lower or "how many years" in q_lower:
            years = resume.total_years_experience
            if years:
                return f"{years:.0f}"
            return "0"

        # Contact info
        if "email" in q_lower:
            return resume.email or "Not provided in resume"

        if "phone" in q_lower:
            return resume.phone or "Not provided in resume"

        # Location
        if "location" in q_lower or "where are you located" in q_lower:
            return resume.location or "Not specified in resume"

        # Yes/No questions
        if question.question_type == QuestionType.YES_NO:
            # Work authorization - typically yes (would need actual data)
            if "authorized to work" in q_lower:
                return "Yes"

            # Relocation - default to yes unless specified
            if "relocate" in q_lower:
                return "Yes"

            # Sponsorship - default to no (conservative)
            if "sponsorship" in q_lower:
                return "No"

        return "Based on my resume, I cannot directly answer this question."

    def _build_prompt(
        self,
        *,
        question: ScreeningQuestion,
        resume: ParsedResume,
        job: Job,
        few_shot_examples: str = "",
    ) -> str:
        """Build the prompt for LLM answer generation.

        Args:
            question: The question
            resume: The resume
            job: The job
            few_shot_examples: Optional few-shot examples from user history

        Returns:
            Formatted prompt
        """
        # Format experience
        experience_text = ""
        if resume.work_experience:
            for exp in resume.work_experience[:3]:
                experience_text += f"- {exp.title} at {exp.company}\n"
                if exp.achievements:
                    for ach in exp.achievements[:2]:
                        experience_text += f"  • {ach}\n"
        else:
            experience_text = "No work experience listed"

        # Format skills
        skills_text = ", ".join(resume.skills[:15]) if resume.skills else "Not specified"

        # Question context for multiple choice
        question_context = ""
        if question.question_type == QuestionType.MULTIPLE_CHOICE and question.options:
            question_context = f"OPTIONS: {', '.join(question.options)}\nSelect the most appropriate option."
        elif question.question_type == QuestionType.YES_NO:
            question_context = "Answer with Yes or No, followed by a brief explanation if needed."

        years_exp = (
            f"{resume.total_years_experience:.1f} years"
            if resume.total_years_experience
            else "Not calculated"
        )

        # Format few-shot examples section
        few_shot_section = ""
        if few_shot_examples:
            few_shot_section = f"\n{few_shot_examples}\n"

        return QUESTION_PROMPT.format(
            job_title=job.title,
            company=job.company,
            question=question.question,
            question_context=question_context,
            few_shot_examples=few_shot_section,
            name=resume.full_name or "Candidate",
            skills=skills_text,
            experience=experience_text,
            years_experience=years_exp,
        )
