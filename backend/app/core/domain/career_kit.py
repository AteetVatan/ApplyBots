"""CareerKit domain models.

Standards: python_clean.mdc
- Enum for phases and confidence scores
- Dataclasses for domain entities
- Typed collections
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class CareerKitPhase(Enum):
    """CareerKit workflow phase."""

    ANALYZE = "analyze"
    QUESTIONNAIRE = "questionnaire"
    GENERATE = "generate"
    COMPLETE = "complete"


class ConfidenceScore(Enum):
    """Confidence level for generated content.

    HIGH: Direct quote from original CV
    MEDIUM: Inferred/rewritten from CV experience
    LOW: Based only on questionnaire answer
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementLevel(Enum):
    """JD requirement importance level."""

    MUST_HAVE = "must"
    NICE_TO_HAVE = "nice"


class GapStatus(Enum):
    """Gap analysis status for a requirement."""

    COVERED = "covered"
    PARTIAL = "partial"
    MISSING = "missing"
    UNCLEAR = "unclear"


class DeltaAction(Enum):
    """Action to take on a CV bullet."""

    KEEP = "keep"
    REWRITE = "rewrite"
    REMOVE = "remove"
    ADD = "add"


# =============================================================================
# Job Description Structures
# =============================================================================


@dataclass
class CustomJD:
    """Custom job description pasted from external source."""

    title: str
    company: str
    description: str
    location: str | None = None
    url: str | None = None

    def generate_session_name(self) -> str:
        """Generate session name: custom_job_[title]_[company]."""
        import re

        safe_title = re.sub(r"[^a-z0-9]+", "_", self.title.lower())[:30]
        safe_company = re.sub(r"[^a-z0-9]+", "_", self.company.lower())[:20]
        return f"custom_job_{safe_title}_{safe_company}"


@dataclass
class Requirement:
    """Extracted JD requirement."""

    name: str
    level: RequirementLevel
    category: str  # e.g., "technical", "experience", "soft_skill"
    keywords: list[str] = field(default_factory=list)
    original_text: str | None = None


# =============================================================================
# Evidence & Gap Analysis Structures
# =============================================================================


@dataclass
class Evidence:
    """Evidence from CV supporting a requirement."""

    source: str  # "uploaded_cv" or "questionnaire"
    quote: str
    cv_section: str | None = None  # e.g., "experience.company_name" or "skills"


@dataclass
class GapMapItem:
    """Mapping of a JD requirement to CV evidence."""

    requirement_name: str
    status: GapStatus
    evidence: list[Evidence] = field(default_factory=list)
    risk_note: str | None = None
    question_needed: bool = False


# =============================================================================
# Questionnaire Structures
# =============================================================================


@dataclass
class Question:
    """Clarification question for missing/unclear items."""

    id: str
    topic: str
    question: str
    answer_type: Literal["text", "yes_no", "scale", "multi_select"]
    why_asked: str
    options: list[str] | None = None  # For multi_select type


@dataclass
class QuestionnaireAnswer:
    """User's answer to a questionnaire question."""

    question_id: str
    answer: str | list[str]  # str for text/yes_no/scale, list for multi_select


# =============================================================================
# CV Generation Structures
# =============================================================================


@dataclass
class CVBullet:
    """A bullet point in the generated CV."""

    text: str
    confidence_score: ConfidenceScore
    source_ref: str | None = None  # Reference to original CV bullet or question ID
    needs_verification: bool = False


@dataclass
class DeltaInstruction:
    """Instruction for modifying a CV bullet."""

    bullet_id: str
    action: DeltaAction
    original_text: str | None = None
    new_text: str | None = None
    confidence_score: ConfidenceScore = ConfidenceScore.HIGH
    reason: str | None = None


@dataclass
class TailoredCV:
    """Generated tailored CV content."""

    targeted_title: str
    summary: str
    skills: list[str] = field(default_factory=list)
    experience_bullets: dict[str, list[CVBullet]] = field(default_factory=dict)  # company -> bullets
    projects: list[CVBullet] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    truth_notes: list[str] = field(default_factory=list)  # What was intentionally NOT claimed


# =============================================================================
# Interview Prep Structures
# =============================================================================


@dataclass
class STARStory:
    """STAR format story for behavioral questions."""

    title: str
    situation: str
    task: str
    action: str
    result: str
    applicable_to: list[str] = field(default_factory=list)  # Question types this applies to


@dataclass
class InterviewQuestion:
    """Expected interview question with suggested answer."""

    question: str
    category: str  # "behavioral", "technical", "situational"
    difficulty: Literal["easy", "medium", "hard"]
    suggested_answer: str | None = None


@dataclass
class PrepPlanDay:
    """Single day in the 7-day prep plan."""

    day: int
    focus: str
    tasks: list[str] = field(default_factory=list)
    time_estimate_minutes: int = 60


@dataclass
class InterviewPrep:
    """Interview preparation kit."""

    role_understanding: str
    likely_questions: list[InterviewQuestion] = field(default_factory=list)
    suggested_answers: dict[str, str] = field(default_factory=dict)  # question -> answer
    story_bank: list[STARStory] = field(default_factory=list)
    tech_deep_dive_topics: list[str] = field(default_factory=list)
    seven_day_prep_plan: list[PrepPlanDay] = field(default_factory=list)


# =============================================================================
# Session Entity
# =============================================================================


@dataclass
class ResumeSource:
    """Resume source specification."""

    source_type: Literal["uploaded", "draft"]
    resume_id: str


@dataclass
class CareerKitSession:
    """CareerKit Expert Apply session entity."""

    id: str
    user_id: str
    session_name: str
    phase: CareerKitPhase
    resume_source: ResumeSource
    is_custom_job: bool = False

    # Job source (one of these)
    job_id: str | None = None
    custom_jd: CustomJD | None = None

    # Phase 1: Analysis
    requirements: list[Requirement] | None = None
    selected_bullets: list[str] | None = None  # Original CV bullets selected for context
    gap_map: list[GapMapItem] | None = None
    questionnaire: list[Question] | None = None
    answers: list[QuestionnaireAnswer] | None = None

    # Phase 2: Generation
    delta_instructions: list[DeltaInstruction] | None = None
    generated_cv: TailoredCV | None = None
    generated_cv_draft_id: str | None = None
    interview_prep: InterviewPrep | None = None

    # Metadata
    pipeline_messages: list[dict] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
