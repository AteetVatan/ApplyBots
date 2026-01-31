"""Career tools schemas for Interview, Negotiation, and Career Advisor.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
- kw-only args for >3 params
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# Common Types
# =============================================================================


class InterviewType(str, Enum):
    """Type of interview to simulate."""

    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    MIXED = "mixed"


class ExperienceLevel(str, Enum):
    """Candidate experience level."""

    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class FeedbackRating(str, Enum):
    """Rating scale for feedback."""

    POOR = "poor"
    NEEDS_IMPROVEMENT = "needs_improvement"
    GOOD = "good"
    EXCELLENT = "excellent"


# =============================================================================
# Interview Roleplay Schemas
# =============================================================================


class InterviewStartRequest(BaseModel):
    """Request to start an interview session."""

    target_role: str = Field(..., min_length=1, max_length=200)
    company_name: str | None = Field(default=None, max_length=200)
    interview_type: InterviewType = Field(default=InterviewType.MIXED)
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.MID)
    focus_areas: list[str] = Field(default_factory=list, max_length=10)


class InterviewQuestion(BaseModel):
    """A single interview question."""

    question_id: str
    question_text: str
    question_type: InterviewType
    difficulty: Literal["easy", "medium", "hard"]
    context: str | None = None


class InterviewStartResponse(BaseModel):
    """Response when starting an interview session."""

    session_id: str
    target_role: str
    first_question: InterviewQuestion
    total_questions: int
    estimated_duration_minutes: int


class InterviewRespondRequest(BaseModel):
    """Request to submit an answer."""

    session_id: str
    question_id: str
    answer: str = Field(..., min_length=1, max_length=5000)


class AnswerFeedback(BaseModel):
    """Feedback on a single answer."""

    score: int = Field(..., ge=1, le=10)
    rating: FeedbackRating
    strengths: list[str]
    improvements: list[str]
    example_answer: str | None = None
    tips: list[str] = Field(default_factory=list)


class InterviewRespondResponse(BaseModel):
    """Response after submitting an answer."""

    feedback: AnswerFeedback
    next_question: InterviewQuestion | None
    questions_remaining: int
    current_score: float


class InterviewEndRequest(BaseModel):
    """Request to end an interview session."""

    session_id: str


class InterviewSummary(BaseModel):
    """Summary of completed interview."""

    session_id: str
    target_role: str
    total_questions: int
    questions_answered: int
    overall_score: float
    overall_rating: FeedbackRating
    strengths: list[str]
    areas_to_improve: list[str]
    recommendations: list[str]
    duration_minutes: int


class InterviewEndResponse(BaseModel):
    """Response when ending an interview session."""

    summary: InterviewSummary


# =============================================================================
# Offer Negotiation Schemas
# =============================================================================


class OfferDetails(BaseModel):
    """Details of a job offer."""

    base_salary: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    signing_bonus: float | None = Field(default=None, ge=0)
    annual_bonus_percent: float | None = Field(default=None, ge=0, le=100)
    equity_value: float | None = Field(default=None, ge=0)
    equity_vesting_years: int | None = Field(default=None, ge=1, le=10)
    pto_days: int | None = Field(default=None, ge=0)
    remote_policy: Literal["remote", "hybrid", "onsite"] | None = None
    other_benefits: list[str] = Field(default_factory=list)


class NegotiationAnalyzeRequest(BaseModel):
    """Request to analyze an offer."""

    offer: OfferDetails
    target_role: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    years_experience: int = Field(..., ge=0, le=50)
    competing_offers: int = Field(default=0, ge=0)
    current_salary: float | None = Field(default=None, gt=0)


class MarketComparison(BaseModel):
    """Comparison to market rates."""

    percentile: int = Field(..., ge=0, le=100)
    market_low: float
    market_median: float
    market_high: float
    position: Literal["below_market", "at_market", "above_market"]


class NegotiationAnalyzeResponse(BaseModel):
    """Response with offer analysis."""

    total_compensation: float
    market_comparison: MarketComparison
    strengths: list[str]
    concerns: list[str]
    negotiation_room: Literal["low", "medium", "high"]
    priority_items: list[str]


class NegotiationStrategyRequest(BaseModel):
    """Request for negotiation strategy."""

    offer: OfferDetails
    target_role: str
    location: str
    years_experience: int
    target_salary: float | None = None
    priorities: list[str] = Field(default_factory=list)
    risk_tolerance: Literal["low", "medium", "high"] = "medium"


class NegotiationScript(BaseModel):
    """Scripts for negotiation scenarios."""

    initial_response: str
    counter_offer_email: str
    phone_script: str
    fallback_positions: list[str]


class NegotiationStrategyResponse(BaseModel):
    """Response with negotiation strategy."""

    recommended_counter: float
    justification_points: list[str]
    scripts: NegotiationScript
    timing_advice: str
    risk_assessment: str
    alternative_asks: list[str]


# =============================================================================
# Career Advisor Schemas
# =============================================================================


class CareerAssessRequest(BaseModel):
    """Request for career assessment."""

    current_role: str = Field(..., min_length=1, max_length=200)
    years_in_role: int = Field(..., ge=0, le=50)
    total_experience: int = Field(..., ge=0, le=50)
    current_industry: str = Field(..., min_length=1, max_length=200)
    skills: list[str] = Field(default_factory=list, max_length=50)
    interests: list[str] = Field(default_factory=list, max_length=20)
    goals: list[str] = Field(default_factory=list, max_length=10)
    constraints: list[str] = Field(default_factory=list, max_length=10)


class SkillAssessment(BaseModel):
    """Assessment of a skill category."""

    category: str
    skills: list[str]
    proficiency: Literal["beginner", "intermediate", "advanced", "expert"]
    market_demand: Literal["low", "medium", "high"]


class CareerAssessResponse(BaseModel):
    """Response with career assessment."""

    strengths: list[str]
    transferable_skills: list[str]
    skill_assessments: list[SkillAssessment]
    market_position: str
    growth_potential: Literal["low", "medium", "high"]
    key_insights: list[str]


class CareerPathsRequest(BaseModel):
    """Request for career path recommendations."""

    current_role: str
    years_experience: int
    skills: list[str]
    target_industries: list[str] = Field(default_factory=list)
    salary_expectation: float | None = None
    willing_to_relocate: bool = False
    willing_to_reskill: bool = True
    timeline_months: int = Field(default=12, ge=1, le=60)


class CareerPath(BaseModel):
    """A recommended career path."""

    target_role: str
    target_industry: str
    fit_score: int = Field(..., ge=0, le=100)
    salary_range_low: float
    salary_range_high: float
    time_to_transition_months: int
    skill_gaps: list[str]
    required_certifications: list[str]
    steps: list[str]
    pros: list[str]
    cons: list[str]


class LearningResource(BaseModel):
    """A recommended learning resource."""

    skill: str
    resource_type: Literal["course", "certification", "book", "project", "mentorship"]
    name: str
    provider: str | None = None
    estimated_hours: int
    priority: Literal["critical", "important", "nice_to_have"]


class CareerPathsResponse(BaseModel):
    """Response with career path recommendations."""

    recommended_paths: list[CareerPath]
    learning_roadmap: list[LearningResource]
    quick_wins: list[str]
    long_term_goals: list[str]
    networking_suggestions: list[str]
