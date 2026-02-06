"""Resume builder schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================================
# URL Schema (matches Reactive Resume's urlSchema)
# ============================================================================


class UrlSchema(BaseModel):
    """URL with optional label."""

    url: str = ""
    label: str = ""


# ============================================================================
# Picture Settings Schema
# ============================================================================


class PictureSettingsSchema(BaseModel):
    """Profile picture display settings."""

    hidden: bool = False
    url: str = ""
    size: int = 80
    rotation: int = 0
    aspect_ratio: float = Field(default=1.0, alias="aspectRatio")
    border_radius: int = Field(default=0, alias="borderRadius")
    border_color: str = Field(default="rgba(0, 0, 0, 0.5)", alias="borderColor")
    border_width: int = Field(default=0, alias="borderWidth")
    shadow_color: str = Field(default="rgba(0, 0, 0, 0.5)", alias="shadowColor")
    shadow_width: int = Field(default=0, alias="shadowWidth")

    class Config:
        populate_by_name = True


# ============================================================================
# Section Settings Schema
# ============================================================================


class SectionSettingsSchema(BaseModel):
    """Common settings for all sections."""

    title: str = ""
    columns: int = 1
    hidden: bool = False


# ============================================================================
# Sub-schemas for resume content (with full Reactive Resume fields)
# ============================================================================


class WorkExperienceSchema(BaseModel):
    """Work experience entry schema."""

    id: str = ""
    hidden: bool = False
    company: str = ""
    title: str = ""  # Maps to 'position' in Reactive Resume
    location: str = ""
    period: str = ""  # Original period string
    start_date: str | None = None  # Parsed for ATS
    end_date: str | None = None  # Parsed for ATS
    is_current: bool = False  # Parsed for ATS
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content - preserved as-is


class EducationSchema(BaseModel):
    """Education entry schema."""

    id: str = ""
    hidden: bool = False
    school: str = ""  # Maps to 'institution' for ATS
    degree: str = ""
    area: str = ""  # Maps to 'field_of_study' for ATS
    grade: str = ""  # Kept as string, maps to 'gpa' for ATS
    location: str = ""
    period: str = ""  # Original period string
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content - preserved as-is


class SkillItemSchema(BaseModel):
    """Individual skill item schema."""

    id: str = ""
    hidden: bool = False
    icon: str = ""
    name: str = ""
    proficiency: str = ""  # e.g., "Expert", "Advanced", "Intermediate"
    level: int = 0  # 0-5 for visual indicator
    keywords: list[str] = Field(default_factory=list)


class ProjectSchema(BaseModel):
    """Project entry schema."""

    id: str = ""
    hidden: bool = False
    name: str = ""
    period: str = ""  # Original period string
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content - preserved as-is
    # Additional fields for ATS extraction
    technologies: list[str] = Field(default_factory=list)


class AwardSchema(BaseModel):
    """Award entry schema."""

    id: str = ""
    hidden: bool = False
    title: str = ""
    awarder: str = ""  # Maps to 'issuer' for ATS
    date: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content - preserved as-is


class CertificationSchema(BaseModel):
    """Certification entry schema."""

    id: str = ""
    hidden: bool = False
    title: str = ""  # Maps to 'name' for ATS
    issuer: str = ""
    date: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content - preserved as-is
    # Additional fields for ATS
    expiry_date: str | None = None
    credential_id: str | None = None


class LanguageSkillSchema(BaseModel):
    """Language skill schema."""

    id: str = ""
    hidden: bool = False
    language: str = ""
    fluency: str = ""  # Free text: "Native", "Fluent", etc.
    level: int = 0  # 0-5 for visual indicator


class ProfileItemSchema(BaseModel):
    """Social profile item schema."""

    id: str = ""
    hidden: bool = False
    icon: str = ""
    network: str = ""
    username: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)


class InterestItemSchema(BaseModel):
    """Interest/hobby item schema."""

    id: str = ""
    hidden: bool = False
    icon: str = ""
    name: str = ""
    keywords: list[str] = Field(default_factory=list)


class VolunteerSchema(BaseModel):
    """Volunteer experience schema."""

    id: str = ""
    hidden: bool = False
    organization: str = ""
    location: str = ""
    period: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content


class PublicationSchema(BaseModel):
    """Publication entry schema."""

    id: str = ""
    hidden: bool = False
    title: str = ""
    publisher: str = ""
    date: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content


class ReferenceSchema(BaseModel):
    """Reference entry schema."""

    id: str = ""
    hidden: bool = False
    name: str = ""
    position: str = ""
    phone: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""  # HTML content (quote/testimonial)


class CustomSectionItemSchema(BaseModel):
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
    website: UrlSchema = Field(default_factory=UrlSchema)
    description: str = ""
    content: str = ""
    icon: str = ""
    keywords: list[str] = Field(default_factory=list)
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


class CustomSectionSchema(BaseModel):
    """Custom section schema."""

    id: str = ""
    title: str = ""
    type: str = "experience"  # Section type determines item structure
    columns: int = 1
    hidden: bool = False
    items: list[CustomSectionItemSchema] = Field(default_factory=list)


class CustomLinkSchema(BaseModel):
    """Custom link/field schema."""

    id: str = ""
    icon: str = ""
    text: str = ""  # Label
    link: str = ""  # URL


# ============================================================================
# Metadata Schemas (Layout, Design, Typography)
# ============================================================================


class PageLayoutSchema(BaseModel):
    """Single page layout configuration."""

    full_width: bool = Field(default=False, alias="fullWidth")
    main: list[str] = Field(default_factory=list)
    sidebar: list[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class LayoutSchema(BaseModel):
    """Resume layout configuration."""

    sidebar_width: int = Field(default=35, alias="sidebarWidth")
    pages: list[PageLayoutSchema] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class CssSchema(BaseModel):
    """Custom CSS configuration."""

    enabled: bool = False
    value: str = ""


class PageSchema(BaseModel):
    """Page settings configuration."""

    gap_x: int = Field(default=4, alias="gapX")
    gap_y: int = Field(default=6, alias="gapY")
    margin_x: int = Field(default=14, alias="marginX")
    margin_y: int = Field(default=12, alias="marginY")
    format: Literal["a4", "letter", "free-form"] = "a4"
    locale: str = "en-US"
    hide_icons: bool = Field(default=False, alias="hideIcons")

    class Config:
        populate_by_name = True


class LevelDesignSchema(BaseModel):
    """Level indicator design settings."""

    icon: str = "star"
    type: Literal["hidden", "circle", "square", "rectangle", "rectangle-full", "progress-bar", "icon"] = "circle"


class ColorDesignSchema(BaseModel):
    """Color scheme settings."""

    primary: str = "rgba(220, 38, 38, 1)"
    text: str = "rgba(0, 0, 0, 1)"
    background: str = "rgba(255, 255, 255, 1)"


class DesignSchema(BaseModel):
    """Overall design settings."""

    level: LevelDesignSchema = Field(default_factory=LevelDesignSchema)
    colors: ColorDesignSchema = Field(default_factory=ColorDesignSchema)


class TypographyItemSchema(BaseModel):
    """Typography settings for body or heading."""

    font_family: str = Field(default="IBM Plex Serif", alias="fontFamily")
    font_weights: list[str] = Field(default_factory=lambda: ["400", "500"], alias="fontWeights")
    font_size: int = Field(default=10, alias="fontSize")
    line_height: float = Field(default=1.5, alias="lineHeight")

    class Config:
        populate_by_name = True


class TypographySchema(BaseModel):
    """Typography configuration."""

    body: TypographyItemSchema = Field(default_factory=TypographyItemSchema)
    heading: TypographyItemSchema = Field(
        default_factory=lambda: TypographyItemSchema.model_validate({
            "font_family": "IBM Plex Serif",
            "font_weights": ["600"],
            "font_size": 14,
            "line_height": 1.5,
        })
    )


class MetadataSchema(BaseModel):
    """Resume metadata configuration."""

    template: str = "onyx"
    layout: LayoutSchema = Field(default_factory=LayoutSchema)
    css: CssSchema = Field(default_factory=CssSchema)
    page: PageSchema = Field(default_factory=PageSchema)
    design: DesignSchema = Field(default_factory=DesignSchema)
    typography: TypographySchema = Field(default_factory=TypographySchema)
    notes: str = ""


# ============================================================================
# Section Schemas (with items and settings)
# ============================================================================


class ProfilesSectionSchema(SectionSettingsSchema):
    """Profiles section with items."""

    items: list[ProfileItemSchema] = Field(default_factory=list)


class ExperienceSectionSchema(SectionSettingsSchema):
    """Experience section with items."""

    items: list[WorkExperienceSchema] = Field(default_factory=list)


class EducationSectionSchema(SectionSettingsSchema):
    """Education section with items."""

    items: list[EducationSchema] = Field(default_factory=list)


class SkillsSectionSchema(SectionSettingsSchema):
    """Skills section with items."""

    items: list[SkillItemSchema] = Field(default_factory=list)


class ProjectsSectionSchema(SectionSettingsSchema):
    """Projects section with items."""

    items: list[ProjectSchema] = Field(default_factory=list)


class AwardsSectionSchema(SectionSettingsSchema):
    """Awards section with items."""

    items: list[AwardSchema] = Field(default_factory=list)


class CertificationsSectionSchema(SectionSettingsSchema):
    """Certifications section with items."""

    items: list[CertificationSchema] = Field(default_factory=list)


class LanguagesSectionSchema(SectionSettingsSchema):
    """Languages section with items."""

    items: list[LanguageSkillSchema] = Field(default_factory=list)


class InterestsSectionSchema(SectionSettingsSchema):
    """Interests section with items."""

    items: list[InterestItemSchema] = Field(default_factory=list)


class VolunteerSectionSchema(SectionSettingsSchema):
    """Volunteer section with items."""

    items: list[VolunteerSchema] = Field(default_factory=list)


class PublicationsSectionSchema(SectionSettingsSchema):
    """Publications section with items."""

    items: list[PublicationSchema] = Field(default_factory=list)


class ReferencesSectionSchema(SectionSettingsSchema):
    """References section with items."""

    items: list[ReferenceSchema] = Field(default_factory=list)


class SectionsSchema(BaseModel):
    """All resume sections."""

    profiles: ProfilesSectionSchema = Field(default_factory=ProfilesSectionSchema)
    experience: ExperienceSectionSchema = Field(default_factory=ExperienceSectionSchema)
    education: EducationSectionSchema = Field(default_factory=EducationSectionSchema)
    skills: SkillsSectionSchema = Field(default_factory=SkillsSectionSchema)
    projects: ProjectsSectionSchema = Field(default_factory=ProjectsSectionSchema)
    awards: AwardsSectionSchema = Field(default_factory=AwardsSectionSchema)
    certifications: CertificationsSectionSchema = Field(default_factory=CertificationsSectionSchema)
    languages: LanguagesSectionSchema = Field(default_factory=LanguagesSectionSchema)
    interests: InterestsSectionSchema = Field(default_factory=InterestsSectionSchema)
    volunteer: VolunteerSectionSchema = Field(default_factory=VolunteerSectionSchema)
    publications: PublicationsSectionSchema = Field(default_factory=PublicationsSectionSchema)
    references: ReferencesSectionSchema = Field(default_factory=ReferencesSectionSchema)


# ============================================================================
# Summary Schema
# ============================================================================


class SummarySchema(BaseModel):
    """Summary/objective section."""

    title: str = ""
    columns: int = 1
    hidden: bool = False
    content: str = ""  # HTML content


# ============================================================================
# Basics Schema
# ============================================================================


class BasicsSchema(BaseModel):
    """Basic contact information."""

    name: str = ""
    headline: str = ""  # Professional tagline
    email: str = ""
    phone: str = ""
    location: str = ""
    website: UrlSchema = Field(default_factory=UrlSchema)
    custom_fields: list[CustomLinkSchema] = Field(default_factory=list, alias="customFields")

    class Config:
        populate_by_name = True


# ============================================================================
# Resume Content Schema (Full Reactive Resume Structure)
# ============================================================================


class ResumeContentSchema(BaseModel):
    """Complete resume content schema - mirrors Reactive Resume's ResumeData."""

    # Picture settings
    picture: PictureSettingsSchema = Field(default_factory=PictureSettingsSchema)

    # Basic information
    basics: BasicsSchema = Field(default_factory=BasicsSchema)

    # Summary section
    summary: SummarySchema = Field(default_factory=SummarySchema)

    # All standard sections
    sections: SectionsSchema = Field(default_factory=SectionsSchema)

    # Custom sections
    custom_sections: list[CustomSectionSchema] = Field(default_factory=list, alias="customSections")

    # Metadata (layout, design, typography)
    metadata: MetadataSchema = Field(default_factory=MetadataSchema)

    class Config:
        populate_by_name = True


