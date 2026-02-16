"""Agent workflow orchestration using AutoGen GroupChat.

Standards: python_clean.mdc
- Async operations
- Proper error handling
- Multi-agent coordination
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
    """Orchestrates multi-agent job application workflow using AutoGen GroupChat."""

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
        self._group_chat = None
        self._manager = None
        self._agents: dict = {}

    def _setup_agents(self) -> None:
        """Initialize AutoGen agents and GroupChat."""
        try:
            from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent
        except ImportError:
            logger.warning("autogen_not_installed", fallback="using_simple_workflow")
            return

        try:
            from app.agents.config import (
                LLM_CONFIG_APPLY,
                LLM_CONFIG_CRITIC,
                LLM_CONFIG_MATCHER,
                LLM_CONFIG_ORCHESTRATOR,
                LLM_CONFIG_QC,
                LLM_CONFIG_RESUME,
                LLM_CONFIG_SCRAPER,
            )
            from app.agents.prompts import (
                APPLY_AGENT_PROMPT,
                CRITIC_AGENT_PROMPT,
                JOB_SCRAPER_PROMPT,
                MATCH_AGENT_PROMPT,
                ORCHESTRATOR_SYSTEM_PROMPT,
                QC_AGENT_PROMPT,
                RESUME_AGENT_PROMPT,
            )
        except Exception as e:
            logger.warning("agent_config_unavailable", error=str(e), fallback="using_simple_workflow")
            return


        # Create UserProxy for human-in-the-loop
        self._agents["user_proxy"] = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",  # Automated mode
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )

        # Create specialized agents
        self._agents["orchestrator"] = AssistantAgent(
            name="Orchestrator",
            system_message=ORCHESTRATOR_SYSTEM_PROMPT,
            llm_config=LLM_CONFIG_ORCHESTRATOR,
        )

        self._agents["resume_agent"] = AssistantAgent(
            name="ResumeAgent",
            system_message=RESUME_AGENT_PROMPT,
            llm_config=LLM_CONFIG_RESUME,
        )

        self._agents["job_scraper"] = AssistantAgent(
            name="JobScraperAgent",
            system_message=JOB_SCRAPER_PROMPT,
            llm_config=LLM_CONFIG_SCRAPER,
        )

        self._agents["match_agent"] = AssistantAgent(
            name="MatchAgent",
            system_message=MATCH_AGENT_PROMPT,
            llm_config=LLM_CONFIG_MATCHER,
        )

        self._agents["apply_agent"] = AssistantAgent(
            name="ApplyAgent",
            system_message=APPLY_AGENT_PROMPT,
            llm_config=LLM_CONFIG_APPLY,
        )

        self._agents["qc_agent"] = AssistantAgent(
            name="QualityControlAgent",
            system_message=QC_AGENT_PROMPT,
            llm_config=LLM_CONFIG_QC,
        )

        self._agents["critic_agent"] = AssistantAgent(
            name="CriticAgent",
            system_message=CRITIC_AGENT_PROMPT,
            llm_config=LLM_CONFIG_CRITIC,
        )

        # Create GroupChat for agent coordination
        self._group_chat = GroupChat(
            agents=[
                self._agents["user_proxy"],
                self._agents["orchestrator"],
                self._agents["resume_agent"],
                self._agents["job_scraper"],
                self._agents["match_agent"],
                self._agents["apply_agent"],
                self._agents["qc_agent"],
                self._agents["critic_agent"],
            ],
            messages=[],
            max_round=20,
            speaker_selection_method="auto",  # Let LLM select next speaker
        )

        # Create GroupChatManager
        self._manager = GroupChatManager(
            groupchat=self._group_chat,
            llm_config=LLM_CONFIG_ORCHESTRATOR,
        )

        # Register tools for agents
        from app.agents.tools import register_agent_tools
        register_agent_tools(self._agents, self._agents["user_proxy"])

        logger.info(
            "autogen_agents_initialized",
            agent_count=len(self._agents),
            user_id=self._user_id,
        )

    async def process_message(
        self,
        message: str,
        session_id: str | None = None,
    ) -> AgentResponse:
        """Process a user message through the AutoGen GroupChat system.

        The Orchestrator coordinates other agents to fulfill the request.
        """
        import uuid

        self._session_id = session_id or str(uuid.uuid4())

        # Early check: If resume-related request but no resume uploaded
        if self._requires_resume(message) and not await self._has_resume():
            return AgentResponse(
                content=(
                    "I'd love to help with your resume, but you haven't uploaded one yet!\n\n"
                    "Please go to the **Profile** tab and upload your resume first. "
                    "Once uploaded, I can:\n"
                    "- Analyze your skills and experience\n"
                    "- Match you with relevant jobs\n"
                    "- Suggest improvements for specific positions\n\n"
                    "Head to Profile → Resume section to get started!"
                ),
                session_id=self._session_id,
                agents_involved=["Orchestrator"],
                actions_taken=["resume_check", "upload_required"],
            )

        # Initialize agents if not done
        if not self._agents:
            self._setup_agents()

        # If AutoGen is available, try it first with fallback
        if self._manager and "user_proxy" in self._agents:
            try:
                return await self._process_with_autogen(message)
            except Exception as e:
                logger.warning(
                    "autogen_chat_failed",
                    error=str(e),
                    user_id=self._user_id,
                    fallback="simple_workflow",
                )

        # Fallback to simple keyword-based workflow
        return await self._process_simple(message)



    async def _process_with_autogen(self, message: str) -> AgentResponse:
        """Process message using AutoGen GroupChat.

        The agents collaborate through the GroupChat to handle the request.
        """
        import asyncio

        # Build context with user's resume data
        context = await self._build_user_context()

        # Construct the full prompt with context
        full_message = f"""User Request: {message}

