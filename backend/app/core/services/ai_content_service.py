"""AI content generation service for resume builder.

Standards: python_clean.mdc
- LLM-powered content generation
- Async operations
- kw-only args
"""

from dataclasses import dataclass, field

import structlog

from app.core.domain.job import Job
from app.core.domain.resume import (
    ResumeContent,
    SkillsSection,
    WorkExperience,
)
from app.core.ports.llm import LLMClient, LLMMessage

logger = structlog.get_logger(__name__)


@dataclass
class SummaryResult:
    """Result of summary generation."""

    content: str
    model_used: str
    tokens_used: int


@dataclass
class BulletEnhanceResult:
    """Result of bullet point enhancement."""

    original: str
    enhanced: str
    improvements: list[str] = field(default_factory=list)


@dataclass
class SkillSuggestionResult:
    """Result of skill suggestions."""

    technical: list[str] = field(default_factory=list)
    soft: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class TailorResult:
    """Result of resume tailoring for a job."""

    content: ResumeContent
    changes_made: list[str]
    keyword_matches: list[str]
    suggestions: list[str]


# System prompts for different tasks
SUMMARY_SYSTEM_PROMPT = """You are an expert resume writer specializing in crafting compelling professional summaries.

Your goal is to create a concise, impactful professional summary that:
- Opens with years of experience and primary expertise area
- Highlights 2-3 key achievements or capabilities
- Mentions relevant technical skills naturally
- Uses action-oriented language
- Is tailored to the target role if provided
- Is 3-5 sentences maximum

IMPORTANT: Only include information that is actually present in the provided experience and skills. Never fabricate or exaggerate."""

BULLET_ENHANCE_PROMPT = """You are an expert resume writer specializing in transforming job descriptions into achievement-focused bullet points.

Guidelines:
1. Start with a strong action verb
2. Quantify results whenever possible (numbers, percentages, dollar amounts)
3. Use the STAR method: Situation, Task, Action, Result
4. Keep each bullet under 2 lines
5. Focus on impact and outcomes, not just responsibilities
6. Use industry-specific keywords naturally

IMPORTANT: Do not add information that wasn't implied in the original. Only enhance the presentation of existing content."""

SKILL_SUGGEST_PROMPT = """You are a career advisor helping identify relevant skills for a specific job title.

Based on the job title and existing skills, suggest additional skills that would strengthen the resume.

Consider:
1. Technical skills commonly required for the role
2. Soft skills valued in similar positions
3. Tools and technologies used in the industry
4. Skills that complement what the candidate already has

Return suggestions in three categories:
- Technical: Hard skills, programming languages, methodologies
- Soft: Interpersonal skills, leadership, communication
- Tools: Software, platforms, frameworks

Only suggest skills that are realistic and commonly expected for the role."""

TAILOR_PROMPT = """You are a resume optimization expert helping tailor resumes for specific job applications.

Analyze the job description and the current resume content. Suggest modifications to:
1. Reorder sections to highlight most relevant experience first
2. Adjust the professional summary to match the role
3. Emphasize bullet points that align with job requirements
4. Suggest which skills to highlight prominently
5. Identify keywords from the job description to incorporate

IMPORTANT: Never add false information. Only reorganize and emphasize existing content."""