# ============================================================================
# Legacy Schema for ATS Analysis (extracted from ResumeContentSchema)
# ============================================================================


class ATSExtractedSchema(BaseModel):
    """Extracted fields for ATS analysis - computed from ResumeContentSchema."""

    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    professional_summary: str = ""
    skills_technical: list[str] = Field(default_factory=list)
    skills_soft: list[str] = Field(default_factory=list)
    skills_tools: list[str] = Field(default_factory=list)
    work_experience_count: int = 0
    education_count: int = 0
    has_certifications: bool = False
    has_projects: bool = False


# ============================================================================
# Draft CRUD Schemas
# ============================================================================


class DraftCreateRequest(BaseModel):
    """Request to create a new draft."""

    name: str = Field(..., max_length=255)
    content: ResumeContentSchema | None = None
    template_id: str = "onyx"


class DraftUpdateRequest(BaseModel):
    """Request to update a draft (autosave)."""

    name: str | None = Field(None, max_length=255)
    content: ResumeContentSchema | None = None
    template_id: str | None = None


class DraftResponse(BaseModel):
    """Draft response schema."""

    id: str
    name: str
    content: ResumeContentSchema
    template_id: str
    ats_score: int | None
    is_published: bool
    created_at: datetime
    updated_at: datetime | None


