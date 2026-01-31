"""SendGrid email notification service.

Standards: python_clean.mdc
- Async HTTP client
- Template-based emails
- Proper error handling
"""

from dataclasses import dataclass
from datetime import datetime

import httpx
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class EmailMessage:
    """Email message configuration."""

    to: str
    subject: str
    html_content: str
    text_content: str | None = None


class EmailError(Exception):
    """Email sending error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EmailService:
    """SendGrid email notification service.

    Sends transactional emails for application events.
    """

    SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(
        self,
        *,
        api_key: str,
        from_email: str,
        from_name: str = "ApplyBots",
    ) -> None:
        """Initialize email service.

        Args:
            api_key: SendGrid API key
            from_email: Sender email address
            from_name: Sender display name
        """
        self._api_key = api_key
        self._from_email = from_email
        self._from_name = from_name

    async def send(self, message: EmailMessage) -> bool:
        """Send an email message.

        Args:
            message: Email message to send

        Returns:
            True if sent successfully

        Raises:
            EmailError: If sending fails
        """
        payload = {
            "personalizations": [{"to": [{"email": message.to}]}],
            "from": {"email": self._from_email, "name": self._from_name},
            "subject": message.subject,
            "content": [{"type": "text/html", "value": message.html_content}],
        }

        if message.text_content:
            payload["content"].insert(
                0, {"type": "text/plain", "value": message.text_content}
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.SENDGRID_API_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code not in (200, 202):
                logger.error(
                    "email_send_failed",
                    to=message.to,
                    subject=message.subject,
                    status_code=response.status_code,
                )
                raise EmailError(
                    f"Failed to send email: {response.text}",
                    status_code=response.status_code,
                )

        logger.info(
            "email_sent",
            to=message.to,
            subject=message.subject,
        )

        return True

    async def send_application_submitted(
        self,
        *,
        to: str,
        job_title: str,
        company: str,
        application_id: str,
    ) -> bool:
        """Send application submitted notification.

        Args:
            to: Recipient email
            job_title: Job title applied for
            company: Company name
            application_id: Application ID for tracking

        Returns:
            True if sent successfully
        """
        subject = f"Application Submitted: {job_title} at {company}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #4F46E5; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">ApplyBots</h1>
            </div>
            <div style="padding: 30px;">
                <h2>Application Submitted! 🎉</h2>
                <p>Great news! Your application has been successfully submitted.</p>
                
                <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Position:</strong> {job_title}</p>
                    <p style="margin: 10px 0 0;"><strong>Company:</strong> {company}</p>
                </div>
                
                <p>What happens next?</p>
                <ul>
                    <li>The hiring team will review your application</li>
                    <li>You'll receive updates on any status changes</li>
                    <li>Track all your applications in your dashboard</li>
                </ul>
                
                <a href="https://applybots.ai/dashboard/applications" 
                   style="display: inline-block; background: #4F46E5; color: white; 
                          padding: 12px 24px; text-decoration: none; border-radius: 6px;
                          margin-top: 20px;">
                    View Application Status
                </a>
                
                <p style="color: #6B7280; margin-top: 30px; font-size: 12px;">
                    Application ID: {application_id}
                </p>
            </div>
            <div style="background: #F9FAFB; padding: 20px; text-align: center; color: #6B7280;">
                <p style="margin: 0;">© 2026 ApplyBots. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
Application Submitted!

Your application for {job_title} at {company} has been successfully submitted.

What happens next?
- The hiring team will review your application
- You'll receive updates on any status changes
- Track all your applications in your dashboard

View your application: https://applybots.ai/dashboard/applications

Application ID: {application_id}
        """

        return await self.send(
            EmailMessage(
                to=to,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
        )

    async def send_interview_scheduled(
        self,
        *,
        to: str,
        job_title: str,
        company: str,
        interview_date: datetime,
        interview_type: str = "Interview",
    ) -> bool:
        """Send interview scheduled notification.

        Args:
            to: Recipient email
            job_title: Job title
            company: Company name
            interview_date: Date and time of interview
            interview_type: Type of interview (Phone, Video, Onsite)

        Returns:
            True if sent successfully
        """
        date_str = interview_date.strftime("%A, %B %d, %Y at %I:%M %p")
        subject = f"🎉 Interview Scheduled: {job_title} at {company}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #059669; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">Congratulations! 🎉</h1>
            </div>
            <div style="padding: 30px;">
                <h2>Interview Scheduled!</h2>
                <p>You've been selected for an interview! Here are the details:</p>
                
                <div style="background: #ECFDF5; padding: 20px; border-radius: 8px; margin: 20px 0;
                            border-left: 4px solid #059669;">
                    <p style="margin: 0;"><strong>Position:</strong> {job_title}</p>
                    <p style="margin: 10px 0;"><strong>Company:</strong> {company}</p>
                    <p style="margin: 10px 0;"><strong>Type:</strong> {interview_type}</p>
                    <p style="margin: 10px 0 0;"><strong>Date:</strong> {date_str}</p>
                </div>
                
                <h3>Preparation Tips:</h3>
                <ul>
                    <li>Research the company and role thoroughly</li>
                    <li>Prepare examples of your past achievements</li>
                    <li>Test your equipment if it's a video interview</li>
                    <li>Prepare questions to ask the interviewer</li>
                </ul>
                
                <p>Good luck! 🍀</p>
            </div>
            <div style="background: #F9FAFB; padding: 20px; text-align: center; color: #6B7280;">
                <p style="margin: 0;">© 2026 ApplyBots. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return await self.send(
            EmailMessage(
                to=to,
                subject=subject,
                html_content=html_content,
            )
        )

    async def send_daily_summary(
        self,
        *,
        to: str,
        date: datetime,
        applications_submitted: int,
        interviews_scheduled: int,
        new_matches: int,
    ) -> bool:
        """Send daily activity summary.

        Args:
            to: Recipient email
            date: Summary date
            applications_submitted: Number of applications submitted
            interviews_scheduled: Number of interviews scheduled
            new_matches: Number of new job matches

        Returns:
            True if sent successfully
        """
        date_str = date.strftime("%B %d, %Y")
        subject = f"📊 Your Daily Summary - {date_str}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #4F46E5; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">Daily Summary</h1>
                <p style="margin: 5px 0 0;">{date_str}</p>
            </div>
            <div style="padding: 30px;">
                <h2>Your Activity Overview</h2>
                
                <div style="display: flex; gap: 20px; margin: 20px 0;">
                    <div style="flex: 1; background: #EEF2FF; padding: 20px; border-radius: 8px; text-align: center;">
                        <p style="margin: 0; font-size: 32px; font-weight: bold; color: #4F46E5;">
                            {applications_submitted}
                        </p>
                        <p style="margin: 5px 0 0; color: #6B7280;">Applications Submitted</p>
                    </div>
                    <div style="flex: 1; background: #ECFDF5; padding: 20px; border-radius: 8px; text-align: center;">
                        <p style="margin: 0; font-size: 32px; font-weight: bold; color: #059669;">
                            {interviews_scheduled}
                        </p>
                        <p style="margin: 5px 0 0; color: #6B7280;">Interviews Scheduled</p>
                    </div>
                    <div style="flex: 1; background: #FEF3C7; padding: 20px; border-radius: 8px; text-align: center;">
                        <p style="margin: 0; font-size: 32px; font-weight: bold; color: #D97706;">
                            {new_matches}
                        </p>
                        <p style="margin: 5px 0 0; color: #6B7280;">New Matches</p>
                    </div>
                </div>
                
                <a href="https://applybots.ai/dashboard" 
                   style="display: inline-block; background: #4F46E5; color: white; 
                          padding: 12px 24px; text-decoration: none; border-radius: 6px;
                          margin-top: 20px;">
                    Go to Dashboard
                </a>
            </div>
            <div style="background: #F9FAFB; padding: 20px; text-align: center; color: #6B7280;">
                <p style="margin: 0;">© 2026 ApplyBots. All rights reserved.</p>
                <p style="margin: 10px 0 0;">
                    <a href="#" style="color: #6B7280;">Unsubscribe</a>
                </p>
            </div>
        </body>
        </html>
        """

        return await self.send(
            EmailMessage(
                to=to,
                subject=subject,
                html_content=html_content,
            )
        )

    async def send_application_status_update(
        self,
        *,
        to: str,
        job_title: str,
        company: str,
        old_status: str,
        new_status: str,
    ) -> bool:
        """Send application status update notification.

        Args:
            to: Recipient email
            job_title: Job title
            company: Company name
            old_status: Previous status
            new_status: New status

        Returns:
            True if sent successfully
        """
        # Determine emoji based on status
        status_emoji = {
            "interview": "🎉",
            "offer": "🎊",
            "rejected": "😔",
            "submitted": "📨",
        }.get(new_status.lower(), "📋")

        subject = f"{status_emoji} Application Update: {job_title} at {company}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #4F46E5; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">Application Update</h1>
            </div>
            <div style="padding: 30px;">
                <h2>Status Changed</h2>
                
                <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Position:</strong> {job_title}</p>
                    <p style="margin: 10px 0 0;"><strong>Company:</strong> {company}</p>
                </div>
                
                <p>Your application status has been updated:</p>
                
                <div style="display: flex; align-items: center; gap: 10px; margin: 20px 0;">
                    <span style="background: #E5E7EB; padding: 8px 16px; border-radius: 20px;">
                        {old_status}
                    </span>
                    <span>→</span>
                    <span style="background: #4F46E5; color: white; padding: 8px 16px; border-radius: 20px;">
                        {new_status}
                    </span>
                </div>
                
                <a href="https://applybots.ai/dashboard/applications" 
                   style="display: inline-block; background: #4F46E5; color: white; 
                          padding: 12px 24px; text-decoration: none; border-radius: 6px;
                          margin-top: 20px;">
                    View Details
                </a>
            </div>
            <div style="background: #F9FAFB; padding: 20px; text-align: center; color: #6B7280;">
                <p style="margin: 0;">© 2026 ApplyBots. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return await self.send(
            EmailMessage(
                to=to,
                subject=subject,
                html_content=html_content,
            )
        )
