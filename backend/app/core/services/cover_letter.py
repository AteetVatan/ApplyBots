"""Cover letter generation service.

Standards: python_clean.mdc
- LLM-powered generation
- Truth-Lock verification
- Async operations
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

import structlog

from app.core.domain.job import Job
from app.core.domain.resume import ParsedResume
from app.core.ports.llm import LLMClient, LLMMessage
from app.core.services.truth_lock import TruthLockVerifier

logger = structlog.get_logger(__name__)


class CoverLetterTone(str, Enum):
    """Cover letter tone options."""

    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    CONCISE = "concise"
    FORMAL = "formal"


@dataclass
class CoverLetterResult:
    """Result of cover letter generation."""

    content: str
    verified: bool
    verification_score: int
    issues: list[str]
    regeneration_count: int


COVER_LETTER_PROMPT = """Generate a cover letter for the following job application.

JOB DETAILS:
Title: {job_title}
Company: {company}
Description: {job_description}

CANDIDATE RESUME:
Name: {name}
Skills: {skills}
Experience: {experience}
Education: {education}

REQUIREMENTS:
1. Write a {tone} cover letter (3-4 paragraphs)
2. Hook with a relevant achievement from the resume
3. Connect actual experience to job requirements
4. Show enthusiasm for the company
5. End with a clear call to action

CRITICAL RULES:
- ONLY mention skills and experience ACTUALLY listed in the resume
- Do NOT fabricate or exaggerate any claims
- Do NOT claim skills not present in the resume
- If a required skill is missing from the resume, do not mention having it

Write the cover letter:"""


class CoverLetterService:
    """Service for generating cover letters using LLM.

    Uses Truth-Lock verification to prevent fabrication.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        truth_lock: TruthLockVerifier | None = None,
        max_regeneration_attempts: int = 3,
    ) -> None:
        """Initialize cover letter service.

        Args:
            llm_client: LLM client for generation
            truth_lock: Optional Truth-Lock verifier
            max_regeneration_attempts: Max attempts to regenerate on verification failure
        """
        self._llm = llm_client
        self._truth_lock = truth_lock or TruthLockVerifier()
        self._max_attempts = max_regeneration_attempts

    async def generate(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        tone: Literal["professional", "enthusiastic", "concise", "formal"] = "professional",
    ) -> CoverLetterResult:
        """Generate a cover letter for a job application.

        Args:
            resume: Parsed resume data
            job: Job to apply for
            tone: Writing tone

        Returns:
            CoverLetterResult with content and verification status
        """
        regeneration_count = 0
        all_issues: list[str] = []

        for attempt in range(self._max_attempts):
            # Build the prompt
            prompt = self._build_prompt(resume=resume, job=job, tone=tone)

            # Add context about previous issues if regenerating
            if all_issues:
                prompt += f"\n\nAVOID THESE ISSUES FROM PREVIOUS ATTEMPTS:\n"
                for issue in all_issues[-5:]:  # Last 5 issues
                    prompt += f"- {issue}\n"

            # Generate cover letter
            messages = [LLMMessage(role="user", content=prompt)]

            from app.agents.config import Models
            response = await self._llm.complete(
                messages=messages,
                model=Models.LLAMA3_70B,
                temperature=0.7 if attempt == 0 else 0.5,  # Lower temp on retry
                max_tokens=1500,
            )

            content = response.content.strip()

            # Verify with Truth-Lock
            verification = self._truth_lock.verify(
                content=content,
                resume=resume,
                job=job,
            )

            logger.info(
                "cover_letter_generated",
                attempt=attempt + 1,
                verified=verification.passed,
                score=verification.score,
                issues_count=len(verification.issues),
            )

            if verification.passed:
                return CoverLetterResult(
                    content=content,
                    verified=True,
                    verification_score=verification.score,
                    issues=[],
                    regeneration_count=regeneration_count,
                )

            # Track issues and regenerate
            all_issues.extend(verification.issues)
            regeneration_count += 1

        # Return best attempt with issues flagged
        logger.warning(
            "cover_letter_verification_failed",
            attempts=self._max_attempts,
            issues=all_issues,
        )

        return CoverLetterResult(
            content=content,
            verified=False,
            verification_score=verification.score,
            issues=all_issues,
            regeneration_count=regeneration_count,
        )

    def _build_prompt(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        tone: str,
    ) -> str:
        """Build the generation prompt.

        Args:
            resume: Parsed resume
            job: Target job
            tone: Writing tone

        Returns:
            Formatted prompt string
        """
        # Format experience
        experience_text = ""
        if resume.work_experience:
            for exp in resume.work_experience[:3]:
                exp_line = f"- {exp.title} at {exp.company}"
                if exp.start_date:
                    exp_line += f" ({exp.start_date}"
                    if exp.end_date:
                        exp_line += f" - {exp.end_date}"
                    exp_line += ")"
                experience_text += exp_line + "\n"
                if exp.achievements:
                    for ach in exp.achievements[:2]:
                        experience_text += f"  • {ach}\n"
        else:
            experience_text = "No work experience listed"

        # Format education
        education_text = ""
        if resume.education:
            for edu in resume.education[:2]:
                education_text += f"- {edu.degree} from {edu.institution}"
                if edu.graduation_year:
                    education_text += f" ({edu.graduation_year})"
                education_text += "\n"
        else:
            education_text = "Not specified"

        # Format skills
        skills_text = ", ".join(resume.skills[:15]) if resume.skills else "Not specified"

        # Truncate job description if needed
        job_desc = job.description[:2000] if job.description else "No description available"

        return COVER_LETTER_PROMPT.format(
            job_title=job.title,
            company=job.company,
            job_description=job_desc,
            name=resume.full_name or "Candidate",
            skills=skills_text,
            experience=experience_text,
            education=education_text,
            tone=tone,
        )

    async def generate_quick(
        self,
        *,
        resume: ParsedResume,
        job: Job,
    ) -> str:
        """Generate a quick cover letter without full verification.

        For preview/draft purposes only.

        Args:
            resume: Parsed resume
            job: Target job

        Returns:
            Generated cover letter text
        """
        prompt = self._build_prompt(resume=resume, job=job, tone="professional")
        messages = [LLMMessage(role="user", content=prompt)]

        from app.agents.config import Models
        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA3_70B,
            temperature=0.7,
            max_tokens=1500,
        )

        return response.content.strip()
