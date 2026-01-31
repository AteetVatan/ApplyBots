"""Application analytics service.

Standards: python_clean.mdc
- Dataclass return types
- Async operations
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import structlog

logger = structlog.get_logger(__name__)


# =============================================================================
# Advanced Analytics Data Classes
# =============================================================================


@dataclass
class ConversionMetrics:
    """Conversion metrics for a dimension."""

    total: int
    interviews: int
    offers: int
    interview_rate: float
    offer_rate: float


@dataclass
class HeatmapCell:
    """Single cell in the heatmap."""

    day: int  # 0-6 (Monday-Sunday)
    hour: int  # 0-23
    count: int
    success_rate: float  # Interview rate for apps submitted at this time


@dataclass
class HeatmapData:
    """Application success heatmap by day and hour."""

    cells: list[HeatmapCell]
    best_day: int
    best_hour: int
    total_applications: int


@dataclass
class AdvancedAnalytics:
    """Complete advanced analytics data."""

    # Funnel metrics
    funnel: "ApplicationFunnel"

    # Conversion rates
    apply_to_interview_rate: float
    interview_to_offer_rate: float
    overall_conversion_rate: float

    # Time metrics
    avg_time_to_first_response_days: float | None
    avg_time_to_interview_days: float | None

    # Performance by dimension
    success_by_source: dict[str, ConversionMetrics]
    success_by_match_score_range: dict[str, ConversionMetrics]
    success_by_remote_type: dict[str, ConversionMetrics]

    # Application patterns
    applications_by_day_of_week: dict[int, int]
    applications_by_hour: dict[int, int]
    best_performing_day: int
    best_performing_hour: int

    # Predictive
    estimated_interviews_this_month: int
    recommended_daily_applications: int


@dataclass
class PredictiveInsights:
    """Predictive analytics insights."""

    estimated_time_to_offer_days: int | None
    estimated_applications_needed: int
    current_success_rate: float
    trend_direction: str  # "improving", "stable", "declining"
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ApplicationFunnel:
    """Application funnel metrics."""

    total_applied: int
    pending: int
    interviews: int
    offers: int
    rejected: int
    no_response: int
    conversion_rate: float  # interviews / applied


@dataclass
class PerformanceMetrics:
    """Performance metrics for job search."""

    avg_match_score: float
    top_skills_matched: list[str]
    top_companies_applied: list[str]
    response_rate_by_source: dict[str, float]
    avg_days_to_response: float | None


@dataclass
class TrendData:
    """Time-series trend data."""

    labels: list[str]  # Date labels
    applications: list[int]
    interviews: list[int]
    offers: list[int]


class AnalyticsService:
    """Service for application analytics and insights."""

    def __init__(
        self,
        *,
        application_repository,
        job_repository,
    ) -> None:
        """Initialize analytics service.

        Args:
            application_repository: Application repository
            job_repository: Job repository
        """
        self._app_repo = application_repository
        self._job_repo = job_repository

    async def get_funnel(
        self,
        *,
        user_id: str,
        days: int = 30,
    ) -> ApplicationFunnel:
        """Get application funnel metrics.

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            ApplicationFunnel with metrics
        """
        since = datetime.utcnow() - timedelta(days=days)

        # Get applications in the time range
        applications = await self._app_repo.get_by_user_id_since(
            user_id=user_id,
            since=since,
        )

        # Count by status
        total = len(applications)
        pending = sum(1 for a in applications if a.status.value == "pending")
        interviews = sum(1 for a in applications if a.status.value == "interview")
        offers = sum(1 for a in applications if a.status.value == "offer")
        rejected = sum(1 for a in applications if a.status.value == "rejected")
        no_response = sum(1 for a in applications if a.status.value == "no_response")

        # Calculate conversion rate
        conversion_rate = (interviews / total * 100) if total > 0 else 0.0

        logger.info(
            "funnel_calculated",
            user_id=user_id,
            total=total,
            interviews=interviews,
            conversion_rate=conversion_rate,
        )

        return ApplicationFunnel(
            total_applied=total,
            pending=pending,
            interviews=interviews,
            offers=offers,
            rejected=rejected,
            no_response=no_response,
            conversion_rate=conversion_rate,
        )

    async def get_performance(
        self,
        *,
        user_id: str,
    ) -> PerformanceMetrics:
        """Get performance metrics for user's job search.

        Args:
            user_id: User ID

        Returns:
            PerformanceMetrics with insights
        """
        # Get all user applications
        applications = await self._app_repo.get_by_user_id(user_id)

        if not applications:
            return PerformanceMetrics(
                avg_match_score=0.0,
                top_skills_matched=[],
                top_companies_applied=[],
                response_rate_by_source={},
                avg_days_to_response=None,
            )

        # Calculate average match score
        match_scores = [a.match_score for a in applications if a.match_score]
        avg_match = sum(match_scores) / len(match_scores) if match_scores else 0.0

        # Top companies applied to
        company_counts: dict[str, int] = {}
        for app in applications:
            company = app.company or "Unknown"
            company_counts[company] = company_counts.get(company, 0) + 1

        top_companies = sorted(
            company_counts.keys(),
            key=lambda c: company_counts[c],
            reverse=True,
        )[:5]

        # Response rate by source
        source_stats: dict[str, dict[str, int]] = {}
        for app in applications:
            source = app.source or "unknown"
            if source not in source_stats:
                source_stats[source] = {"total": 0, "responded": 0}
            source_stats[source]["total"] += 1
            if app.status.value in ("interview", "offer", "rejected"):
                source_stats[source]["responded"] += 1

        response_rates = {
            source: stats["responded"] / stats["total"] * 100 if stats["total"] > 0 else 0.0
            for source, stats in source_stats.items()
        }

        # Average days to response
        response_times = []
        for app in applications:
            if app.submitted_at and app.updated_at:
                days = (app.updated_at - app.submitted_at).days
                if days > 0:
                    response_times.append(days)

        avg_days = sum(response_times) / len(response_times) if response_times else None

        return PerformanceMetrics(
            avg_match_score=avg_match,
            top_skills_matched=[],  # Would need skill tracking
            top_companies_applied=top_companies,
            response_rate_by_source=response_rates,
            avg_days_to_response=avg_days,
        )

    async def get_trends(
        self,
        *,
        user_id: str,
        days: int = 30,
    ) -> TrendData:
        """Get application trend data.

        Args:
            user_id: User ID
            days: Number of days of history

        Returns:
            TrendData with time-series data
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        # Get applications
        applications = await self._app_repo.get_by_user_id_since(
            user_id=user_id,
            since=datetime.combine(start_date, datetime.min.time()),
        )

        # Build daily counts
        labels = []
        app_counts = []
        interview_counts = []
        offer_counts = []

        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime("%m/%d"))

            # Count applications for this date
            day_apps = [
                a for a in applications
                if a.created_at.date() == current_date
            ]
            app_counts.append(len(day_apps))

            # Count interviews
            day_interviews = [
                a for a in applications
                if a.status.value == "interview"
                and a.updated_at
                and a.updated_at.date() == current_date
            ]
            interview_counts.append(len(day_interviews))

            # Count offers
            day_offers = [
                a for a in applications
                if a.status.value == "offer"
                and a.updated_at
                and a.updated_at.date() == current_date
            ]
            offer_counts.append(len(day_offers))

            current_date += timedelta(days=1)

        return TrendData(
            labels=labels,
            applications=app_counts,
            interviews=interview_counts,
            offers=offer_counts,
        )

    # =========================================================================
    # Advanced Analytics Methods
    # =========================================================================

    async def get_advanced_analytics(
        self,
        *,
        user_id: str,
        days: int = 90,
    ) -> AdvancedAnalytics:
        """Get comprehensive advanced analytics.

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            AdvancedAnalytics with all metrics
        """
        since = datetime.utcnow() - timedelta(days=days)
        applications = await self._app_repo.get_by_user_id_since(
            user_id=user_id,
            since=since,
        )

        # Get basic funnel
        funnel = await self.get_funnel(user_id=user_id, days=days)

        # Calculate conversion rates
        total = len(applications)
        interviews = sum(
            1 for a in applications if a.stage.value in ("interviewing", "offer")
        )
        offers = sum(1 for a in applications if a.stage.value == "offer")

        apply_to_interview = (interviews / total * 100) if total > 0 else 0.0
        interview_to_offer = (offers / interviews * 100) if interviews > 0 else 0.0
        overall_conversion = (offers / total * 100) if total > 0 else 0.0

        # Time metrics
        response_times = []
        interview_times = []
        for app in applications:
            if app.submitted_at and app.stage_updated_at:
                days_diff = (app.stage_updated_at - app.submitted_at).days
                if days_diff > 0:
                    response_times.append(days_diff)
                    if app.stage.value in ("interviewing", "offer"):
                        interview_times.append(days_diff)

        avg_response = (
            sum(response_times) / len(response_times) if response_times else None
        )
        avg_interview = (
            sum(interview_times) / len(interview_times) if interview_times else None
        )

        # Success by source
        success_by_source = self._calculate_success_by_dimension(
            applications, key=lambda a: getattr(a, "source", "unknown") or "unknown"
        )

        # Success by match score range
        def get_score_range(app):
            score = app.match_score or 0
            if score >= 90:
                return "90-100"
            elif score >= 80:
                return "80-89"
            elif score >= 70:
                return "70-79"
            elif score >= 60:
                return "60-69"
            else:
                return "Below 60"

        success_by_score = self._calculate_success_by_dimension(
            applications, key=get_score_range
        )

        # Success by remote type (would need job data)
        success_by_remote: dict[str, ConversionMetrics] = {}

        # Application patterns by day/hour
        day_counts: dict[int, int] = {i: 0 for i in range(7)}
        hour_counts: dict[int, int] = {i: 0 for i in range(24)}
        day_success: dict[int, list[bool]] = {i: [] for i in range(7)}
        hour_success: dict[int, list[bool]] = {i: [] for i in range(24)}

        for app in applications:
            if app.submitted_at:
                day = app.submitted_at.weekday()
                hour = app.submitted_at.hour
                day_counts[day] += 1
                hour_counts[hour] += 1

                is_success = app.stage.value in ("interviewing", "offer")
                day_success[day].append(is_success)
                hour_success[hour].append(is_success)

        # Find best performing day/hour
        best_day = max(
            range(7),
            key=lambda d: (
                sum(day_success[d]) / len(day_success[d])
                if day_success[d]
                else 0
            ),
        )
        best_hour = max(
            range(24),
            key=lambda h: (
                sum(hour_success[h]) / len(hour_success[h])
                if hour_success[h]
                else 0
            ),
        )

        # Predictive: estimate interviews this month
        days_elapsed = min(days, 30)
        interview_rate = apply_to_interview / 100 if apply_to_interview else 0.05
        daily_apps = total / days if days > 0 else 1
        estimated_interviews = int(daily_apps * 30 * interview_rate)

        # Recommended daily applications (to get ~4 interviews/month)
        target_interviews = 4
        if interview_rate > 0:
            recommended_daily = int(target_interviews / (30 * interview_rate)) + 1
        else:
            recommended_daily = 5

        logger.info(
            "advanced_analytics_calculated",
            user_id=user_id,
            total_apps=total,
            interview_rate=apply_to_interview,
        )

        return AdvancedAnalytics(
            funnel=funnel,
            apply_to_interview_rate=apply_to_interview,
            interview_to_offer_rate=interview_to_offer,
            overall_conversion_rate=overall_conversion,
            avg_time_to_first_response_days=avg_response,
            avg_time_to_interview_days=avg_interview,
            success_by_source=success_by_source,
            success_by_match_score_range=success_by_score,
            success_by_remote_type=success_by_remote,
            applications_by_day_of_week=day_counts,
            applications_by_hour=hour_counts,
            best_performing_day=best_day,
            best_performing_hour=best_hour,
            estimated_interviews_this_month=estimated_interviews,
            recommended_daily_applications=recommended_daily,
        )

    async def get_heatmap(
        self,
        *,
        user_id: str,
        days: int = 90,
    ) -> HeatmapData:
        """Get application success heatmap by day and hour.

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            HeatmapData with success rates by time
        """
        since = datetime.utcnow() - timedelta(days=days)
        applications = await self._app_repo.get_by_user_id_since(
            user_id=user_id,
            since=since,
        )

        # Build grid: [day][hour] -> {total, success}
        grid: dict[tuple[int, int], dict[str, int]] = {}
        for d in range(7):
            for h in range(24):
                grid[(d, h)] = {"total": 0, "success": 0}

        for app in applications:
            if app.submitted_at:
                day = app.submitted_at.weekday()
                hour = app.submitted_at.hour
                grid[(day, hour)]["total"] += 1
                if app.stage.value in ("interviewing", "offer"):
                    grid[(day, hour)]["success"] += 1

        # Convert to cells
        cells = []
        best_rate = 0.0
        best_day = 0
        best_hour = 9  # Default to 9 AM

        for (day, hour), stats in grid.items():
            rate = (
                stats["success"] / stats["total"] * 100
                if stats["total"] > 0
                else 0.0
            )
            cells.append(
                HeatmapCell(
                    day=day,
                    hour=hour,
                    count=stats["total"],
                    success_rate=rate,
                )
            )

            if stats["total"] >= 3 and rate > best_rate:
                best_rate = rate
                best_day = day
                best_hour = hour

        return HeatmapData(
            cells=cells,
            best_day=best_day,
            best_hour=best_hour,
            total_applications=len(applications),
        )

    async def get_predictions(
        self,
        *,
        user_id: str,
    ) -> PredictiveInsights:
        """Get predictive insights for user's job search.

        Args:
            user_id: User ID

        Returns:
            PredictiveInsights with predictions and recommendations
        """
        # Get recent and older analytics to compare
        recent = await self.get_advanced_analytics(user_id=user_id, days=30)
        older = await self.get_advanced_analytics(user_id=user_id, days=90)

        # Determine trend
        recent_rate = recent.apply_to_interview_rate
        older_rate = older.apply_to_interview_rate

        if recent_rate > older_rate + 5:
            trend = "improving"
        elif recent_rate < older_rate - 5:
            trend = "declining"
        else:
            trend = "stable"

        # Estimate time to offer
        if recent.overall_conversion_rate > 0:
            # Based on current rate, estimate apps needed for 1 offer
            apps_for_offer = int(100 / recent.overall_conversion_rate)
            daily_rate = recent.funnel.total_applied / 30 if recent.funnel.total_applied > 0 else 1
            days_to_offer = int(apps_for_offer / daily_rate) if daily_rate > 0 else None
        else:
            days_to_offer = None
            apps_for_offer = 50  # Default estimate

        # Generate recommendations
        recommendations = []

        if recent.apply_to_interview_rate < 10:
            recommendations.append(
                "Your interview rate is below average. Consider optimizing your resume for ATS."
            )

        if recent.best_performing_day is not None:
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            recommendations.append(
                f"You tend to have better success applying on {day_names[recent.best_performing_day]}s."
            )

        if recent.best_performing_hour is not None:
            recommendations.append(
                f"Submitting applications around {recent.best_performing_hour}:00 has worked well for you."
            )

        # Check match score impact
        high_score_metrics = recent.success_by_match_score_range.get("90-100")
        if high_score_metrics and high_score_metrics.interview_rate > recent.apply_to_interview_rate:
            recommendations.append(
                "Focus on jobs with 90%+ match scores - they have higher success rates for you."
            )

        if recent.funnel.total_applied < 10:
            recommendations.append(
                "Increase your application volume. Most successful job seekers apply to 10+ jobs per week."
            )

        return PredictiveInsights(
            estimated_time_to_offer_days=days_to_offer,
            estimated_applications_needed=apps_for_offer,
            current_success_rate=recent.overall_conversion_rate,
            trend_direction=trend,
            recommendations=recommendations,
        )

    def _calculate_success_by_dimension(
        self,
        applications,
        key,
    ) -> dict[str, ConversionMetrics]:
        """Calculate success metrics grouped by a dimension.

        Args:
            applications: List of applications
            key: Function to extract dimension value from application

        Returns:
            Dict mapping dimension values to ConversionMetrics
        """
        groups: dict[str, dict[str, int]] = {}

        for app in applications:
            dim_value = key(app)
            if dim_value not in groups:
                groups[dim_value] = {"total": 0, "interviews": 0, "offers": 0}

            groups[dim_value]["total"] += 1
            if app.stage.value in ("interviewing", "offer"):
                groups[dim_value]["interviews"] += 1
            if app.stage.value == "offer":
                groups[dim_value]["offers"] += 1

        result = {}
        for dim_value, stats in groups.items():
            total = stats["total"]
            interviews = stats["interviews"]
            offers = stats["offers"]

            result[dim_value] = ConversionMetrics(
                total=total,
                interviews=interviews,
                offers=offers,
                interview_rate=(interviews / total * 100) if total > 0 else 0.0,
                offer_rate=(offers / total * 100) if total > 0 else 0.0,
            )

        return result
