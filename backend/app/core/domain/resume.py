"""Resume domain model.

Standards: python_clean.mdc
- Dataclass for domain models
- Typed fields for parsed data
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


# ============================================================================
# URL Schema
# ============================================================================


@dataclass
class Url:
    """URL with optional label."""

    url: str = ""
    label: str = ""


# ============================================================================
# Picture Settings
# ============================================================================


@dataclass
class PictureSettings:
    """Profile picture display settings."""

    hidden: bool = False
    url: str = ""
    size: int = 80
    rotation: int = 0
    aspect_ratio: float = 1.0
    border_radius: int = 0
    border_color: str = "rgba(0, 0, 0, 0.5)"
    border_width: int = 0
    shadow_color: str = "rgba(0, 0, 0, 0.5)"
    shadow_width: int = 0


# ============================================================================
# Section Settings
# ============================================================================


@dataclass
class SectionSettings:
    """Common settings for all sections."""

    title: str = ""
    columns: int = 1
    hidden: bool = False


# ============================================================================
# Item Models (with full Reactive Resume fields)
# ============================================================================


@dataclass
class WorkExperience:
    """Work experience entry."""

    id: str = ""
    hidden: bool = False
    company: str = ""
    title: str = ""  # Maps to 'position' in Reactive Resume
    location: str = ""
    period: str = ""  # Original period string
    start_date: str | None = None  # Parsed for ATS
    end_date: str | None = None  # Parsed for ATS
    is_current: bool = False  # Parsed for ATS
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content - preserved as-is
    achievements: list[str] = field(default_factory=list)  # Key achievements/bullet points


@dataclass
class Education:
    """Education entry."""

    id: str = ""
    hidden: bool = False
    school: str = ""  # Maps to 'institution' for ATS
    institution: str = ""  # ATS-compatible field name
    degree: str = ""
    area: str = ""  # Maps to 'field_of_study' for ATS
    field_of_study: str | None = None  # ATS-compatible field name
    grade: str = ""  # Kept as string
    gpa: str | None = None  # ATS-compatible field name
    location: str = ""
    period: str = ""  # Original period string
    graduation_date: str | None = None  # ATS-compatible field name
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content - preserved as-is


@dataclass
class SkillItem:
    """Individual skill item."""

    id: str = ""
    hidden: bool = False
    icon: str = ""
    name: str = ""
    proficiency: str = ""  # e.g., "Expert", "Advanced", "Intermediate"
    level: int = 0  # 0-5 for visual indicator
    keywords: list[str] = field(default_factory=list)


@dataclass
class Project:
    """Project entry."""

    id: str = ""
    hidden: bool = False
    name: str = ""
    period: str = ""  # Original period string
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content - preserved as-is
    technologies: list[str] = field(default_factory=list)


@dataclass
class Award:
    """Award entry."""

    id: str = ""
    hidden: bool = False
    title: str = ""
    awarder: str = ""  # Maps to 'issuer' for ATS
    date: str = ""
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content - preserved as-is


@dataclass
class Certification:
    """Certification entry."""

    id: str = ""
    hidden: bool = False
    title: str = ""  # Maps to 'name' for ATS
    issuer: str = ""
    date: str = ""
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content - preserved as-is
    expiry_date: str | None = None
    credential_id: str | None = None


@dataclass
class LanguageSkill:
    """Language skill."""

    id: str = ""
    hidden: bool = False
    language: str = ""
    fluency: str = ""  # Free text: "Native", "Fluent", etc.
    level: int = 0  # 0-5 for visual indicator


@dataclass
class ProfileItem:
    """Social profile item."""

    id: str = ""
    hidden: bool = False
    icon: str = ""
    network: str = ""
    username: str = ""
    website: Url = field(default_factory=Url)


@dataclass
class InterestItem:
    """Interest/hobby item."""

    id: str = ""
    hidden: bool = False
    icon: str = ""
    name: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class Volunteer:
    """Volunteer experience."""

    id: str = ""
    hidden: bool = False
    organization: str = ""
    location: str = ""
    period: str = ""
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content


@dataclass
class Publication:
    """Publication entry."""

    id: str = ""
    hidden: bool = False
    title: str = ""
    publisher: str = ""
    date: str = ""
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content


@dataclass
class Reference:
    """Reference entry."""

    id: str = ""
    hidden: bool = False
    name: str = ""
    position: str = ""
    phone: str = ""
    website: Url = field(default_factory=Url)
    description: str = ""  # HTML content (quote/testimonial)


@dataclass
class CustomSectionItem:
    """Custom section item - flexible structure."""

    id: str = ""
    hidden: bool = False
    # Common fields that may appear based on section type
    name: str = ""
    title: str = ""
    company: str = ""
    school: str = ""
    organization: str = ""
    position: str = ""
    location: str = ""
    period: str = ""
    date: str = ""
    website: Url = field(default_factory=Url)
    description: str = ""
    content: str = ""
    icon: str = ""
    keywords: list[str] = field(default_factory=list)
    proficiency: str = ""
    level: int = 0
    fluency: str = ""
    language: str = ""
    awarder: str = ""
    issuer: str = ""
    publisher: str = ""
    phone: str = ""
    network: str = ""
    username: str = ""
    recipient: str = ""  # For cover letter


@dataclass
class CustomSection:
    """Custom section."""

    id: str = ""
    title: str = ""
    type: str = "experience"  # Section type determines item structure
    columns: int = 1
    hidden: bool = False
    items: list[CustomSectionItem] = field(default_factory=list)


@dataclass
class CustomLink:
    """Custom link/field."""

    id: str = ""
    icon: str = ""
    text: str = ""  # Label
    link: str = ""  # URL


# ============================================================================
# Metadata Models
# ============================================================================


@dataclass
class PageLayout:
    """Single page layout configuration."""

    full_width: bool = False
    main: list[str] = field(default_factory=list)
    sidebar: list[str] = field(default_factory=list)


@dataclass
class Layout:
    """Resume layout configuration."""

    sidebar_width: int = 35
    pages: list[PageLayout] = field(default_factory=list)


@dataclass
class Css:
    """Custom CSS configuration."""

    enabled: bool = False
    value: str = ""


@dataclass
class Page:
    """Page settings configuration."""

    gap_x: int = 4
    gap_y: int = 6
    margin_x: int = 14
    margin_y: int = 12
    format: str = "a4"  # "a4", "letter", "free-form"
    locale: str = "en-US"
    hide_icons: bool = False


@dataclass
class LevelDesign:
    """Level indicator design settings."""

    icon: str = "star"
    type: str = "circle"  # "hidden", "circle", "square", etc.


@dataclass
class ColorDesign:
    """Color scheme settings."""

    primary: str = "rgba(220, 38, 38, 1)"
    text: str = "rgba(0, 0, 0, 1)"
    background: str = "rgba(255, 255, 255, 1)"


@dataclass
class Design:
    """Overall design settings."""

    level: LevelDesign = field(default_factory=LevelDesign)
    colors: ColorDesign = field(default_factory=ColorDesign)


@dataclass
class TypographyItem:
    """Typography settings for body or heading."""

    font_family: str = "IBM Plex Serif"
    font_weights: list[str] = field(default_factory=lambda: ["400", "500"])
    font_size: int = 10
    line_height: float = 1.5


@dataclass
class Typography:
    """Typography configuration."""

    body: TypographyItem = field(default_factory=TypographyItem)
    heading: TypographyItem = field(default_factory=lambda: TypographyItem(
        font_family="IBM Plex Serif",
        font_weights=["600"],
        font_size=14,
        line_height=1.5,
    ))


@dataclass
class Metadata:
    """Resume metadata configuration."""

    template: str = "onyx"
    layout: Layout = field(default_factory=Layout)
    css: Css = field(default_factory=Css)
    page: Page = field(default_factory=Page)
    design: Design = field(default_factory=Design)
    typography: Typography = field(default_factory=Typography)
    notes: str = ""


# ============================================================================
# Section Models
# ============================================================================


@dataclass
class ProfilesSection(SectionSettings):
    """Profiles section with items."""

    items: list[ProfileItem] = field(default_factory=list)


@dataclass
class ExperienceSection(SectionSettings):
    """Experience section with items."""

    items: list[WorkExperience] = field(default_factory=list)


@dataclass
class EducationSection(SectionSettings):
    """Education section with items."""

    items: list[Education] = field(default_factory=list)


@dataclass
class SkillsSection(SectionSettings):
    """Skills section with items."""

    items: list[SkillItem] = field(default_factory=list)


@dataclass
class ProjectsSection(SectionSettings):
    """Projects section with items."""

    items: list[Project] = field(default_factory=list)


@dataclass
class AwardsSection(SectionSettings):
    """Awards section with items."""

    items: list[Award] = field(default_factory=list)


@dataclass
class CertificationsSection(SectionSettings):
    """Certifications section with items."""

    items: list[Certification] = field(default_factory=list)


@dataclass
class LanguagesSection(SectionSettings):
    """Languages section with items."""

    items: list[LanguageSkill] = field(default_factory=list)


@dataclass
class InterestsSection(SectionSettings):
    """Interests section with items."""

    items: list[InterestItem] = field(default_factory=list)


@dataclass
class VolunteerSection(SectionSettings):
    """Volunteer section with items."""

    items: list[Volunteer] = field(default_factory=list)


@dataclass
class PublicationsSection(SectionSettings):
    """Publications section with items."""

    items: list[Publication] = field(default_factory=list)


@dataclass
class ReferencesSection(SectionSettings):
    """References section with items."""

    items: list[Reference] = field(default_factory=list)


@dataclass
class Sections:
    """All resume sections."""

    profiles: ProfilesSection = field(default_factory=ProfilesSection)
    experience: ExperienceSection = field(default_factory=ExperienceSection)
    education: EducationSection = field(default_factory=EducationSection)
    skills: SkillsSection = field(default_factory=SkillsSection)
    projects: ProjectsSection = field(default_factory=ProjectsSection)
    awards: AwardsSection = field(default_factory=AwardsSection)
    certifications: CertificationsSection = field(default_factory=CertificationsSection)
    languages: LanguagesSection = field(default_factory=LanguagesSection)
    interests: InterestsSection = field(default_factory=InterestsSection)
    volunteer: VolunteerSection = field(default_factory=VolunteerSection)
    publications: PublicationsSection = field(default_factory=PublicationsSection)
    references: ReferencesSection = field(default_factory=ReferencesSection)


# ============================================================================
# Summary Model
# ============================================================================


@dataclass
class Summary:
    """Summary/objective section."""

    title: str = ""
    columns: int = 1
    hidden: bool = False
    content: str = ""  # HTML content


# ============================================================================
# Basics Model
# ============================================================================


@dataclass
class Basics:
    """Basic contact information."""

    name: str = ""
    headline: str = ""  # Professional tagline
    email: str = ""
    phone: str = ""
    location: str = ""
    website: Url = field(default_factory=Url)
    custom_fields: list[CustomLink] = field(default_factory=list)


# ============================================================================
# Resume Content (Full Reactive Resume Structure)
# ============================================================================


@dataclass
class ResumeContent:
    """Complete resume content - mirrors Reactive Resume's ResumeData."""

    # Picture settings
    picture: PictureSettings = field(default_factory=PictureSettings)

    # Basic information
    basics: Basics = field(default_factory=Basics)

    # Summary section
    summary: Summary = field(default_factory=Summary)

    # All standard sections
    sections: Sections = field(default_factory=Sections)

    # Custom sections
    custom_sections: list[CustomSection] = field(default_factory=list)

    # Metadata (layout, design, typography)
    metadata: Metadata = field(default_factory=Metadata)