class DraftListResponse(BaseModel):
    """List of drafts response."""

    items: list[DraftResponse]
    total: int


# ============================================================================
# AI Feature Schemas (use legacy flat structure for compatibility)
# ============================================================================


class LegacySkillsSectionSchema(BaseModel):
    """Legacy skills section schema for AI features."""

    technical: list[str] = Field(default_factory=list)
    soft: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class LegacyWorkExperienceSchema(BaseModel):
    """Legacy work experience for AI features."""

    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    location: str | None = None
    is_current: bool = False


class GenerateSummaryRequest(BaseModel):
    """Request to generate AI summary."""

    work_experience: list[LegacyWorkExperienceSchema] = Field(default_factory=list)
    skills: LegacySkillsSectionSchema = Field(default_factory=LegacySkillsSectionSchema)
    target_role: str | None = None
    years_of_experience: float | None = None


class GenerateSummaryResponse(BaseModel):
    """AI summary generation response."""

    content: str
    model_used: str
    tokens_used: int


class EnhanceBulletRequest(BaseModel):
    """Request to enhance a bullet point."""

    original: str
    job_title: str | None = None
    company: str | None = None


class EnhanceBulletResponse(BaseModel):
    """Enhanced bullet point response."""

    original: str
    enhanced: str
    improvements: list[str]


