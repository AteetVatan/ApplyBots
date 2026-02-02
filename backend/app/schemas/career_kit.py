"""CareerKit schemas for Expert Apply API.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types with Field constraints
"""

import re
from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


# =============================================================================
# Enums as Literals for API
# =============================================================================

PhaseType = Literal["analyze", "questionnaire", "generate", "complete"]
ConfidenceType = Literal["high", "medium", "low"]
RequirementLevelType = Literal["must", "nice"]
GapStatusType = Literal["covered", "partial", "missing", "unclear"]
DeltaActionType = Literal["keep", "rewrite", "remove", "add"]
ResumeSourceType = Literal["uploaded", "draft"]
AnswerType = Literal["text", "yes_no", "scale", "multi_select"]


# =============================================================================
# Input Schemas
# =============================================================================


class CustomJDSchema(BaseModel):
    """Custom job description pasted from external source."""

    title: str = Field(..., min_length=3, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=100, max_length=50000)
    location: str | None = None
    url: str | None = None

    def generate_session_name(self) -> str:
        """Generate session name: custom_job_[title]_[company]."""
        safe_title = re.sub(r"[^a-z0-9]+", "_", self.title.lower())[:30]
        safe_company = re.sub(r"[^a-z0-9]+", "_", self.company.lower())[:20]
        return f"custom_job_{safe_title}_{safe_company}"


class ResumeSourceSchema(BaseModel):
    """Resume source - either uploaded resume or builder draft."""

    source_type: ResumeSourceType
    resume_id: str


class AnalyzeRequest(BaseModel):
    """Request to analyze JD vs CV. Supports multiple sources."""

    # Job source (one required)
    job_id: str | None = None
    custom_jd: CustomJDSchema | None = None

    # Resume source (required)
    resume_source: ResumeSourceSchema

    @model_validator(mode="after")
    def validate_job_source(self) -> Self:
        """Validate that exactly one job source is provided."""
        if not self.job_id and not self.custom_jd:
            raise ValueError("Either job_id or custom_jd must be provided")
        if self.job_id and self.custom_jd:
            raise ValueError("Provide either job_id or custom_jd, not both")
        return self


class QuestionnaireAnswerSchema(BaseModel):
    """User's answer to a questionnaire question."""

    question_id: str
    answer: str | list[str]  # str for text/yes_no/scale, list for multi_select


class GenerateRequest(BaseModel):
    """Request to generate tailored CV and interview prep."""

    session_id: str
    answers: list[QuestionnaireAnswerSchema]


class SaveAnswersRequest(BaseModel):
    """Request to save questionnaire answers (auto-save)."""

    answers: list[QuestionnaireAnswerSchema]


# =============================================================================
# Output Schemas - Analysis Phase
# =============================================================================


class RequirementSchema(BaseModel):
    """Extracted JD requirement."""

    name: str
    level: RequirementLevelType
    category: str
    keywords: list[str] = []
    original_text: str | None = None


class EvidenceSchema(BaseModel):
    """Evidence from CV supporting a requirement."""

    source: str  # "uploaded_cv" or "questionnaire"
    quote: str
    cv_section: str | None = None


class GapMapItemSchema(BaseModel):
    """Gap analysis item mapping requirement to evidence."""

    requirement_name: str
    status: GapStatusType
    evidence: list[EvidenceSchema] = []
    risk_note: str | None = None
    question_needed: bool = False


class QuestionSchema(BaseModel):
    """Clarification question for missing/unclear items."""

    id: str
    topic: str
    question: str
    answer_type: AnswerType
    why_asked: str
    options: list[str] | None = None


# =============================================================================
# Output Schemas - Generation Phase
# =============================================================================


class BulletSchema(BaseModel):
    """A bullet point with confidence score."""

    text: str
    confidence_score: ConfidenceType
    source_ref: str | None = None
    needs_verification: bool = False


class DeltaInstructionSchema(BaseModel):
    """Instruction for modifying a CV bullet."""

    bullet_id: str
    action: DeltaActionType
    original_text: str | None = None
    new_text: str | None = None
    confidence_score: ConfidenceType = "high"
    reason: str | None = None


