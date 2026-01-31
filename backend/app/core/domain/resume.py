"""Resume domain model.

Standards: python_clean.mdc
- Dataclass for domain models
- Typed fields for parsed data
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class LanguageProficiency(str, Enum):
    """Language proficiency levels."""

    NATIVE = "native"
    FLUENT = "fluent"
    CONVERSATIONAL = "conversational"
    BASIC = "basic"


@dataclass
class WorkExperience:
    """Parsed work experience entry."""

    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = field(default_factory=list)
    location: str | None = None
    is_current: bool = False


@dataclass
class Education:
    """Parsed education entry."""

    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_date: str | None = None
    gpa: float | None = None
    location: str | None = None
    achievements: list[str] = field(default_factory=list)


@dataclass
class Project:
    """Project entry for resume builder."""

    name: str
    description: str
    url: str | None = None
    technologies: list[str] = field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None
    highlights: list[str] = field(default_factory=list)


@dataclass
class Award:
    """Award or achievement entry."""

    title: str
    issuer: str
    date: str | None = None
    description: str | None = None


@dataclass
class Certification:
    """Certification entry with more details than simple string."""

    name: str
    issuer: str
    date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None
    url: str | None = None


@dataclass
class LanguageSkill:
    """Language skill with proficiency level."""

    language: str
    proficiency: LanguageProficiency = LanguageProficiency.CONVERSATIONAL


@dataclass
class SkillsSection:
    """Categorized skills section."""

    technical: list[str] = field(default_factory=list)
    soft: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


@dataclass
class CustomSection:
    """User-defined custom section."""

    id: str
    title: str
    items: list[str] = field(default_factory=list)


# Default section order for resume builder
DEFAULT_SECTION_ORDER: list[str] = [
    "contact",
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "awards",
    "languages",
]


@dataclass
class ResumeContent:
    """Complete resume content for the builder.

    This is the main data structure for the resume builder,
    containing all sections and metadata.
    """

    # Contact Information
    full_name: str = ""
    email: str = ""
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None

    # Professional Summary
    professional_summary: str | None = None

    # Main Sections
    work_experience: list[WorkExperience] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    skills: SkillsSection = field(default_factory=SkillsSection)
    projects: list[Project] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    awards: list[Award] = field(default_factory=list)
    languages: list[LanguageSkill] = field(default_factory=list)
    custom_sections: list[CustomSection] = field(default_factory=list)

    # Metadata
    template_id: str = "professional-modern"
    section_order: list[str] = field(default_factory=lambda: DEFAULT_SECTION_ORDER.copy())
    ats_score: int | None = None


@dataclass
class ATSScoreResult:
    """Result of ATS score calculation."""

    total_score: int
    keyword_match_score: int
    formatting_score: int
    section_completeness_score: int
    quantified_achievements_score: int
    length_score: int
    contact_info_score: int
    suggestions: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)


@dataclass
class Improvement:
    """Suggested improvement for resume content."""

    section: str
    suggestion: str
    priority: Literal["high", "medium", "low"] = "medium"


@dataclass
class ParsedResume:
    """Structured data extracted from resume."""

    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = field(default_factory=list)
    work_experience: list[WorkExperience] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    total_years_experience: float | None = None

    def to_resume_content(self) -> ResumeContent:
        """Convert parsed resume to ResumeContent for builder."""
        # Convert simple certification strings to Certification objects
        certs = [Certification(name=c, issuer="") for c in self.certifications]

        # Convert simple language strings to LanguageSkill objects
        langs = [LanguageSkill(language=lang) for lang in self.languages]

        # Flatten skills into technical category
        skills_section = SkillsSection(technical=self.skills.copy())

        return ResumeContent(
            full_name=self.full_name or "",
            email=self.email or "",
            phone=self.phone,
            location=self.location,
            professional_summary=self.summary,
            work_experience=self.work_experience.copy(),
            education=self.education.copy(),
            skills=skills_section,
            certifications=certs,
            languages=langs,
        )


@dataclass
class Resume:
    """Resume domain entity."""

    id: str
    user_id: str
    filename: str
    s3_key: str
    raw_text: str | None = None
    parsed_data: ParsedResume | None = None
    embedding: list[float] | None = None
    is_primary: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResumeDraft:
    """Resume draft entity for the builder with autosave."""

    id: str
    user_id: str
    name: str
    content: ResumeContent
    template_id: str = "professional-modern"
    ats_score: int | None = None
    is_published: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
