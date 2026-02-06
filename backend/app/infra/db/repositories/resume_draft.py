"""Resume draft repository implementation."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.resume import (
    Award,
    AwardsSection,
    Basics,
    Certification,
    CertificationsSection,
    ColorDesign,
    Css,
    CustomLink,
    CustomSection,
    CustomSectionItem,
    Design,
    Education,
    EducationSection,
    ExperienceSection,
    InterestItem,
    InterestsSection,
    LanguageSkill,
    LanguagesSection,
    Layout,
    LevelDesign,
    Metadata,
    Page,
    PageLayout,
    PictureSettings,
    ProfileItem,
    ProfilesSection,
    Project,
    ProjectsSection,
    Publication,
    PublicationsSection,
    Reference,
    ReferencesSection,
    ResumeContent,
    ResumeDraft,
    Sections,
    SkillItem,
    SkillsSection,
    Summary,
    Typography,
    TypographyItem,
    Url,
    Volunteer,
    VolunteerSection,
    WorkExperience,
)
from app.infra.db.models import ResumeDraftModel


class SQLResumeDraftRepository:
    """SQLAlchemy implementation of ResumeDraftRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, draft_id: str) -> ResumeDraft | None:
        """Get draft by ID."""
        result = await self._session.get(ResumeDraftModel, draft_id)
        return self._to_domain(result) if result else None

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        include_published: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResumeDraft]:
        """Get all drafts for a user."""
        stmt = select(ResumeDraftModel).where(ResumeDraftModel.user_id == user_id)

        if not include_published:
            stmt = stmt.where(ResumeDraftModel.is_published == False)  # noqa: E712

        stmt = stmt.order_by(ResumeDraftModel.updated_at.desc().nulls_last())
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, draft: ResumeDraft) -> ResumeDraft:
        """Create a new draft."""
        model = ResumeDraftModel(
            id=draft.id,
            user_id=draft.user_id,
            name=draft.name,
            content=self._content_to_dict(draft.content),
            template_id=draft.template_id,
            ats_score=draft.ats_score,
            is_published=draft.is_published,
            created_at=draft.created_at,
            updated_at=draft.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, draft: ResumeDraft) -> ResumeDraft:
        """Update an existing draft (autosave)."""
        model = await self._session.get(ResumeDraftModel, draft.id)
        if model:
            model.name = draft.name
            model.content = self._content_to_dict(draft.content)
            model.template_id = draft.template_id
            model.ats_score = draft.ats_score
            model.is_published = draft.is_published
            model.updated_at = datetime.utcnow()
            await self._session.flush()
            return self._to_domain(model)
        raise ValueError(f"Resume draft {draft.id} not found")

    async def delete(self, draft_id: str) -> None:
        """Delete a draft."""
        model = await self._session.get(ResumeDraftModel, draft_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def count_by_user_id(self, user_id: str) -> int:
        """Count drafts for a user."""
        stmt = select(func.count()).select_from(ResumeDraftModel).where(
            ResumeDraftModel.user_id == user_id,
            ResumeDraftModel.is_published == False,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    def _to_domain(self, model: ResumeDraftModel) -> ResumeDraft:
        """Convert ORM model to domain entity."""
        content = self._dict_to_content(model.content)
        return ResumeDraft(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            content=content,
            template_id=model.template_id,
            ats_score=model.ats_score,
            is_published=model.is_published,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # =========================================================================
    # Serialization: Domain -> Dict (for JSON storage)
    # =========================================================================

    def _url_to_dict(self, url: Url) -> dict:
        """Convert Url to dict."""
        return {"url": url.url, "label": url.label}

    def _content_to_dict(self, content: ResumeContent) -> dict:
        """Convert ResumeContent to dict for JSON storage."""
        return {
            "picture": self._picture_to_dict(content.picture),
            "basics": self._basics_to_dict(content.basics),
            "summary": self._summary_to_dict(content.summary),
            "sections": self._sections_to_dict(content.sections),
            "customSections": [self._custom_section_to_dict(cs) for cs in content.custom_sections],
            "metadata": self._metadata_to_dict(content.metadata),
        }

    def _picture_to_dict(self, picture: PictureSettings) -> dict:
        """Convert PictureSettings to dict."""
        return {
            "hidden": picture.hidden,
            "url": picture.url,
            "size": picture.size,
            "rotation": picture.rotation,
            "aspectRatio": picture.aspect_ratio,
            "borderRadius": picture.border_radius,
            "borderColor": picture.border_color,
            "borderWidth": picture.border_width,
            "shadowColor": picture.shadow_color,
            "shadowWidth": picture.shadow_width,
        }

    def _basics_to_dict(self, basics: Basics) -> dict:
        """Convert Basics to dict."""
        return {
            "name": basics.name,
            "headline": basics.headline,
            "email": basics.email,
            "phone": basics.phone,
            "location": basics.location,
            "website": self._url_to_dict(basics.website),
            "customFields": [
                {"id": cf.id, "icon": cf.icon, "text": cf.text, "link": cf.link}
                for cf in basics.custom_fields
            ],
        }

    def _summary_to_dict(self, summary: Summary) -> dict:
        """Convert Summary to dict."""
        return {
            "title": summary.title,
            "columns": summary.columns,
            "hidden": summary.hidden,
            "content": summary.content,
        }

    def _sections_to_dict(self, sections: Sections) -> dict:
        """Convert Sections to dict."""
        return {
            "profiles": self._section_to_dict(
                sections.profiles,
                lambda p: {
                    "id": p.id, "hidden": p.hidden, "icon": p.icon,
                    "network": p.network, "username": p.username,
                    "website": self._url_to_dict(p.website),
                },
            ),
            "experience": self._section_to_dict(
                sections.experience,
                lambda e: {
                    "id": e.id, "hidden": e.hidden, "company": e.company,
                    "position": e.title, "location": e.location, "period": e.period,
                    "website": self._url_to_dict(e.website), "description": e.description,
                },
            ),
            "education": self._section_to_dict(
                sections.education,
                lambda e: {
                    "id": e.id, "hidden": e.hidden, "school": e.school,
                    "degree": e.degree, "area": e.area, "grade": e.grade,
                    "location": e.location, "period": e.period,
                    "website": self._url_to_dict(e.website), "description": e.description,
                },
            ),
            "skills": self._section_to_dict(
                sections.skills,
                lambda s: {
                    "id": s.id, "hidden": s.hidden, "icon": s.icon,
                    "name": s.name, "proficiency": s.proficiency,
                    "level": s.level, "keywords": s.keywords,
                },
            ),
            "projects": self._section_to_dict(
                sections.projects,
                lambda p: {
                    "id": p.id, "hidden": p.hidden, "name": p.name,
                    "period": p.period, "website": self._url_to_dict(p.website),
                    "description": p.description,
                },
            ),
            "awards": self._section_to_dict(
                sections.awards,
                lambda a: {
                    "id": a.id, "hidden": a.hidden, "title": a.title,
                    "awarder": a.awarder, "date": a.date,
                    "website": self._url_to_dict(a.website), "description": a.description,
                },
            ),
            "certifications": self._section_to_dict(
                sections.certifications,
                lambda c: {
                    "id": c.id, "hidden": c.hidden, "title": c.title,
                    "issuer": c.issuer, "date": c.date,
                    "website": self._url_to_dict(c.website), "description": c.description,
                },
            ),
            "languages": self._section_to_dict(
                sections.languages,
                lambda l: {
                    "id": l.id, "hidden": l.hidden, "language": l.language,
                    "fluency": l.fluency, "level": l.level,
                },
            ),
            "interests": self._section_to_dict(
                sections.interests,
                lambda i: {
                    "id": i.id, "hidden": i.hidden, "icon": i.icon,
                    "name": i.name, "keywords": i.keywords,
                },
            ),
            "volunteer": self._section_to_dict(
                sections.volunteer,
                lambda v: {
                    "id": v.id, "hidden": v.hidden, "organization": v.organization,
                    "location": v.location, "period": v.period,
                    "website": self._url_to_dict(v.website), "description": v.description,
                },
            ),
            "publications": self._section_to_dict(
                sections.publications,
                lambda p: {
                    "id": p.id, "hidden": p.hidden, "title": p.title,
                    "publisher": p.publisher, "date": p.date,
                    "website": self._url_to_dict(p.website), "description": p.description,
                },
            ),
            "references": self._section_to_dict(
                sections.references,
                lambda r: {
                    "id": r.id, "hidden": r.hidden, "name": r.name,
                    "position": r.position, "phone": r.phone,
                    "website": self._url_to_dict(r.website), "description": r.description,
                },
            ),
        }

    def _section_to_dict(self, section: Any, item_converter: Any) -> dict:
        """Convert a section with items to dict."""
        return {
            "title": section.title,
            "columns": section.columns,
            "hidden": section.hidden,
            "items": [item_converter(item) for item in section.items],
        }

    def _custom_section_to_dict(self, section: CustomSection) -> dict:
        """Convert CustomSection to dict."""
        return {
            "id": section.id,
            "title": section.title,
            "type": section.type,
            "columns": section.columns,
            "hidden": section.hidden,
            "items": [self._custom_section_item_to_dict(item) for item in section.items],
        }

    def _custom_section_item_to_dict(self, item: CustomSectionItem) -> dict:
        """Convert CustomSectionItem to dict."""
        return {
            "id": item.id,
            "hidden": item.hidden,
            "name": item.name,
            "title": item.title,
            "company": item.company,
            "school": item.school,
            "organization": item.organization,
            "position": item.position,
            "location": item.location,
            "period": item.period,
            "date": item.date,
            "website": self._url_to_dict(item.website),
            "description": item.description,
            "content": item.content,
            "icon": item.icon,
            "keywords": item.keywords,
            "proficiency": item.proficiency,
            "level": item.level,
            "fluency": item.fluency,
            "language": item.language,
            "awarder": item.awarder,
            "issuer": item.issuer,
            "publisher": item.publisher,
            "phone": item.phone,
            "network": item.network,
            "username": item.username,
            "recipient": item.recipient,
        }

    def _metadata_to_dict(self, metadata: Metadata) -> dict:
        """Convert Metadata to dict."""
        return {
            "template": metadata.template,
            "layout": {
                "sidebarWidth": metadata.layout.sidebar_width,
                "pages": [
                    {"fullWidth": p.full_width, "main": p.main, "sidebar": p.sidebar}
                    for p in metadata.layout.pages
                ],
            },
            "css": {"enabled": metadata.css.enabled, "value": metadata.css.value},
            "page": {
                "gapX": metadata.page.gap_x,
                "gapY": metadata.page.gap_y,
                "marginX": metadata.page.margin_x,
                "marginY": metadata.page.margin_y,
                "format": metadata.page.format,
                "locale": metadata.page.locale,
                "hideIcons": metadata.page.hide_icons,
            },
            "design": {
                "level": {"icon": metadata.design.level.icon, "type": metadata.design.level.type},
                "colors": {
                    "primary": metadata.design.colors.primary,
                    "text": metadata.design.colors.text,
                    "background": metadata.design.colors.background,
                },
            },
            "typography": {
                "body": {
                    "fontFamily": metadata.typography.body.font_family,
                    "fontWeights": metadata.typography.body.font_weights,
                    "fontSize": metadata.typography.body.font_size,
                    "lineHeight": metadata.typography.body.line_height,
                },
                "heading": {
                    "fontFamily": metadata.typography.heading.font_family,
                    "fontWeights": metadata.typography.heading.font_weights,
                    "fontSize": metadata.typography.heading.font_size,
                    "lineHeight": metadata.typography.heading.line_height,
                },
            },
            "notes": metadata.notes,
        }

    # =========================================================================
    # Deserialization: Dict -> Domain (from JSON storage)
    # =========================================================================

    def _dict_to_url(self, data: dict | None) -> Url:
        """Convert dict to Url."""
        if not data:
            return Url()
        return Url(url=data.get("url", ""), label=data.get("label", ""))

    def _dict_to_content(self, data: dict) -> ResumeContent:
        """Convert dict from JSON storage to ResumeContent."""
        # Handle both new format (nested) and legacy format (flat)
        if "basics" in data:
            # New nested format
            return self._dict_to_content_new_format(data)
        else:
            # Legacy flat format - convert to new structure
            return self._dict_to_content_legacy_format(data)

    def _dict_to_content_new_format(self, data: dict) -> ResumeContent:
        """Parse new nested format."""
        return ResumeContent(
            picture=self._dict_to_picture(data.get("picture", {})),
            basics=self._dict_to_basics(data.get("basics", {})),
            summary=self._dict_to_summary(data.get("summary", {})),
            sections=self._dict_to_sections(data.get("sections", {})),
            custom_sections=[
                self._dict_to_custom_section(cs)
                for cs in data.get("customSections", [])
            ],
            metadata=self._dict_to_metadata(data.get("metadata", {})),
        )

    def _dict_to_content_legacy_format(self, data: dict) -> ResumeContent:
        """Convert legacy flat format to new nested structure."""
        # Build basics from legacy fields
        basics = Basics(
            name=data.get("full_name", ""),
            headline="",
            email=data.get("email", ""),
            phone=data.get("phone") or "",
            location=data.get("location") or "",
            website=Url(url=data.get("portfolio_url") or ""),
            custom_fields=[
                CustomLink(id=cl.get("id", ""), text=cl.get("label", ""), link=cl.get("url", ""))
                for cl in data.get("custom_links", [])
            ],
        )

        # Build summary
        summary = Summary(content=data.get("professional_summary") or "")

        # Build sections from legacy arrays
        sections = Sections(
            profiles=self._legacy_profiles_to_section(data),
            experience=self._legacy_experience_to_section(data.get("work_experience", [])),
            education=self._legacy_education_to_section(data.get("education", [])),
            skills=self._legacy_skills_to_section(data.get("skills", {})),
            projects=self._legacy_projects_to_section(data.get("projects", [])),
            awards=self._legacy_awards_to_section(data.get("awards", [])),
            certifications=self._legacy_certifications_to_section(data.get("certifications", [])),
            languages=self._legacy_languages_to_section(data.get("languages", [])),
        )

        # Build metadata
        metadata = Metadata(template=data.get("template_id", "onyx"))

        return ResumeContent(
            picture=PictureSettings(url=data.get("profile_picture_url") or ""),
            basics=basics,
            summary=summary,
            sections=sections,
            custom_sections=[],
            metadata=metadata,
        )

    def _legacy_profiles_to_section(self, data: dict) -> ProfilesSection:
        """Convert legacy profile URLs to ProfilesSection."""
        items = []
        if data.get("linkedin_url"):
            items.append(ProfileItem(
                network="LinkedIn",
                website=Url(url=data["linkedin_url"]),
            ))
        if data.get("github_url"):
            items.append(ProfileItem(
                network="GitHub",
                website=Url(url=data["github_url"]),
            ))
        return ProfilesSection(items=items)

    def _legacy_experience_to_section(self, exp_list: list) -> ExperienceSection:
        """Convert legacy work experience to ExperienceSection."""
        items = []
        for e in exp_list:
            # Build period from start_date/end_date
            period = ""
            if e.get("start_date"):
                period = e["start_date"]
                if e.get("is_current"):
                    period += " - Present"
                elif e.get("end_date"):
                    period += f" - {e['end_date']}"
            items.append(WorkExperience(
                company=e.get("company", ""),
                title=e.get("title", ""),
                location=e.get("location") or "",
                period=period,
                description=e.get("description") or "",
            ))
        return ExperienceSection(items=items)

    def _legacy_education_to_section(self, edu_list: list) -> EducationSection:
        """Convert legacy education to EducationSection."""
        items = []
        for e in edu_list:
            items.append(Education(
                school=e.get("institution", ""),
                degree=e.get("degree", ""),
                area=e.get("field_of_study") or "",
                grade=str(e.get("gpa", "")) if e.get("gpa") else "",
                location=e.get("location") or "",
                period=e.get("graduation_date") or "",
            ))
        return EducationSection(items=items)

    def _legacy_skills_to_section(self, skills_data: dict) -> SkillsSection:
        """Convert legacy categorized skills to SkillsSection."""
        items = []
        # Add technical skills
        for skill in skills_data.get("technical", []):
            items.append(SkillItem(name=skill, proficiency="Expert", level=5))
        # Add tools
        for skill in skills_data.get("tools", []):
            items.append(SkillItem(name=skill, proficiency="Advanced", level=4))
        # Add soft skills
        for skill in skills_data.get("soft", []):
            items.append(SkillItem(name=skill, proficiency="Advanced", level=4))
        return SkillsSection(items=items)

    def _legacy_projects_to_section(self, proj_list: list) -> ProjectsSection:
        """Convert legacy projects to ProjectsSection."""
        items = []
        for p in proj_list:
            period = ""
            if p.get("start_date"):
                period = p["start_date"]
                if p.get("end_date"):
                    period += f" - {p['end_date']}"
            items.append(Project(
                name=p.get("name", ""),
                period=period,
                website=Url(url=p.get("url") or ""),
                description=p.get("description", ""),
            ))
        return ProjectsSection(items=items)

    def _legacy_awards_to_section(self, award_list: list) -> AwardsSection:
        """Convert legacy awards to AwardsSection."""
        items = []
        for a in award_list:
            items.append(Award(
                title=a.get("title", ""),
                awarder=a.get("issuer", ""),
                date=a.get("date") or "",
                description=a.get("description") or "",
            ))
        return AwardsSection(items=items)

    def _legacy_certifications_to_section(self, cert_list: list) -> CertificationsSection:
        """Convert legacy certifications to CertificationsSection."""
        items = []
        for c in cert_list:
            items.append(Certification(
                title=c.get("name", ""),
                issuer=c.get("issuer", ""),
                date=c.get("date") or "",
                website=Url(url=c.get("url") or ""),
            ))
        return CertificationsSection(items=items)

    def _legacy_languages_to_section(self, lang_list: list) -> LanguagesSection:
        """Convert legacy languages to LanguagesSection."""
        items = []
        for lang in lang_list:
            fluency = lang.get("proficiency") or "conversational"
            # Convert enum to display text
            fluency_map = {
                "native": "Native",
                "fluent": "Fluent",
                "conversational": "Conversational",
                "basic": "Basic",
            }
            level_map = {"native": 5, "fluent": 4, "conversational": 3, "basic": 2}
            items.append(LanguageSkill(
                language=lang.get("language", ""),
                fluency=fluency_map.get(fluency, fluency),
                level=level_map.get(fluency, 3),
            ))
        return LanguagesSection(items=items)

    def _dict_to_picture(self, data: dict) -> PictureSettings:
        """Convert dict to PictureSettings."""
        return PictureSettings(
            hidden=data.get("hidden", False),
            url=data.get("url", ""),
            size=data.get("size", 80),
            rotation=data.get("rotation", 0),
            aspect_ratio=data.get("aspectRatio", 1.0),
            border_radius=data.get("borderRadius", 0),
            border_color=data.get("borderColor", "rgba(0, 0, 0, 0.5)"),
            border_width=data.get("borderWidth", 0),
            shadow_color=data.get("shadowColor", "rgba(0, 0, 0, 0.5)"),
            shadow_width=data.get("shadowWidth", 0),
        )

    def _dict_to_basics(self, data: dict) -> Basics:
        """Convert dict to Basics."""
        return Basics(
            name=data.get("name", ""),
            headline=data.get("headline", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            location=data.get("location", ""),
            website=self._dict_to_url(data.get("website")),
            custom_fields=[
                CustomLink(
                    id=cf.get("id", ""),
                    icon=cf.get("icon", ""),
                    text=cf.get("text", ""),
                    link=cf.get("link", ""),
                )
                for cf in data.get("customFields", [])
            ],
        )

    def _dict_to_summary(self, data: dict) -> Summary:
        """Convert dict to Summary."""
        return Summary(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            content=data.get("content", ""),
        )

    def _dict_to_sections(self, data: dict) -> Sections:
        """Convert dict to Sections."""
        return Sections(
            profiles=self._dict_to_profiles_section(data.get("profiles", {})),
            experience=self._dict_to_experience_section(data.get("experience", {})),
            education=self._dict_to_education_section(data.get("education", {})),
            skills=self._dict_to_skills_section(data.get("skills", {})),
            projects=self._dict_to_projects_section(data.get("projects", {})),
            awards=self._dict_to_awards_section(data.get("awards", {})),
            certifications=self._dict_to_certifications_section(data.get("certifications", {})),
            languages=self._dict_to_languages_section(data.get("languages", {})),
            interests=self._dict_to_interests_section(data.get("interests", {})),
            volunteer=self._dict_to_volunteer_section(data.get("volunteer", {})),
            publications=self._dict_to_publications_section(data.get("publications", {})),
            references=self._dict_to_references_section(data.get("references", {})),
        )

    def _dict_to_profiles_section(self, data: dict) -> ProfilesSection:
        """Convert dict to ProfilesSection."""
        items = [
            ProfileItem(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                icon=item.get("icon", ""),
                network=item.get("network", ""),
                username=item.get("username", ""),
                website=self._dict_to_url(item.get("website")),
            )
            for item in data.get("items", [])
        ]
        return ProfilesSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_experience_section(self, data: dict) -> ExperienceSection:
        """Convert dict to ExperienceSection."""
        items = [
            WorkExperience(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                company=item.get("company", ""),
                title=item.get("position", ""),
                location=item.get("location", ""),
                period=item.get("period", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return ExperienceSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_education_section(self, data: dict) -> EducationSection:
        """Convert dict to EducationSection."""
        items = [
            Education(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                school=item.get("school", ""),
                degree=item.get("degree", ""),
                area=item.get("area", ""),
                grade=item.get("grade", ""),
                location=item.get("location", ""),
                period=item.get("period", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return EducationSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_skills_section(self, data: dict) -> SkillsSection:
        """Convert dict to SkillsSection."""
        items = [
            SkillItem(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                icon=item.get("icon", ""),
                name=item.get("name", ""),
                proficiency=item.get("proficiency", ""),
                level=item.get("level", 0),
                keywords=item.get("keywords", []),
            )
            for item in data.get("items", [])
        ]
        return SkillsSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_projects_section(self, data: dict) -> ProjectsSection:
        """Convert dict to ProjectsSection."""
        items = [
            Project(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                name=item.get("name", ""),
                period=item.get("period", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return ProjectsSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_awards_section(self, data: dict) -> AwardsSection:
        """Convert dict to AwardsSection."""
        items = [
            Award(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                title=item.get("title", ""),
                awarder=item.get("awarder", ""),
                date=item.get("date", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return AwardsSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_certifications_section(self, data: dict) -> CertificationsSection:
        """Convert dict to CertificationsSection."""
        items = [
            Certification(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                title=item.get("title", ""),
                issuer=item.get("issuer", ""),
                date=item.get("date", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return CertificationsSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_languages_section(self, data: dict) -> LanguagesSection:
        """Convert dict to LanguagesSection."""
        items = [
            LanguageSkill(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                language=item.get("language", ""),
                fluency=item.get("fluency", ""),
                level=item.get("level", 0),
            )
            for item in data.get("items", [])
        ]
        return LanguagesSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_interests_section(self, data: dict) -> InterestsSection:
        """Convert dict to InterestsSection."""
        items = [
            InterestItem(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                icon=item.get("icon", ""),
                name=item.get("name", ""),
                keywords=item.get("keywords", []),
            )
            for item in data.get("items", [])
        ]
        return InterestsSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_volunteer_section(self, data: dict) -> VolunteerSection:
        """Convert dict to VolunteerSection."""
        items = [
            Volunteer(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                organization=item.get("organization", ""),
                location=item.get("location", ""),
                period=item.get("period", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return VolunteerSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_publications_section(self, data: dict) -> PublicationsSection:
        """Convert dict to PublicationsSection."""
        items = [
            Publication(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                title=item.get("title", ""),
                publisher=item.get("publisher", ""),
                date=item.get("date", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return PublicationsSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_references_section(self, data: dict) -> ReferencesSection:
        """Convert dict to ReferencesSection."""
        items = [
            Reference(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                name=item.get("name", ""),
                position=item.get("position", ""),
                phone=item.get("phone", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
            )
            for item in data.get("items", [])
        ]
        return ReferencesSection(
            title=data.get("title", ""),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_custom_section(self, data: dict) -> CustomSection:
        """Convert dict to CustomSection."""
        items = [
            CustomSectionItem(
                id=item.get("id", ""),
                hidden=item.get("hidden", False),
                name=item.get("name", ""),
                title=item.get("title", ""),
                company=item.get("company", ""),
                school=item.get("school", ""),
                organization=item.get("organization", ""),
                position=item.get("position", ""),
                location=item.get("location", ""),
                period=item.get("period", ""),
                date=item.get("date", ""),
                website=self._dict_to_url(item.get("website")),
                description=item.get("description", ""),
                content=item.get("content", ""),
                icon=item.get("icon", ""),
                keywords=item.get("keywords", []),
                proficiency=item.get("proficiency", ""),
                level=item.get("level", 0),
                fluency=item.get("fluency", ""),
                language=item.get("language", ""),
                awarder=item.get("awarder", ""),
                issuer=item.get("issuer", ""),
                publisher=item.get("publisher", ""),
                phone=item.get("phone", ""),
                network=item.get("network", ""),
                username=item.get("username", ""),
                recipient=item.get("recipient", ""),
            )
            for item in data.get("items", [])
        ]
        return CustomSection(
            id=data.get("id", ""),
            title=data.get("title", ""),
            type=data.get("type", "experience"),
            columns=data.get("columns", 1),
            hidden=data.get("hidden", False),
            items=items,
        )

    def _dict_to_metadata(self, data: dict) -> Metadata:
        """Convert dict to Metadata."""
        layout_data = data.get("layout", {})
        layout = Layout(
            sidebar_width=layout_data.get("sidebarWidth", 35),
            pages=[
                PageLayout(
                    full_width=p.get("fullWidth", False),
                    main=p.get("main", []),
                    sidebar=p.get("sidebar", []),
                )
                for p in layout_data.get("pages", [])
            ],
        )

        css_data = data.get("css", {})
        css = Css(enabled=css_data.get("enabled", False), value=css_data.get("value", ""))

        page_data = data.get("page", {})
        page = Page(
            gap_x=page_data.get("gapX", 4),
            gap_y=page_data.get("gapY", 6),
            margin_x=page_data.get("marginX", 14),
            margin_y=page_data.get("marginY", 12),
            format=page_data.get("format", "a4"),
            locale=page_data.get("locale", "en-US"),
            hide_icons=page_data.get("hideIcons", False),
        )

        design_data = data.get("design", {})
        level_data = design_data.get("level", {})
        colors_data = design_data.get("colors", {})
        design = Design(
            level=LevelDesign(
                icon=level_data.get("icon", "star"),
                type=level_data.get("type", "circle"),
            ),
            colors=ColorDesign(
                primary=colors_data.get("primary", "rgba(220, 38, 38, 1)"),
                text=colors_data.get("text", "rgba(0, 0, 0, 1)"),
                background=colors_data.get("background", "rgba(255, 255, 255, 1)"),
            ),
        )

        typography_data = data.get("typography", {})
        body_data = typography_data.get("body", {})
        heading_data = typography_data.get("heading", {})
        typography = Typography(
            body=TypographyItem(
                font_family=body_data.get("fontFamily", "IBM Plex Serif"),
                font_weights=body_data.get("fontWeights", ["400", "500"]),
                font_size=body_data.get("fontSize", 10),
                line_height=body_data.get("lineHeight", 1.5),
            ),
            heading=TypographyItem(
                font_family=heading_data.get("fontFamily", "IBM Plex Serif"),
                font_weights=heading_data.get("fontWeights", ["600"]),
                font_size=heading_data.get("fontSize", 14),
                line_height=heading_data.get("lineHeight", 1.5),
            ),
        )

        return Metadata(
            template=data.get("template", "onyx"),
            layout=layout,
            css=css,
            page=page,
            design=design,
            typography=typography,
            notes=data.get("notes", ""),
        )
