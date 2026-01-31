"""Wellness service for mental health support.

Standards: python_clean.mdc
- Supportive, non-judgmental messaging
- Data-driven burnout detection
"""

import random
from datetime import datetime, timedelta
from typing import Protocol, Sequence

import structlog

from app.core.domain.application import ApplicationStage
from app.core.domain.wellness import (
    BREAK_REMINDERS,
    ENCOURAGEMENT_MESSAGES,
    WELLNESS_TIPS,
    BurnoutSignals,
    WellnessInsight,
    WellnessInsightType,
    WellnessStatus,
)

logger = structlog.get_logger(__name__)


class ApplicationRepository(Protocol):
    """Protocol for application repository."""

    async def get_by_user_id(self, user_id: str) -> Sequence: ...
    async def get_by_user_id_since(
        self, user_id: str, since: datetime
    ) -> Sequence: ...


class WellnessService:
    """Service for mental wellness support during job search."""

    # Thresholds for burnout detection
    REJECTION_STREAK_WARNING = 5
    REJECTION_STREAK_HIGH = 10
    HIGH_ACTIVITY_HOURS = 4
    PANIC_APPLY_THRESHOLD = 10  # Apps in one day

    def __init__(
        self,
        *,
        application_repo: ApplicationRepository,
    ) -> None:
        """Initialize wellness service.

        Args:
            application_repo: Application repository for data access
        """
        self._app_repo = application_repo

    async def get_daily_insight(self, user_id: str) -> WellnessInsight:
        """Get a personalized daily wellness insight.

        Args:
            user_id: User ID

        Returns:
            Contextual WellnessInsight based on user's situation
        """
        # Get user's recent data
        status = await self.get_wellness_status(user_id)

        # Check for burnout warning first
        if status.burnout_risk == "high":
            return WellnessInsight(
                insight_type=WellnessInsightType.BURNOUT_WARNING,
                title="Time to Recharge",
                message=(
                    "You've been working hard on your job search. "
                    "It's important to take breaks and maintain your well-being. "
                    "A rested mind performs better in interviews!"
                ),
                action_suggestion="Take the rest of the day off from applications",
                priority=3,
            )

        # Check for recent rejection streak
        if status.rejection_streak >= self.REJECTION_STREAK_WARNING:
            return self._get_rejection_support_insight(status.rejection_streak)

        # Check for milestones or positive events
        apps = await self._app_repo.get_by_user_id(user_id)

        # Check for recent interview
        recent_interviews = [
            a for a in apps
            if a.stage == ApplicationStage.INTERVIEWING
            and a.stage_updated_at
            and (datetime.utcnow() - a.stage_updated_at).days < 3
        ]
        if recent_interviews:
            messages = ENCOURAGEMENT_MESSAGES["first_interview"]
            return WellnessInsight(
                insight_type=WellnessInsightType.ENCOURAGEMENT,
                title="Interview Coming Up!",
                message=random.choice(messages),
                action_suggestion="Prepare by researching the company",
                priority=2,
            )

        # Check application milestones
        total_applied = len([a for a in apps if a.stage != ApplicationStage.SAVED])
        milestone_insight = self._check_milestone(total_applied)
        if milestone_insight:
            return milestone_insight

        # Default to a random tip or motivation
        if random.random() < 0.5:
            return WellnessInsight(
                insight_type=WellnessInsightType.TIP,
                title="Job Search Tip",
                message=random.choice(WELLNESS_TIPS),
                priority=1,
            )
        else:
            return WellnessInsight(
                insight_type=WellnessInsightType.ENCOURAGEMENT,
                title="Keep Going!",
                message=random.choice(ENCOURAGEMENT_MESSAGES["general_motivation"]),
                priority=1,
            )

    async def get_wellness_status(self, user_id: str) -> WellnessStatus:
        """Get comprehensive wellness status for a user.

        Args:
            user_id: User ID

        Returns:
            WellnessStatus with analysis
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get recent applications
        week_ago = now - timedelta(days=7)
        recent_apps = await self._app_repo.get_by_user_id_since(
            user_id=user_id,
            since=week_ago,
        )

        today_apps = [
            a for a in recent_apps
            if a.created_at >= today_start
        ]

        # Calculate rejection streak
        rejection_streak = self._calculate_rejection_streak(recent_apps)

        # Days since last positive (interview or offer)
        all_apps = await self._app_repo.get_by_user_id(user_id)
        days_since_positive = self._days_since_last_positive(all_apps)

        # Determine activity level
        daily_count = len(today_apps)
        if daily_count >= 15:
            activity_level = "very_high"
        elif daily_count >= 10:
            activity_level = "high"
        elif daily_count >= 5:
            activity_level = "moderate"
        else:
            activity_level = "low"

        # Assess burnout risk
        burnout_risk = self._assess_burnout_risk(
            rejection_streak=rejection_streak,
            daily_apps=daily_count,
            days_since_positive=days_since_positive,
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            burnout_risk=burnout_risk,
            activity_level=activity_level,
            rejection_streak=rejection_streak,
        )

        logger.debug(
            "wellness_status_calculated",
            user_id=user_id,
            burnout_risk=burnout_risk,
            rejection_streak=rejection_streak,
        )

        return WellnessStatus(
            user_id=user_id,
            activity_level=activity_level,
            rejection_streak=rejection_streak,
            days_since_last_positive=days_since_positive,
            burnout_risk=burnout_risk,
            recommended_action=recommendation,
        )

    async def detect_burnout_signals(self, user_id: str) -> BurnoutSignals:
        """Detect specific burnout warning signals.

        Args:
            user_id: User ID

        Returns:
            BurnoutSignals with detected issues
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        recent_apps = await self._app_repo.get_by_user_id_since(
            user_id=user_id,
            since=week_ago,
        )

        today_apps = [a for a in recent_apps if a.created_at >= today_start]

        # Consecutive rejections
        rejection_streak = self._calculate_rejection_streak(recent_apps)

        # Hours active today (estimate based on app timestamps)
        if today_apps:
            first_app = min(today_apps, key=lambda a: a.created_at)
            hours_active = (now - first_app.created_at).total_seconds() / 3600
        else:
            hours_active = 0

        # Declining match scores
        scores = [a.match_score for a in recent_apps if a.match_score]
        declining_scores = False
        if len(scores) >= 5:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            if sum(first_half)/len(first_half) > sum(second_half)/len(second_half) + 5:
                declining_scores = True

        # Panic applying (sudden increase)
        panic_applying = len(today_apps) >= self.PANIC_APPLY_THRESHOLD

        # No breaks (apps every hour for 4+ hours)
        no_breaks = hours_active >= self.HIGH_ACTIVITY_HOURS

        return BurnoutSignals(
            consecutive_rejections=rejection_streak,
            hours_active_today=hours_active,
            declining_match_scores=declining_scores,
            panic_applying=panic_applying,
            no_breaks_taken=no_breaks,
        )

    def get_encouragement_message(self, context: str) -> str:
        """Get an encouragement message for a specific context.

        Args:
            context: Context key (e.g., "first_interview", "streak_maintained")

        Returns:
            Encouraging message string
        """
        if context in ENCOURAGEMENT_MESSAGES:
            return random.choice(ENCOURAGEMENT_MESSAGES[context])
        return random.choice(ENCOURAGEMENT_MESSAGES["general_motivation"])

    def get_break_reminder(self) -> WellnessInsight:
        """Get a break reminder insight.

        Returns:
            Break reminder WellnessInsight
        """
        return WellnessInsight(
            insight_type=WellnessInsightType.BREAK_REMINDER,
            title="Break Time",
            message=random.choice(BREAK_REMINDERS),
            action_suggestion="Step away from the screen for 5 minutes",
            priority=2,
        )

    def _calculate_rejection_streak(self, applications) -> int:
        """Calculate consecutive rejection streak."""
        # Sort by date descending
        sorted_apps = sorted(
            applications,
            key=lambda a: a.stage_updated_at or a.created_at,
            reverse=True,
        )

        streak = 0
        for app in sorted_apps:
            if app.stage == ApplicationStage.REJECTED:
                streak += 1
            elif app.stage in (ApplicationStage.INTERVIEWING, ApplicationStage.OFFER):
                break  # Streak broken by positive outcome

        return streak

    def _days_since_last_positive(self, applications) -> int | None:
        """Calculate days since last interview or offer."""
        positive_apps = [
            a for a in applications
            if a.stage in (ApplicationStage.INTERVIEWING, ApplicationStage.OFFER)
            and a.stage_updated_at
        ]

        if not positive_apps:
            return None

        latest = max(positive_apps, key=lambda a: a.stage_updated_at)
        return (datetime.utcnow() - latest.stage_updated_at).days

    def _assess_burnout_risk(
        self,
        *,
        rejection_streak: int,
        daily_apps: int,
        days_since_positive: int | None,
    ) -> str:
        """Assess overall burnout risk level."""
        risk_score = 0

        # High rejection streak
        if rejection_streak >= self.REJECTION_STREAK_HIGH:
            risk_score += 3
        elif rejection_streak >= self.REJECTION_STREAK_WARNING:
            risk_score += 2

        # Excessive daily activity
        if daily_apps >= 15:
            risk_score += 2
        elif daily_apps >= 10:
            risk_score += 1

        # Long time without positive feedback
        if days_since_positive is not None:
            if days_since_positive >= 30:
                risk_score += 2
            elif days_since_positive >= 14:
                risk_score += 1

        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        return "low"

    def _generate_recommendation(
        self,
        *,
        burnout_risk: str,
        activity_level: str,
        rejection_streak: int,
    ) -> str:
        """Generate actionable recommendation."""
        if burnout_risk == "high":
            return "Consider taking a break from applications today. Focus on self-care."

        if activity_level == "very_high":
            return "You're applying at a high rate. Quality applications often beat quantity."

        if rejection_streak >= 5:
            return "Multiple rejections are normal. Consider reviewing your resume with fresh eyes."

        if activity_level == "low":
            return "Try to maintain consistency with your applications - even 3-5 per day helps."

        return "You're doing great! Keep a steady pace and take breaks when needed."

    def _get_rejection_support_insight(self, streak: int) -> WellnessInsight:
        """Get supportive insight for rejection streak."""
        if streak >= 10:
            return WellnessInsight(
                insight_type=WellnessInsightType.ENCOURAGEMENT,
                title="Hang In There",
                message=(
                    f"You've faced {streak} rejections recently, but remember: "
                    "this is part of the process. Many successful people faced "
                    "dozens of rejections before landing their dream job. "
                    "Each application teaches you something."
                ),
                action_suggestion=(
                    "Consider reaching out to a mentor or friend to review your approach"
                ),
                priority=3,
            )
        else:
            return WellnessInsight(
                insight_type=WellnessInsightType.ENCOURAGEMENT,
                title="Keep Your Head Up",
                message=(
                    "A few rejections don't define your worth or capabilities. "
                    "Companies reject great candidates all the time due to timing, "
                    "internal candidates, or random factors beyond your control."
                ),
                action_suggestion="Focus on what you can control: your application quality",
                priority=2,
            )

    def _check_milestone(self, total_applied: int) -> WellnessInsight | None:
        """Check if user hit an application milestone."""
        milestones = {
            10: "application_milestone_10",
            25: "application_milestone_25",
            50: "application_milestone_50",
        }

        for count, key in milestones.items():
            if total_applied == count:
                return WellnessInsight(
                    insight_type=WellnessInsightType.MILESTONE,
                    title=f"Milestone: {count} Applications!",
                    message=random.choice(ENCOURAGEMENT_MESSAGES[key]),
                    priority=2,
                )

        return None
