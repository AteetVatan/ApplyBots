"""Recruiter outreach automation service.

Standards: python_clean.mdc
- Async operations
- Ethical automation only
- No LinkedIn scraping
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import structlog

from app.core.domain.job import Job
from app.core.domain.resume import ParsedResume
from app.core.ports.llm import LLMClient, LLMMessage

logger = structlog.get_logger(__name__)


@dataclass
class RecruiterContact:
    """Recruiter contact information."""

    name: str
    email: str | None
    company: str
    title: str
    source: str  # Where the contact was found


@dataclass
class FollowUpMessage:
    """Generated follow-up message."""

    subject: str
    body: str
    tone: str
    generated_at: datetime


class RecruiterOutreachService:
    """Service for automated recruiter follow-up.

    Generates personalized follow-up messages after application submission.
    Does NOT scrape LinkedIn or violate any platform ToS.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
    ) -> None:
        """Initialize outreach service.

        Args:
            llm_client: LLM client for message generation
        """
        self._llm = llm_client

    async def generate_followup_message(
        self,
        *,
        job: Job,
        resume: ParsedResume,
        application_date: datetime,
        tone: str = "professional",
    ) -> FollowUpMessage:
        """Generate a personalized follow-up message.

        Args:
            job: The job that was applied to
            resume: Candidate's parsed resume
            application_date: When the application was submitted
            tone: Message tone (professional, enthusiastic, concise)

        Returns:
            Generated follow-up message
        """
        days_since_application = (datetime.utcnow() - application_date).days

        prompt = f"""Generate a professional follow-up email for a job application.

JOB DETAILS:
- Position: {job.title}
- Company: {job.company}
- Applied: {days_since_application} days ago

CANDIDATE:
- Name: {resume.full_name or 'Candidate'}
- Top Skills: {', '.join(resume.skills[:5]) if resume.skills else 'N/A'}
- Years Experience: {resume.total_years_experience or 'N/A'}

REQUIREMENTS:
1. Write a {tone} follow-up email
2. Be brief (under 150 words)
3. Express continued interest
4. Highlight one relevant qualification
5. Request a brief conversation or update
6. Do NOT be pushy or demanding

Generate the email subject and body:

Subject: [subject line]

Body:
[email body]"""

        messages = [LLMMessage(role="user", content=prompt)]

        from app.agents.config import Models
        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA3_70B,
            temperature=0.7,
            max_tokens=500,
        )

        # Parse response
        content = response.content.strip()
        subject, body = self._parse_email_response(content)

        logger.info(
            "followup_message_generated",
            job_id=job.id,
            company=job.company,
            days_since=days_since_application,
        )

        return FollowUpMessage(
            subject=subject,
            body=body,
            tone=tone,
            generated_at=datetime.utcnow(),
        )

    def _parse_email_response(self, content: str) -> tuple[str, str]:
        """Parse LLM response into subject and body."""
        lines = content.split("\n")
        subject = ""
        body_lines = []
        in_body = False

        for line in lines:
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            elif line.lower().startswith("body:"):
                in_body = True
            elif in_body:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # Fallback parsing if format didn't match
        if not subject:
            subject = "Following up on my application"
        if not body:
            body = content

        return subject, body

    def get_recommended_followup_timing(
        self,
        *,
        application_date: datetime,
    ) -> datetime | None:
        """Get recommended time for follow-up.

        Args:
            application_date: When the application was submitted

        Returns:
            Recommended follow-up date, or None if too soon
        """
        days_since = (datetime.utcnow() - application_date).days

        # Timing recommendations:
        # - Wait at least 5 business days before first follow-up
        # - Second follow-up after 10 business days
        # - Don't follow up more than twice

        if days_since < 5:
            # Too soon - wait
            return application_date + timedelta(days=7)
        elif days_since < 14:
            # Good time for first follow-up
            return datetime.utcnow()
        elif days_since < 21:
            # Time for second follow-up
            return datetime.utcnow()
        else:
            # Too late for automated follow-up
            return None

    async def schedule_followup(
        self,
        *,
        application_id: str,
        followup_date: datetime,
    ) -> str:
        """Schedule a follow-up task.

        Args:
            application_id: Application to follow up on
            followup_date: When to send the follow-up

        Returns:
            Task ID for the scheduled follow-up
        """
        from app.workers.celery_app import celery_app

        # Schedule the task
        task = celery_app.send_task(
            "app.workers.recruiter_followup.send_followup",
            args=[application_id],
            eta=followup_date,
        )

        logger.info(
            "followup_scheduled",
            application_id=application_id,
            scheduled_for=followup_date.isoformat(),
            task_id=task.id,
        )

        return task.id
