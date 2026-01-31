"""Application timing intelligence service.

Standards: python_clean.mdc
- Data-driven timing recommendations
- Urgency scoring
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import structlog

from app.core.domain.job import ApplicationTiming, Job

logger = structlog.get_logger(__name__)


# Optimal application windows by days since posting
URGENCY_THRESHOLDS = {
    1: {"score": 100, "recommendation": "Apply now - just posted!"},
    2: {"score": 95, "recommendation": "Apply now - very fresh listing"},
    3: {"score": 90, "recommendation": "Apply now - prime window"},
    7: {"score": 80, "recommendation": "Good time to apply"},
    14: {"score": 60, "recommendation": "Still worth applying"},
    21: {"score": 40, "recommendation": "May be late, but try anyway"},
    30: {"score": 20, "recommendation": "Position may be filled"},
}

# Estimated applicants based on days since posting
APPLICANT_ESTIMATES = {
    1: 5,
    2: 15,
    3: 30,
    7: 75,
    14: 150,
    21: 250,
    30: 400,
}


class TimingIntelligenceService:
    """Service for application timing intelligence."""

    def calculate_timing(self, job: Job) -> ApplicationTiming:
        """Calculate optimal application timing for a job.

        Args:
            job: Job to analyze

        Returns:
            ApplicationTiming with recommendations
        """
        now = datetime.utcnow()

        # Calculate days since posting
        if job.posted_at:
            days_since = (now - job.posted_at).days
        else:
            # Assume 7 days if no posted_at
            days_since = 7

        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(days_since)

        # Get recommendation
        recommendation = self._get_recommendation(days_since)

        # Estimate applicants
        estimated_applicants = self._estimate_applicants(days_since)

        # Calculate optimal window
        # Best time: early morning (9 AM) or early afternoon (1-2 PM)
        optimal_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now.hour >= 9:
            optimal_start += timedelta(days=1)

        optimal_end = optimal_start.replace(hour=14)

        logger.debug(
            "timing_calculated",
            job_id=job.id,
            days_since_posted=days_since,
            urgency_score=urgency_score,
        )

        return ApplicationTiming(
            optimal_window_start=optimal_start,
            optimal_window_end=optimal_end,
            urgency_score=urgency_score,
            days_since_posted=days_since,
            estimated_applicants=estimated_applicants,
            recommendation=recommendation,
        )

    def get_urgency_score(self, job: Job) -> int:
        """Get just the urgency score for a job.

        Args:
            job: Job to analyze

        Returns:
            Urgency score 0-100
        """
        if job.posted_at:
            days_since = (datetime.utcnow() - job.posted_at).days
        else:
            days_since = 7

        return self._calculate_urgency_score(days_since)

    def _calculate_urgency_score(self, days_since: int) -> int:
        """Calculate urgency score based on days since posting.

        Args:
            days_since: Days since job was posted

        Returns:
            Score from 0-100
        """
        if days_since < 0:
            return 100

        for threshold, data in sorted(URGENCY_THRESHOLDS.items()):
            if days_since <= threshold:
                return data["score"]

        # Very old posting
        return max(0, 100 - (days_since * 3))

    def _get_recommendation(self, days_since: int) -> str:
        """Get timing recommendation text.

        Args:
            days_since: Days since job was posted

        Returns:
            Recommendation string
        """
        if days_since < 0:
            return "Future posting - set a reminder"

        for threshold, data in sorted(URGENCY_THRESHOLDS.items()):
            if days_since <= threshold:
                return data["recommendation"]

        return "Position likely filled, but worth a shot"

    def _estimate_applicants(self, days_since: int) -> int:
        """Estimate number of applicants based on days since posting.

        Based on industry averages for tech jobs.

        Args:
            days_since: Days since job was posted

        Returns:
            Estimated number of applicants
        """
        if days_since < 0:
            return 0

        for threshold, estimate in sorted(APPLICANT_ESTIMATES.items()):
            if days_since <= threshold:
                # Linear interpolation within the range
                return estimate

        # Extrapolate for very old posts
        return min(1000, 400 + (days_since - 30) * 10)

    def get_best_application_times(self) -> dict:
        """Get recommended application times.

        Based on hiring manager availability patterns.

        Returns:
            Dict with recommended times
        """
        return {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_hours": [9, 10, 13, 14],  # 9-10 AM, 1-2 PM
            "avoid_days": ["Friday", "Saturday", "Sunday"],
            "avoid_hours": list(range(0, 7)) + list(range(20, 24)),  # Late night/early morning
            "notes": [
                "Avoid Monday mornings - hiring managers are catching up on emails",
                "Tuesday through Thursday are optimal for review",
                "Early morning submissions (9 AM) often get reviewed first",
                "Avoid weekend submissions - they get buried",
            ],
        }

    def should_apply_now(self, job: Job) -> tuple[bool, str]:
        """Determine if user should apply immediately.

        Args:
            job: Job to evaluate

        Returns:
            Tuple of (should_apply_now, reason)
        """
        timing = self.calculate_timing(job)

        if timing.urgency_score >= 80:
            return True, timing.recommendation

        if timing.urgency_score >= 50:
            # Check if it's a good time of day
            now = datetime.utcnow()
            if now.weekday() < 5 and 9 <= now.hour <= 16:  # Weekday, business hours
                return True, "Good time - business hours on a weekday"
            return False, "Wait for business hours for best visibility"

        return False, timing.recommendation