class SuggestSkillsRequest(BaseModel):
    """Request to suggest skills."""

    job_title: str
    existing_skills: LegacySkillsSectionSchema = Field(default_factory=LegacySkillsSectionSchema)
    industry: str | None = None


class SuggestSkillsResponse(BaseModel):
    """Skill suggestions response."""

    technical: list[str]
    soft: list[str]
    tools: list[str]
    reasoning: str


class TailorForJobRequest(BaseModel):
    """Request to tailor resume for a job."""

    content: ResumeContentSchema
    job_id: str


class TailorForJobResponse(BaseModel):
    """Tailored resume response."""

    content: ResumeContentSchema
    changes_made: list[str]
    keyword_matches: list[str]
    suggestions: list[str]


# ============================================================================
# ATS Scoring Schemas
# ============================================================================


class ATSScoreRequest(BaseModel):
    """Request to calculate ATS score."""

    content: ResumeContentSchema
    job_description: str | None = None


class ATSScoreResponse(BaseModel):
    """ATS score calculation response."""

    total_score: int
    keyword_match_score: int
    formatting_score: int
    section_completeness_score: int
    quantified_achievements_score: int
    length_score: int
    contact_info_score: int
    suggestions: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]


# ============================================================================
# Template Schemas
# ============================================================================


class TemplateSchema(BaseModel):
    """Resume template schema."""

    id: str
    name: str
    description: str
    ats_score: int


class TemplateListResponse(BaseModel):
    """List of templates response."""

    templates: list[TemplateSchema]


# ============================================================================
# Profile Picture Schemas
# ============================================================================


class ProfilePictureResponse(BaseModel):
    """Response after uploading a profile picture."""

    url: str
    filename: str