# ============================================================================
# Resume Draft Entity
# ============================================================================


@dataclass
class ResumeDraft:
    """Resume draft entity for the builder with autosave."""

    id: str
    user_id: str
    name: str
    content: ResumeContent
    template_id: str = "onyx"
    ats_score: int | None = None
    is_published: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None


# ============================================================================
# ATS Score Result
# ============================================================================


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


# ============================================================================
# Legacy Models (for backward compatibility with parsing)
# ============================================================================


@dataclass
class ParsedResume:
    """Structured data extracted from resume (legacy parser format)."""

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
        # Create basics
        basics = Basics(
            name=self.full_name or "",
            email=self.email or "",
            phone=self.phone or "",
            location=self.location or "",
        )

        # Create summary
        summary = Summary(content=self.summary or "")

        # Create sections
        sections = Sections(
            experience=ExperienceSection(items=self.work_experience.copy()),
            education=EducationSection(items=self.education.copy()),
            skills=SkillsSection(items=[
                SkillItem(name=skill) for skill in self.skills
            ]),
            certifications=CertificationsSection(items=[
                Certification(title=cert) for cert in self.certifications
            ]),
            languages=LanguagesSection(items=[
                LanguageSkill(language=lang) for lang in self.languages
            ]),
        )

        return ResumeContent(
            basics=basics,
            summary=summary,
            sections=sections,
        )


@dataclass
class Resume:
    """Resume domain entity (for uploaded resume files)."""

    id: str
    user_id: str
    filename: str
    s3_key: str
    raw_text: str | None = None
    parsed_data: ParsedResume | None = None
    embedding: list[float] | None = None
    is_primary: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