User Context:
{context}

Please coordinate the appropriate agents to fulfill this request.
Ensure all responses are based on the user's actual resume data."""

        # Run the group chat in a thread to not block async
        def run_chat():
            chat_result = self._agents["user_proxy"].initiate_chat(
                self._manager,
                message=full_message,
                clear_history=False,
            )
            return chat_result

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_chat)

        # Extract the final response and agents involved
        agents_involved = self._extract_agents_from_chat()
        final_content = self._extract_final_response(result)

        logger.info(
            "autogen_chat_complete",
            session_id=self._session_id,
            agents_involved=agents_involved,
            message_count=len(self._group_chat.messages) if self._group_chat else 0,
        )

        return AgentResponse(
            content=final_content,
            session_id=self._session_id or "",
            agents_involved=agents_involved,
            actions_taken=self._extract_actions_from_chat(),
        )

    def _extract_agents_from_chat(self) -> list[str]:
        """Extract list of agents that participated in the chat."""
        if not self._group_chat or not self._group_chat.messages:
            return ["Orchestrator"]

        agents = set()
        for msg in self._group_chat.messages:
            if "name" in msg:
                agents.add(msg["name"])

        return list(agents) or ["Orchestrator"]

    def _extract_final_response(self, chat_result) -> str:
        """Extract the final response from the chat result."""
        if self._group_chat and self._group_chat.messages:
            # Get last assistant message (not from UserProxy)
            for msg in reversed(self._group_chat.messages):
                if msg.get("role") == "assistant" and msg.get("name") != "UserProxy":
                    return msg.get("content", "")

        # Fallback
        if hasattr(chat_result, "chat_history") and chat_result.chat_history:
            return chat_result.chat_history[-1].get("content", "")

        return "I've processed your request. Please check the results."

    def _extract_actions_from_chat(self) -> list[str]:
        """Extract actions taken from the chat messages."""
        actions = ["message_received", "context_loaded"]

        if not self._group_chat or not self._group_chat.messages:
            return actions

        for msg in self._group_chat.messages:
            name = msg.get("name", "")
            content = msg.get("content", "").lower()

            if "ResumeAgent" in name:
                actions.append("resume_analysis")
            if "JobScraperAgent" in name:
                actions.append("job_search")
            if "MatchAgent" in name:
                actions.append("match_scoring")
            if "ApplyAgent" in name:
                actions.append("application_generation")
            if "QualityControlAgent" in name:
                actions.append("quality_review")
            if "CriticAgent" in name:
                actions.append("feedback_generated")

        return list(set(actions))

    async def _build_user_context(self) -> str:
        """Build user context from database for agent reference."""
        from app.infra.db.repositories.resume import SQLResumeRepository

        resume_repo = SQLResumeRepository(session=self._db)

        # Get user's resume
        resume = await resume_repo.get_primary(user_id=self._user_id)
        if not resume:
            resumes = await resume_repo.get_by_user_id(self._user_id)
            resume = resumes[0] if resumes else None

        if not resume or not resume.parsed_data:
            return "No resume uploaded yet."

        parsed = resume.parsed_data

        # Build context string
        context_parts = [
            f"Name: {parsed.full_name or 'Not specified'}",
            f"Email: {parsed.email or 'Not specified'}",
            f"Location: {parsed.location or 'Not specified'}",
        ]

        if parsed.skills:
            context_parts.append(f"Skills: {', '.join(parsed.skills[:20])}")

        if parsed.total_years_experience:
            context_parts.append(f"Total Experience: {parsed.total_years_experience:.1f} years")

        if parsed.work_experience:
            exp_summary = []
            for exp in parsed.work_experience[:3]:
                exp_summary.append(f"  - {exp.title} at {exp.company}")
            context_parts.append("Recent Experience:\n" + "\n".join(exp_summary))

        if parsed.education:
            edu_summary = []
            for edu in parsed.education[:2]:
                edu_summary.append(f"  - {edu.degree} from {edu.institution}")
            context_parts.append("Education:\n" + "\n".join(edu_summary))

        return "\n".join(context_parts)

    async def _process_simple(self, message: str) -> AgentResponse:
        """Simple fallback processing when AutoGen is not available."""
        intent = self._analyze_intent(message)

        if "job" in intent.lower() or "search" in intent.lower():
            return await self._handle_job_search(message)
        elif "resume" in intent.lower() or "optimize" in intent.lower():
            return await self._handle_resume_query(message)
        elif "apply" in intent.lower():
            return await self._handle_apply_query(message)
        else:
            return await self._handle_general_query(message)

    async def stream_process(
        self,
        message: str,
    ) -> AsyncIterator[StreamResponse]:
        """Stream agent responses for real-time updates."""
        import uuid

        self._session_id = str(uuid.uuid4())

        # Early check: If resume-related request but no resume uploaded
        if self._requires_resume(message) and not await self._has_resume():
            yield StreamResponse(
                agent_name="Orchestrator",
                content=(
                    "I'd love to help with your resume, but you haven't uploaded one yet!\n\n"
                    "Please go to the **Profile** tab and upload your resume first. "
                    "Once uploaded, I can:\n"
                    "- Analyze your skills and experience\n"
                    "- Match you with relevant jobs\n"
                    "- Suggest improvements for specific positions\n\n"
                    "Head to Profile → Resume section to get started!"
                ),
                is_final=True,
            )
            return

        # Initialize agents
        if not self._agents:
            self._setup_agents()

        # Yield orchestrator thinking
        yield StreamResponse(
            agent_name="Orchestrator",
            content="Analyzing your request...",
            is_final=False,
        )

        # Build context
        context = await self._build_user_context()
        yield StreamResponse(
            agent_name="Orchestrator",
            content="Loading your profile data...",
            is_final=False,
        )

        # If AutoGen available, stream from agents
        if self._manager and self._group_chat:
            # Track which agents respond
            seen_agents = set()

            # Process through group chat
            response = await self.process_message(message, self._session_id)

            # Yield intermediate agent responses
            for agent_name in response.agents_involved:
                if agent_name != "UserProxy" and agent_name not in seen_agents:
                    seen_agents.add(agent_name)
                    yield StreamResponse(
                        agent_name=agent_name,
                        content=f"{agent_name} processing...",
                        is_final=False,
                    )

            # Yield final response
            yield StreamResponse(
                agent_name="Orchestrator",
                content=response.content,
                is_final=True,
            )
        else:
            # Simple fallback
            response = await self._process_simple(message)
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
        """Optimize resume for a specific job using agent collaboration."""
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

        # If AutoGen is available, use agents for optimization
        if self._manager and "resume_agent" in self._agents:
            suggestions, tailored_summary = await self._get_agent_optimization(
                resume=resume,
                job=job,
                explanation=explanation,
            )
        else:
            # Fallback to simple suggestions
            suggestions = []
            if explanation.skills_missing:
                suggestions.append(
                    f"Consider highlighting these skills if you have them: {', '.join(explanation.skills_missing[:5])}"
                )
            if explanation.experience_gap:
                suggestions.append(f"Experience note: {explanation.experience_gap}")

            tailored_summary = self._generate_tailored_summary(resume.parsed_data, job)

        # Identify skills to highlight
        highlighted_skills = explanation.skills_matched[:10]

        return OptimizationResult(
            original_score=original_score,
            optimized_score=min(100, original_score + len(suggestions) * 3),
            suggestions=suggestions,
            tailored_summary=tailored_summary,
            highlighted_skills=highlighted_skills,
        )

    async def _get_agent_optimization(
        self,
        *,
        resume,
        job,
        explanation,
    ) -> tuple[list[str], str]:
        """Get optimization suggestions from Resume and Critic agents."""
        import asyncio

        # Build optimization prompt
        prompt = f"""Please analyze this resume-job match and provide optimization suggestions.

Job: {job.title} at {job.company}
Job Description: {job.description[:1500]}

Resume Skills: {', '.join(resume.parsed_data.skills[:15])}
Skills Matched: {', '.join(explanation.skills_matched[:10])}
Skills Missing: {', '.join(explanation.skills_missing[:10])}
Match Score: {explanation.skills_score}%

Provide:
1. 3-5 specific suggestions to improve the match (only recommend highlighting skills the candidate actually has)
2. A tailored professional summary (2-3 sentences)

Remember: Only suggest highlighting skills/experience that exist in the resume."""

        def run_optimization():
            # Use resume agent for suggestions
            self._agents["user_proxy"].initiate_chat(
                self._agents["resume_agent"],
                message=prompt,
                max_turns=2,
            )
            return self._agents["resume_agent"].last_message()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_optimization)

        # Parse response
        content = result.get("content", "") if isinstance(result, dict) else str(result)
        suggestions = self._parse_suggestions(content)
        summary = self._parse_summary(content)

        return suggestions, summary

    def _parse_suggestions(self, content: str) -> list[str]:
        """Parse suggestions from agent response."""
        suggestions = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            # Look for numbered suggestions
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                # Clean up the line
                cleaned = line.lstrip("0123456789.-•) ").strip()
                if cleaned and len(cleaned) > 10:
                    suggestions.append(cleaned)

        return suggestions[:5] if suggestions else [
            "Focus your experience section on relevant achievements",
            "Quantify your accomplishments where possible",
            "Tailor your skills section to match the job requirements",
        ]

    def _parse_summary(self, content: str) -> str:
        """Parse tailored summary from agent response."""
        # Look for summary section
        lower_content = content.lower()

        if "summary" in lower_content:
            # Find the summary section
            idx = lower_content.find("summary")
            section = content[idx:idx + 500]
            lines = section.split("\n")[1:4]  # Get lines after "summary"
            summary = " ".join(line.strip() for line in lines if line.strip())
            if summary:
                return summary

        # Fallback
        return ""

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

    def _requires_resume(self, message: str) -> bool:
        """Check if message requires a resume to be uploaded.

        Used for early validation before agent setup.
        """
        message_lower = message.lower()
        resume_keywords = ["resume", "cv", "optimize", "tailor", "improve my"]
        action_keywords = ["analyze", "review", "check", "score", "match"]

        has_resume_keyword = any(kw in message_lower for kw in resume_keywords)
        has_action_keyword = any(kw in message_lower for kw in action_keywords)

        return has_resume_keyword or (has_action_keyword and "resume" in message_lower)

    async def _has_resume(self) -> bool:
        """Check if user has uploaded a resume with parsed data."""
        from app.infra.db.repositories.resume import SQLResumeRepository

        resume_repo = SQLResumeRepository(session=self._db)

        # Check primary resume first
        resume = await resume_repo.get_primary(user_id=self._user_id)
        if resume and resume.parsed_data:
            return True

        # Fall back to any resume with parsed data
        resumes = await resume_repo.get_by_user_id(self._user_id)
        return any(r.parsed_data for r in resumes)

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
            experience_count = len(parsed.work_experience) if parsed.work_experience else 0
            education_count = len(parsed.education) if parsed.education else 0
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
                f"**Certifications:** {len(parsed.certifications) if parsed.certifications else 0}\n\n"
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
        skills = ", ".join(resume.skills[:5]) if resume.skills else "your skills"
        return (
            f"With expertise in {skills}, I am well-positioned for this "
            f"{job.title} role at {job.company}."
        )
