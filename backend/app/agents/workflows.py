"""Agent workflow orchestration.

Standards: python_clean.mdc
- Async operations
- Proper error handling
"""

from dataclasses import dataclass, field
from typing import AsyncIterator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings

logger = structlog.get_logger()


@dataclass
class AgentResponse:
    """Response from agent workflow."""

    content: str
    session_id: str
    agents_involved: list[str] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)


@dataclass
class StreamResponse:
    """Streaming response from agent."""

    agent_name: str
    content: str
    is_final: bool = False


@dataclass
class OptimizationResult:
    """Result of resume optimization."""

    original_score: int
    optimized_score: int
    suggestions: list[str]
    tailored_summary: str | None
    highlighted_skills: list[str]


class JobApplicationWorkflow:
    """Orchestrates multi-agent job application workflow."""

    def __init__(
        self,
        *,
        user_id: str,
        db_session: AsyncSession,
        settings: Settings,
    ) -> None:
        self._user_id = user_id
        self._db = db_session
        self._settings = settings
        self._session_id: str | None = None

    async def process_message(
        self,
        message: str,
        session_id: str | None = None,
    ) -> AgentResponse:
        """Process a user message through the agent system.

        This is a simplified implementation. Full AutoGen integration
        would use GroupChat for multi-agent coordination.
        """
        import uuid

        self._session_id = session_id or str(uuid.uuid4())

        # For MVP, we'll use a simple prompt-based approach
        # Full implementation would use AutoGen GroupChat

        try:
            # Analyze intent
            intent = self._analyze_intent(message)

            if "job" in intent.lower() or "search" in intent.lower():
                return await self._handle_job_search(message)
            elif "resume" in intent.lower() or "optimize" in intent.lower():
                return await self._handle_resume_query(message)
            elif "apply" in intent.lower():
                return await self._handle_apply_query(message)
            else:
                return await self._handle_general_query(message)

        except Exception as e:
            logger.error(
                "workflow_error",
                error=str(e),
                user_id=self._user_id,
            )
            return AgentResponse(
                content="I encountered an error processing your request. Please try again.",
                session_id=self._session_id,
                agents_involved=["Orchestrator"],
                actions_taken=["error_handling"],
            )

    async def stream_process(
        self,
        message: str,
    ) -> AsyncIterator[StreamResponse]:
        """Stream agent responses for real-time updates."""
        import uuid

        self._session_id = str(uuid.uuid4())

        # Yield orchestrator thinking
        yield StreamResponse(
            agent_name="Orchestrator",
            content="Analyzing your request...",
            is_final=False,
        )

        # Process and yield final response
        response = await self.process_message(message, self._session_id)

        yield StreamResponse(
            agent_name="Orchestrator",
            content=response.content,
            is_final=True,
        )

    async def optimize_resume(
        self,
        *,
        resume_id: str,
        job_id: str,
    ) -> OptimizationResult:
        """Optimize resume for a specific job."""
        from app.core.services.matcher import MatchService
        from app.infra.db.repositories.job import SQLJobRepository
        from app.infra.db.repositories.resume import SQLResumeRepository

        job_repo = SQLJobRepository(session=self._db)
        resume_repo = SQLResumeRepository(session=self._db)
        match_service = MatchService()

        job = await job_repo.get_by_id(job_id)
        resume = await resume_repo.get_by_id(resume_id)

        if not job or not resume or not resume.parsed_data:
            raise ValueError("Job or resume not found")

        # Calculate original score
        original_score, explanation = match_service.calculate_score(
            resume=resume.parsed_data,
            job=job,
        )

        # Generate suggestions based on gaps
        suggestions = []
        if explanation.skills_missing:
            suggestions.append(
                f"Consider highlighting these skills if you have them: {', '.join(explanation.skills_missing[:5])}"
            )
        if explanation.experience_gap:
            suggestions.append(f"Experience note: {explanation.experience_gap}")

        # Identify skills to highlight
        highlighted_skills = explanation.skills_matched[:10]

        # Generate tailored summary (simplified - would use LLM in production)
        tailored_summary = self._generate_tailored_summary(resume.parsed_data, job)

        return OptimizationResult(
            original_score=original_score,
            optimized_score=min(100, original_score + 10),  # Optimistic estimate
            suggestions=suggestions,
            tailored_summary=tailored_summary,
            highlighted_skills=highlighted_skills,
        )

    def _analyze_intent(self, message: str) -> str:
        """Simple intent analysis based on keywords."""
        message_lower = message.lower()

        if any(kw in message_lower for kw in ["find job", "search", "looking for"]):
            return "job_search"
        elif any(kw in message_lower for kw in ["resume", "cv", "optimize"]):
            return "resume"
        elif any(kw in message_lower for kw in ["apply", "submit", "application"]):
            return "apply"
        else:
            return "general"

    async def _handle_job_search(self, message: str) -> AgentResponse:
        """Handle job search queries."""
        return AgentResponse(
            content=(
                "I can help you find jobs! Here's what I can do:\n\n"
                "1. Search for jobs matching your profile\n"
                "2. Filter by location, salary, and remote options\n"
                "3. Show match scores for each job\n\n"
                "Check the Jobs tab to see your personalized matches, or tell me "
                "specific criteria you're looking for."
            ),
            session_id=self._session_id or "",
            agents_involved=["Orchestrator", "JobScraperAgent"],
            actions_taken=["intent_analysis", "job_search_guidance"],
        )

    async def _handle_resume_query(self, message: str) -> AgentResponse:
        """Handle resume-related queries."""
        from app.infra.db.repositories.resume import SQLResumeRepository

        resume_repo = SQLResumeRepository(session=self._db)

        # Try primary resume first, fall back to any resume
        resume = await resume_repo.get_primary(user_id=self._user_id)
        if not resume:
            all_resumes = await resume_repo.get_by_user_id(self._user_id)
            resume = all_resumes[0] if all_resumes else None

        # State 1: Resume with parsed data - show analysis
        if resume and resume.parsed_data:
            parsed = resume.parsed_data
            skills = parsed.skills[:15] if parsed.skills else []
            experience_count = len(parsed.work_experience)
            education_count = len(parsed.education)
            years_exp = parsed.total_years_experience

            # Build skills analysis response
            skills_text = ", ".join(skills) if skills else "No skills extracted yet"
            years_text = f"{years_exp:.1f} years" if years_exp else "Not calculated"

            content = (
                f"📋 **Your Resume Analysis**\n\n"
                f"**Name:** {parsed.full_name or 'Not extracted'}\n"
                f"**Location:** {parsed.location or 'Not specified'}\n\n"
                f"**Skills ({len(parsed.skills)} total):**\n{skills_text}\n\n"
                f"**Experience:** {experience_count} positions ({years_text})\n"
                f"**Education:** {education_count} entries\n"
                f"**Certifications:** {len(parsed.certifications)}\n\n"
                "I can help you:\n"
                "• Match your profile to specific jobs\n"
                "• Suggest skills to highlight for a role\n"
                "• Generate tailored cover letters\n\n"
                "Would you like me to find jobs that match your skills?"
            )

            return AgentResponse(
                content=content,
                session_id=self._session_id or "",
                agents_involved=["Orchestrator", "ResumeAgent"],
                actions_taken=["intent_analysis", "resume_analysis", "skills_extraction"],
            )

        # State 2: Resume exists but parsing failed
        if resume:
            return AgentResponse(
                content=(
                    f"I found your resume **{resume.filename}**, but I couldn't extract "
                    "its contents properly.\n\n"
                    "This can happen with:\n"
                    "• Scanned/image-based PDFs\n"
                    "• Protected or encrypted documents\n"
                    "• Unusual formatting\n\n"
                    "**To fix this:**\n"
                    "1. Go to the Profile section\n"
                    "2. Delete the current resume\n"
                    "3. Upload a text-based PDF or DOCX file\n\n"
                    "Once re-uploaded, I'll be able to analyze your skills and help you "
                    "find matching jobs!"
                ),
                session_id=self._session_id or "",
                agents_involved=["Orchestrator", "ResumeAgent"],
                actions_taken=["intent_analysis", "resume_parsing_failed"],
            )

        # State 3: No resume uploaded yet
        return AgentResponse(
            content=(
                "I can help optimize your resume! Here's how:\n\n"
                "1. Upload your resume in the Profile section\n"
                "2. I'll parse and extract your skills\n"
                "3. For any job, I can show how well you match\n"
                "4. I'll suggest improvements without fabricating\n\n"
                "Please upload your resume first to get started!"
            ),
            session_id=self._session_id or "",
            agents_involved=["Orchestrator", "ResumeAgent"],
            actions_taken=["intent_analysis", "resume_guidance"],
        )

    async def _handle_apply_query(self, message: str) -> AgentResponse:
        """Handle application queries."""
        return AgentResponse(
            content=(
                "I can help you apply to jobs! Here's the process:\n\n"
                "1. Select a job from your matches\n"
                "2. I'll generate a tailored cover letter\n"
                "3. You review and edit before submitting\n"
                "4. I handle the form filling via automation\n\n"
                "All content is based on YOUR actual experience - "
                "I never fabricate information. Ready to apply?"
            ),
            session_id=self._session_id or "",
            agents_involved=["Orchestrator", "ApplyAgent", "QualityControlAgent"],
            actions_taken=["intent_analysis", "apply_guidance"],
        )

    async def _handle_general_query(self, message: str) -> AgentResponse:
        """Handle general queries."""
        return AgentResponse(
            content=(
                "I'm your AI job application assistant! I can help with:\n\n"
                "• **Finding Jobs** - Discover positions matching your skills\n"
                "• **Resume Analysis** - Understand your strengths\n"
                "• **Applications** - Generate and submit applications\n"
                "• **Tracking** - Monitor your application status\n\n"
                "What would you like to do today?"
            ),
            session_id=self._session_id or "",
            agents_involved=["Orchestrator"],
            actions_taken=["intent_analysis", "general_guidance"],
        )

    def _generate_tailored_summary(self, resume, job) -> str:
        """Generate a tailored summary for the job."""
        # Simplified - would use LLM in production
        skills = ", ".join(resume.skills[:5]) if resume.skills else "your skills"
        return (
            f"With expertise in {skills}, I am well-positioned for this "
            f"{job.title} role at {job.company}."
        )