class TailoredCVSchema(BaseModel):
    """Generated tailored CV content."""

    targeted_title: str
    summary: str
    skills: list[str] = []
    experience_bullets: dict[str, list[BulletSchema]] = {}  # company -> bullets
    projects: list[BulletSchema] = []
    education: list[str] = []
    truth_notes: list[str] = []


class STARStorySchema(BaseModel):
    """STAR format story for behavioral questions."""

    title: str
    situation: str
    task: str
    action: str
    result: str
    applicable_to: list[str] = []


class InterviewQuestionSchema(BaseModel):
    """Expected interview question with suggested answer."""

    question: str
    category: str
    difficulty: Literal["easy", "medium", "hard"]
    suggested_answer: str | None = None


class PrepPlanDaySchema(BaseModel):
    """Single day in the 7-day prep plan."""

    day: int
    focus: str
    tasks: list[str] = []
    time_estimate_minutes: int = 60


class InterviewPrepSchema(BaseModel):
    """Interview preparation kit."""

    role_understanding: str
    likely_questions: list[InterviewQuestionSchema] = []
    suggested_answers: dict[str, str] = {}
    story_bank: list[STARStorySchema] = []
    tech_deep_dive_topics: list[str] = []
    seven_day_prep_plan: list[PrepPlanDaySchema] = []


# =============================================================================
# API Response Schemas
# =============================================================================


class AnalyzeResponse(BaseModel):
    """Response from /analyze endpoint (Phase 1 complete)."""

    session_id: str
    session_name: str
    phase: PhaseType = "questionnaire"
    is_custom_job: bool = False
    requirements: list[RequirementSchema]
    gap_map: list[GapMapItemSchema]
    questionnaire: list[QuestionSchema]
    # CV and interview are null in this phase
    tailored_cv: TailoredCVSchema | None = None
    interview_prep: InterviewPrepSchema | None = None


class GenerateResponse(BaseModel):
    """Response from /generate endpoint (Phase 2 complete)."""

    session_id: str
    session_name: str
    phase: PhaseType = "complete"
    is_custom_job: bool = False
    requirements: list[RequirementSchema]
    gap_map: list[GapMapItemSchema]
    questionnaire: list[QuestionSchema]
    delta_instructions: list[DeltaInstructionSchema]
    tailored_cv: TailoredCVSchema
    generated_cv_draft_id: str | None = None
    interview_prep: InterviewPrepSchema


class SessionSummarySchema(BaseModel):
    """Summary of a CareerKit session for list view."""

    id: str
    session_name: str
    phase: PhaseType
    is_custom_job: bool
    job_title: str
    company: str
    created_at: datetime
    updated_at: datetime | None


class SessionDetailResponse(BaseModel):
    """Full session details for loading saved session."""

    id: str
    session_name: str
    phase: PhaseType
    is_custom_job: bool
    job_id: str | None
    custom_jd: CustomJDSchema | None
    resume_source: ResumeSourceSchema
    requirements: list[RequirementSchema] | None
    gap_map: list[GapMapItemSchema] | None
    questionnaire: list[QuestionSchema] | None
    answers: list[QuestionnaireAnswerSchema] | None
    delta_instructions: list[DeltaInstructionSchema] | None
    tailored_cv: TailoredCVSchema | None
    generated_cv_draft_id: str | None
    interview_prep: InterviewPrepSchema | None
    created_at: datetime
    updated_at: datetime | None


class SessionListResponse(BaseModel):
    """List of user's CareerKit sessions."""

    items: list[SessionSummarySchema]
    total: int


# =============================================================================
# Resume Selection Schemas
# =============================================================================


class ResumeOptionSchema(BaseModel):
    """Resume option for selection UI."""

    id: str
    name: str
    source_type: ResumeSourceType
    is_primary: bool = False
    updated_at: datetime | None = None
    preview: str | None = None  # First 100 chars of summary or skills


class AvailableResumesResponse(BaseModel):
    """List of all available resumes for CareerKit."""

    uploaded_resumes: list[ResumeOptionSchema]
    builder_drafts: list[ResumeOptionSchema]
