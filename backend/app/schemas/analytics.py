"""Analytics API schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from pydantic import BaseModel, Field


class ApplicationFunnelResponse(BaseModel):
    """Application funnel metrics response."""

    total_applied: int
    pending: int
    interviews: int
    offers: int
    rejected: int
    no_response: int
    conversion_rate: float


class ConversionMetricsResponse(BaseModel):
    """Conversion metrics for a dimension."""

    total: int
    interviews: int
    offers: int
    interview_rate: float
    offer_rate: float


class HeatmapCellResponse(BaseModel):
    """Single cell in the heatmap."""

    day: int = Field(ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    hour: int = Field(ge=0, le=23, description="Hour of day (0-23)")
    count: int
    success_rate: float


class HeatmapResponse(BaseModel):
    """Application success heatmap."""

    cells: list[HeatmapCellResponse]
    best_day: int
    best_hour: int
    total_applications: int


class AdvancedAnalyticsResponse(BaseModel):
    """Comprehensive advanced analytics response."""

    # Funnel
    funnel: ApplicationFunnelResponse

    # Conversion rates
    apply_to_interview_rate: float
    interview_to_offer_rate: float
    overall_conversion_rate: float

    # Time metrics
    avg_time_to_first_response_days: float | None
    avg_time_to_interview_days: float | None

    # Performance by dimension
    success_by_source: dict[str, ConversionMetricsResponse]
    success_by_match_score_range: dict[str, ConversionMetricsResponse]
    success_by_remote_type: dict[str, ConversionMetricsResponse]

    # Application patterns
    applications_by_day_of_week: dict[int, int]
    applications_by_hour: dict[int, int]
    best_performing_day: int
    best_performing_hour: int

    # Predictive
    estimated_interviews_this_month: int
    recommended_daily_applications: int


class PredictiveInsightsResponse(BaseModel):
    """Predictive insights response."""

    estimated_time_to_offer_days: int | None
    estimated_applications_needed: int
    current_success_rate: float
    trend_direction: str  # "improving", "stable", "declining"
    recommendations: list[str]


class TrendDataResponse(BaseModel):
    """Time-series trend data response."""

    labels: list[str]
    applications: list[int]
    interviews: list[int]
    offers: list[int]