class AIContentService:
    """Service for AI-powered resume content generation.

    Uses Together AI LLMs for generating and enhancing resume content.
    """

    def __init__(self, *, llm_client: LLMClient) -> None:
        """Initialize AI content service.

        Args:
            llm_client: LLM client for generation
        """
        self._llm = llm_client

    async def generate_summary(
        self,
        *,
        work_experience: list[WorkExperience],
        skills: SkillsSection,
        target_role: str | None = None,
        years_of_experience: float | None = None,
    ) -> SummaryResult:
        """Generate a professional summary based on experience and skills.

        Args:
            work_experience: List of work experiences
            skills: Skills section with categorized skills
            target_role: Optional target job title to tailor the summary
            years_of_experience: Optional total years of experience

        Returns:
            SummaryResult with generated summary
        """
        # Build context from experience
        experience_text = self._format_experience(work_experience)

        # Combine all skills
        all_skills = skills.technical + skills.soft + skills.tools
        skills_text = ", ".join(all_skills[:20]) if all_skills else "Not specified"

        # Build the user prompt
        user_prompt = f"""Generate a professional summary for the following profile:

WORK EXPERIENCE:
{experience_text}

SKILLS:
{skills_text}

TOTAL YEARS OF EXPERIENCE: {years_of_experience or "Not specified"}
TARGET ROLE: {target_role or "General professional position"}

Write a compelling 3-5 sentence professional summary:"""

        messages = [
            LLMMessage(role="system", content=SUMMARY_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

        from app.agents.config import Models

        response = await self._llm.complete(
            messages=messages,
            model=Models.QWEN3_235B,  # Best for document understanding
            temperature=0.6,
            max_tokens=500,
        )

        logger.info(
            "summary_generated",
            target_role=target_role,
            tokens_used=response.usage.get("total_tokens", 0),
        )

        return SummaryResult(
            content=response.content.strip(),
            model_used=response.model,
            tokens_used=response.usage.get("total_tokens", 0),
        )

    async def enhance_bullet_point(
        self,
        *,
        original: str,
        job_title: str | None = None,
        company: str | None = None,
    ) -> BulletEnhanceResult:
        """Enhance a single bullet point to be more impactful.

        Args:
            original: Original bullet point text
            job_title: Optional job title for context
            company: Optional company name for context

        Returns:
            BulletEnhanceResult with enhanced bullet point
        """
        context = ""
        if job_title:
            context += f"Job Title: {job_title}\n"
        if company:
            context += f"Company: {company}\n"

        user_prompt = f"""Enhance this resume bullet point to be more impactful:

{context}
Original bullet point: {original}

Return the enhanced bullet point. Keep it concise (under 2 lines).
Also list 2-3 specific improvements you made.

Format your response as:
ENHANCED: [your enhanced bullet point]
IMPROVEMENTS:
- [improvement 1]
- [improvement 2]
- [improvement 3]"""

        messages = [
            LLMMessage(role="system", content=BULLET_ENHANCE_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

        from app.agents.config import Models

        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA3_70B,
            temperature=0.5,
            max_tokens=300,
        )

        # Parse the response
        result_text = response.content.strip()
        enhanced = original  # Fallback to original
        improvements: list[str] = []

        if "ENHANCED:" in result_text:
            parts = result_text.split("IMPROVEMENTS:")
            enhanced_part = parts[0].replace("ENHANCED:", "").strip()
            enhanced = enhanced_part

            if len(parts) > 1:
                improvements_text = parts[1].strip()
                improvements = [
                    line.strip().lstrip("-").strip()
                    for line in improvements_text.split("\n")
                    if line.strip() and line.strip() != "-"
                ]

        logger.info(
            "bullet_enhanced",
            original_length=len(original),
            enhanced_length=len(enhanced),
            improvements_count=len(improvements),
        )

        return BulletEnhanceResult(
            original=original,
            enhanced=enhanced,
            improvements=improvements[:3],
        )

    async def suggest_skills(
        self,
        *,
        job_title: str,
        existing_skills: SkillsSection,
        industry: str | None = None,
    ) -> SkillSuggestionResult:
        """Suggest additional skills based on job title.

        Args:
            job_title: Target job title
            existing_skills: Current skills in the resume
            industry: Optional industry context

        Returns:
            SkillSuggestionResult with skill suggestions
        """
        existing_all = (
            existing_skills.technical + existing_skills.soft + existing_skills.tools
        )
        existing_text = ", ".join(existing_all) if existing_all else "None listed"

        user_prompt = f"""Suggest skills for the following profile:

TARGET ROLE: {job_title}
INDUSTRY: {industry or "Not specified"}
EXISTING SKILLS: {existing_text}

Suggest skills that would strengthen this candidate's resume for the target role.
Return skills in three categories (5-7 per category).

Format your response as:
TECHNICAL:
- skill1
- skill2
...

SOFT:
- skill1
- skill2
...

TOOLS:
- tool1
- tool2
...

REASONING: [Brief explanation of why these skills are relevant]"""

        messages = [
            LLMMessage(role="system", content=SKILL_SUGGEST_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

        from app.agents.config import Models

        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA4_MAVERICK,  # Good for analysis
            temperature=0.4,
            max_tokens=600,
        )

        # Parse the response
        result_text = response.content.strip()
        technical: list[str] = []
        soft: list[str] = []
        tools: list[str] = []
        reasoning = ""

        current_section = None
        for line in result_text.split("\n"):
            line = line.strip()
            if line.startswith("TECHNICAL:"):
                current_section = "technical"
            elif line.startswith("SOFT:"):
                current_section = "soft"
            elif line.startswith("TOOLS:"):
                current_section = "tools"
            elif line.startswith("REASONING:"):
                current_section = "reasoning"
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("-") and current_section:
                skill = line.lstrip("-").strip()
                if skill and current_section == "technical":
                    technical.append(skill)
                elif skill and current_section == "soft":
                    soft.append(skill)
                elif skill and current_section == "tools":
                    tools.append(skill)
            elif current_section == "reasoning" and line:
                reasoning += " " + line

        # Filter out skills that already exist
        existing_lower = {s.lower() for s in existing_all}
        technical = [s for s in technical if s.lower() not in existing_lower][:7]
        soft = [s for s in soft if s.lower() not in existing_lower][:7]
        tools = [s for s in tools if s.lower() not in existing_lower][:7]

        logger.info(
            "skills_suggested",
            job_title=job_title,
            technical_count=len(technical),
            soft_count=len(soft),
            tools_count=len(tools),
        )

        return SkillSuggestionResult(
            technical=technical,
            soft=soft,
            tools=tools,
            reasoning=reasoning.strip(),
        )

    async def tailor_for_job(
        self,
        *,
        content: ResumeContent,
        job: Job,
    ) -> TailorResult:
        """Tailor resume content for a specific job.

        Args:
            content: Current resume content
            job: Target job to tailor for

        Returns:
            TailorResult with tailored content and suggestions
        """
        # Format current resume for the prompt
        resume_text = self._format_resume_content(content)

        user_prompt = f"""Analyze this resume and job description. Suggest how to tailor the resume.

JOB DESCRIPTION:
Title: {job.title}
Company: {job.company}
Description: {job.description[:3000] if job.description else "Not available"}

CURRENT RESUME:
{resume_text}

Analyze and provide:
1. KEYWORD_MATCHES: List keywords from the job description that are already in the resume
2. SUMMARY_SUGGESTION: A tailored professional summary
3. SECTION_ORDER: Recommended section order to highlight relevant experience
4. BULLET_SUGGESTIONS: 2-3 existing bullet points that should be emphasized
5. SKILLS_TO_HIGHLIGHT: Skills from the resume that match job requirements
6. ADDITIONAL_SUGGESTIONS: Other improvements

Format your response with clear section headers."""

        messages = [
            LLMMessage(role="system", content=TAILOR_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

        from app.agents.config import Models

        response = await self._llm.complete(
            messages=messages,
            model=Models.QWEN3_235B,
            temperature=0.4,
            max_tokens=1500,
        )

        # Parse the response
        result_text = response.content.strip()

        # Extract sections from response
        keyword_matches = self._extract_list_section(result_text, "KEYWORD_MATCHES")
        summary_suggestion = self._extract_text_section(result_text, "SUMMARY_SUGGESTION")
        suggestions = self._extract_list_section(result_text, "ADDITIONAL_SUGGESTIONS")

        # Create tailored content (copy and modify)
        tailored_content = ResumeContent(
            full_name=content.full_name,
            email=content.email,
            phone=content.phone,
            location=content.location,
            linkedin_url=content.linkedin_url,
            portfolio_url=content.portfolio_url,
            github_url=content.github_url,
            professional_summary=summary_suggestion or content.professional_summary,
            work_experience=content.work_experience.copy(),
            education=content.education.copy(),
            skills=content.skills,
            projects=content.projects.copy(),
            certifications=content.certifications.copy(),
            awards=content.awards.copy(),
            languages=content.languages.copy(),
            custom_sections=content.custom_sections.copy(),
            template_id=content.template_id,
            section_order=content.section_order.copy(),
            ats_score=content.ats_score,
        )

        changes_made = []
        if summary_suggestion and summary_suggestion != content.professional_summary:
            changes_made.append("Updated professional summary to match job requirements")

        logger.info(
            "resume_tailored",
            job_title=job.title,
            keyword_matches_count=len(keyword_matches),
            changes_count=len(changes_made),
        )

        return TailorResult(
            content=tailored_content,
            changes_made=changes_made,
            keyword_matches=keyword_matches,
            suggestions=suggestions,
        )

    def _format_experience(self, work_experience: list[WorkExperience]) -> str:
        """Format work experience for prompts."""
        if not work_experience:
            return "No work experience listed"

        lines = []
        for exp in work_experience[:5]:
            line = f"- {exp.title} at {exp.company}"
            if exp.start_date:
                line += f" ({exp.start_date}"
                if exp.end_date:
                    line += f" - {exp.end_date}"
                elif exp.is_current:
                    line += " - Present"
                line += ")"
            lines.append(line)

            if exp.achievements:
                for ach in exp.achievements[:3]:
                    lines.append(f"  • {ach}")

        return "\n".join(lines)

    def _format_resume_content(self, content: ResumeContent) -> str:
        """Format full resume content for prompts."""
        sections = []

        sections.append(f"Name: {content.full_name}")
        if content.professional_summary:
            sections.append(f"\nSummary: {content.professional_summary}")

        if content.work_experience:
            sections.append("\nExperience:")
            sections.append(self._format_experience(content.work_experience))

        if content.education:
            sections.append("\nEducation:")
            for edu in content.education[:3]:
                sections.append(f"- {edu.degree} in {edu.field_of_study or 'N/A'} from {edu.institution}")

        all_skills = content.skills.technical + content.skills.soft + content.skills.tools
        if all_skills:
            sections.append(f"\nSkills: {', '.join(all_skills[:20])}")

        return "\n".join(sections)

    def _extract_list_section(self, text: str, section_name: str) -> list[str]:
        """Extract a list from a section in the response."""
        items: list[str] = []
        in_section = False

        for line in text.split("\n"):
            if section_name.upper() in line.upper():
                in_section = True
                continue
            elif in_section:
                if line.strip().startswith("-") or line.strip().startswith("•"):
                    item = line.strip().lstrip("-•").strip()
                    if item:
                        items.append(item)
                elif line.strip() and not line.strip().startswith("-"):
                    # Check if we hit a new section
                    if any(header in line.upper() for header in ["SUMMARY", "SECTION", "BULLET", "SKILLS", "ADDITIONAL"]):
                        break

        return items[:10]

    def _extract_text_section(self, text: str, section_name: str) -> str | None:
        """Extract text from a section in the response."""
        lines = []
        in_section = False

        for line in text.split("\n"):
            if section_name.upper() in line.upper():
                in_section = True
                # Check if content is on the same line
                after_colon = line.split(":", 1)
                if len(after_colon) > 1 and after_colon[1].strip():
                    lines.append(after_colon[1].strip())
                continue
            elif in_section:
                if line.strip() and not any(
                    header in line.upper()
                    for header in ["KEYWORD", "SECTION_ORDER", "BULLET", "SKILLS_TO", "ADDITIONAL"]
                ):
                    lines.append(line.strip())
                else:
                    break

        return " ".join(lines).strip() if lines else None
