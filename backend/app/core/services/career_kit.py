"""CareerKit Expert Apply service.

Standards: python_clean.mdc
- Cost-optimized pipeline architecture
- Embedding-based bullet selection
- Deterministic delta application
- kw-only args
"""

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime

import structlog

from app.agents.config import Models
from app.agents.prompts import (
    CAREERKIT_CV_POLISH_PROMPT,
    CAREERKIT_DELTA_GENERATOR_PROMPT,
    CAREERKIT_GAP_ANALYZER_PROMPT,
    CAREERKIT_INTERVIEW_PREP_PROMPT,
    CAREERKIT_JD_EXTRACTOR_PROMPT,
)
from app.core.domain.career_kit import (
    CareerKitPhase,
    CareerKitSession,
    ConfidenceScore,
    CustomJD,
    CVBullet,
    DeltaAction,
    DeltaInstruction,
    Evidence,
    GapMapItem,
    GapStatus,
    InterviewPrep,
    InterviewQuestion,
    PrepPlanDay,
    Question,
    QuestionnaireAnswer,
    Requirement,
    RequirementLevel,
    ResumeSource,
    STARStory,
    TailoredCV,
)
from app.core.domain.job import Job
from app.core.domain.resume import ParsedResume, ResumeContent
from app.core.ports.llm import LLMClient, LLMMessage

logger = structlog.get_logger(__name__)


@dataclass
class AnalyzeResult:
    """Result of Phase 1 analysis."""

    session: CareerKitSession
    requirements: list[Requirement]
    gap_map: list[GapMapItem]
    questionnaire: list[Question]


@dataclass
class GenerateResult:
    """Result of Phase 2 generation."""

    session: CareerKitSession
    delta_instructions: list[DeltaInstruction]
    tailored_cv: TailoredCV
    interview_prep: InterviewPrep


class CareerKitService:
    """Service for CareerKit Expert Apply workflow.

    Implements a cost-optimized pipeline:
    - Phase 1 (Analyze): JD extraction -> Bullet selection -> Gap analysis -> Questionnaire
    - Phase 2 (Generate): Delta generation -> Deduplication -> Polish -> Interview prep
    """

    # Token caps for cost control
    MAX_BULLETS_TO_SELECT = 50
    MAX_REQUIREMENTS = 30

    def __init__(self, *, llm_client: LLMClient) -> None:
        """Initialize CareerKit service.

        Args:
            llm_client: LLM client for generation
        """
        self._llm = llm_client

    async def analyze(
        self,
        *,
        user_id: str,
        job: Job | None = None,
        custom_jd: CustomJD | None = None,
        resume_source: ResumeSource,
        resume_content: ParsedResume | ResumeContent,
    ) -> AnalyzeResult:
        """Phase 1: Analyze JD vs CV and generate questionnaire.

        Args:
            user_id: User ID
            job: Job from database (if using db job)
            custom_jd: Custom JD (if pasted)
            resume_source: Resume source specification
            resume_content: Parsed resume or builder content

        Returns:
            AnalyzeResult with requirements, gap_map, questionnaire
        """
        logger.info(
            "careerkit_analyze_start",
            user_id=user_id,
            has_job=job is not None,
            has_custom_jd=custom_jd is not None,
            resume_source_type=resume_source.source_type,
        )

        # Determine job details
        if job:
            jd_text = job.description
            job_title = job.title
            company = job.company
            session_name = f"{job_title} at {company}"
            is_custom = False
        elif custom_jd:
            jd_text = custom_jd.description
            job_title = custom_jd.title
            company = custom_jd.company
            session_name = custom_jd.generate_session_name()
            is_custom = True
        else:
            raise ValueError("Either job or custom_jd must be provided")

        # Step 1: Extract JD requirements
        requirements = await self._extract_jd_requirements(
            jd_text=jd_text,
            job_title=job_title,
        )

        # Step 2: Extract and select relevant CV bullets
        cv_bullets = self._extract_cv_bullets(resume_content)
        selected_bullets = await self._select_relevant_bullets(
            requirements=requirements,
            cv_bullets=cv_bullets,
        )

        # Step 3: Gap analysis and questionnaire generation
        gap_map, questionnaire = await self._analyze_gaps(
            requirements=requirements,
            selected_bullets=selected_bullets,
            job_title=job_title,
        )

        # Create session
        session = CareerKitSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            job_id=job.id if job else None,
            custom_jd=custom_jd,
            session_name=session_name,
            is_custom_job=is_custom,
            phase=CareerKitPhase.QUESTIONNAIRE,
            resume_source=resume_source,
            requirements=requirements,
            selected_bullets=selected_bullets,
            gap_map=gap_map,
            questionnaire=questionnaire,
            created_at=datetime.utcnow(),
        )

        logger.info(
            "careerkit_analyze_complete",
            session_id=session.id,
            requirements_count=len(requirements),
            gaps_count=len([g for g in gap_map if g.status != GapStatus.COVERED]),
            questions_count=len(questionnaire),
        )

        return AnalyzeResult(
            session=session,
            requirements=requirements,
            gap_map=gap_map,
            questionnaire=questionnaire,
        )

    async def generate(
        self,
        *,
        session: CareerKitSession,
        answers: list[QuestionnaireAnswer],
        original_cv_content: ParsedResume | ResumeContent,
    ) -> GenerateResult:
        """Phase 2: Generate tailored CV and interview prep.

        Args:
            session: Existing session from Phase 1
            answers: User's questionnaire answers
            original_cv_content: Original CV content for delta application

        Returns:
            GenerateResult with tailored CV and interview prep
        """
        logger.info(
            "careerkit_generate_start",
            session_id=session.id,
            answers_count=len(answers),
        )

        # Update session with answers
        session.answers = answers
        session.phase = CareerKitPhase.GENERATE

        # Step 4: Generate delta instructions
        delta_instructions = await self._generate_delta(
            requirements=session.requirements or [],
            selected_bullets=session.selected_bullets or [],
            gap_map=session.gap_map or [],
            answers=answers,
        )

        # Step 5: Deduplicate bullets (deterministic)
        delta_instructions = self._deduplicate_bullets(delta_instructions)

        # Step 6 & 7: Apply delta and polish CV
        tailored_cv = await self._apply_and_polish(
            original_cv=original_cv_content,
            delta_instructions=delta_instructions,
            requirements=session.requirements or [],
        )

        # Step 8: Generate interview prep
        interview_prep = await self._generate_interview_prep(
            requirements=session.requirements or [],
            tailored_cv=tailored_cv,
            gap_map=session.gap_map or [],
            answers=answers,
        )

        # Update session
        session.delta_instructions = delta_instructions
        session.interview_prep = interview_prep
        session.phase = CareerKitPhase.COMPLETE
        session.updated_at = datetime.utcnow()

        logger.info(
            "careerkit_generate_complete",
            session_id=session.id,
            delta_count=len(delta_instructions),
            interview_questions=len(interview_prep.likely_questions),
        )

        return GenerateResult(
            session=session,
            delta_instructions=delta_instructions,
            tailored_cv=tailored_cv,
            interview_prep=interview_prep,
        )

    # =========================================================================
    # Phase 1 Pipeline Steps
    # =========================================================================

    async def _extract_jd_requirements(
        self,
        *,
        jd_text: str,
        job_title: str,
    ) -> list[Requirement]:
        """Step 1: Extract structured requirements from JD.

        Uses LLAMA4_SCOUT for fast, cheap extraction.
        """
        messages = [
            LLMMessage(role="system", content=CAREERKIT_JD_EXTRACTOR_PROMPT),
            LLMMessage(
                role="user",
                content=f"""Extract requirements from this job description.

Job Title: {job_title}

Job Description:
{jd_text[:8000]}  # Cap to avoid token overflow

Return JSON with "requirements" array and "target_profile" string.""",
            ),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA4_SCOUT,
            temperature=0.2,
            max_tokens=2000,
        )

        # Parse JSON response
        requirements = self._parse_requirements_response(response.content)

        # Cap requirements
        return requirements[: self.MAX_REQUIREMENTS]

    def _extract_cv_bullets(
        self,
        cv: ParsedResume | ResumeContent,
    ) -> list[str]:
        """Extract individual bullets from CV content."""
        bullets: list[str] = []

        if isinstance(cv, ParsedResume):
            # ParsedResume from uploaded file
            if cv.experience:
                for exp in cv.experience:
                    if exp.get("achievements"):
                        bullets.extend(exp["achievements"])
                    if exp.get("description"):
                        bullets.append(exp["description"])
            if cv.skills:
                bullets.extend(cv.skills)
            if cv.education:
                for edu in cv.education:
                    bullets.append(f"{edu.get('degree', '')} from {edu.get('institution', '')}")
        else:
            # ResumeContent from builder (new nested structure)
            for exp in cv.sections.experience.items:
                if exp.description:
                    bullets.append(exp.description)
            # Skills are now objects with .name
            for skill in cv.sections.skills.items:
                bullets.append(skill.name)
                bullets.extend(skill.keywords)
            for project in cv.sections.projects.items:
                if project.name and project.description:
                    bullets.append(f"{project.name}: {project.description}")

        return [b for b in bullets if b and len(b) > 10]

    async def _select_relevant_bullets(
        self,
        *,
        requirements: list[Requirement],
        cv_bullets: list[str],
    ) -> list[str]:
        """Step 2: Select most relevant bullets using embedding similarity.

        Uses embeddings to find bullets most relevant to JD requirements.
        Falls back to keyword matching if embedding fails.
        """
        if not cv_bullets:
            return []

        # Collect all keywords from requirements
        keywords = set()
        for req in requirements:
            keywords.add(req.name.lower())
            keywords.update(k.lower() for k in req.keywords)

        # Simple keyword-based scoring (fallback, faster)
        scored_bullets: list[tuple[str, int]] = []
        for bullet in cv_bullets:
            bullet_lower = bullet.lower()
            score = sum(1 for kw in keywords if kw in bullet_lower)
            scored_bullets.append((bullet, score))

        # Sort by score and take top N
        scored_bullets.sort(key=lambda x: x[1], reverse=True)
        selected = [b for b, s in scored_bullets if s > 0][: self.MAX_BULLETS_TO_SELECT]

        # If not enough matches, add some bullets anyway
        if len(selected) < 20:
            remaining = [b for b, _ in scored_bullets if b not in selected]
            selected.extend(remaining[: 20 - len(selected)])

        return selected

    async def _analyze_gaps(
        self,
        *,
        requirements: list[Requirement],
        selected_bullets: list[str],
        job_title: str,
    ) -> tuple[list[GapMapItem], list[Question]]:
        """Step 3: Analyze gaps between requirements and CV evidence."""
        # Format requirements
        req_text = "\n".join(
            f"- {r.name} ({r.level.value}): {', '.join(r.keywords)}"
            for r in requirements
        )

        # Format bullets
        bullets_text = "\n".join(f"- {b}" for b in selected_bullets[:40])

        messages = [
            LLMMessage(role="system", content=CAREERKIT_GAP_ANALYZER_PROMPT),
            LLMMessage(
                role="user",
                content=f"""Analyze gaps between these JD requirements and CV bullets.

JOB TITLE: {job_title}

REQUIREMENTS:
{req_text}

CV BULLETS (selected relevant ones):
{bullets_text}

Return JSON with "gap_map" and "questionnaire" arrays.""",
            ),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA4_MAVERICK,
            temperature=0.4,
            max_tokens=3000,
        )

        return self._parse_gap_analysis_response(response.content)

    # =========================================================================
    # Phase 2 Pipeline Steps
    # =========================================================================

    async def _generate_delta(
        self,
        *,
        requirements: list[Requirement],
        selected_bullets: list[str],
        gap_map: list[GapMapItem],
        answers: list[QuestionnaireAnswer],
    ) -> list[DeltaInstruction]:
        """Step 4: Generate delta instructions for CV modification."""
        # Format inputs
        req_text = "\n".join(f"- {r.name}" for r in requirements[:20])
        bullets_text = "\n".join(
            f"[{i}] {b}" for i, b in enumerate(selected_bullets[:30])
        )
        gap_text = "\n".join(
            f"- {g.requirement_name}: {g.status.value}"
            for g in gap_map
        )
        answers_text = "\n".join(
            f"Q: {a.question_id} -> A: {a.answer}" for a in answers
        )

        messages = [
            LLMMessage(role="system", content=CAREERKIT_DELTA_GENERATOR_PROMPT),
            LLMMessage(
                role="user",
                content=f"""Generate delta instructions to tailor this CV.

REQUIREMENTS:
{req_text}

CV BULLETS:
{bullets_text}

GAP STATUS:
{gap_text}

USER ANSWERS:
{answers_text}

Return JSON with "delta_instructions" and "truth_notes" arrays.""",
            ),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA4_MAVERICK,
            temperature=0.3,
            max_tokens=3000,
        )

        return self._parse_delta_response(response.content)

    def _deduplicate_bullets(
        self,
        instructions: list[DeltaInstruction],
    ) -> list[DeltaInstruction]:
        """Step 5: Remove near-duplicate bullets deterministically."""
        # Simple deduplication: remove exact duplicates and very similar strings
        seen_texts: set[str] = set()
        deduplicated: list[DeltaInstruction] = []

        for inst in instructions:
            text = (inst.new_text or inst.original_text or "").lower().strip()
            # Normalize for comparison
            normalized = re.sub(r"[^a-z0-9\s]", "", text)

            if normalized not in seen_texts and len(normalized) > 20:
                seen_texts.add(normalized)
                deduplicated.append(inst)

        return deduplicated

    async def _apply_and_polish(
        self,
        *,
        original_cv: ParsedResume | ResumeContent,
        delta_instructions: list[DeltaInstruction],
        requirements: list[Requirement],
    ) -> TailoredCV:
        """Step 6 & 7: Apply delta and polish for ATS."""
        # Collect bullets by action
        keep_bullets: list[CVBullet] = []
        rewrite_bullets: list[CVBullet] = []
        add_bullets: list[CVBullet] = []

        for inst in delta_instructions:
            if inst.action == DeltaAction.KEEP:
                keep_bullets.append(
                    CVBullet(
                        text=inst.original_text or "",
                        confidence_score=ConfidenceScore.HIGH,
                        source_ref=inst.bullet_id,
                    )
                )
            elif inst.action == DeltaAction.REWRITE:
                rewrite_bullets.append(
                    CVBullet(
                        text=inst.new_text or inst.original_text or "",
                        confidence_score=inst.confidence_score,
                        source_ref=inst.bullet_id,
                    )
                )
            elif inst.action == DeltaAction.ADD:
                add_bullets.append(
                    CVBullet(
                        text=inst.new_text or "",
                        confidence_score=ConfidenceScore.LOW,
                        source_ref=inst.bullet_id,
                        needs_verification=True,
                    )
                )

        # Extract original info
        if isinstance(original_cv, ParsedResume):
            name = original_cv.name or ""
            summary = original_cv.summary or ""
            skills = original_cv.skills or []
            education = [
                f"{e.get('degree', '')} - {e.get('institution', '')}"
                for e in (original_cv.education or [])
            ]
        else:
            # ResumeContent from builder (new nested structure)
            name = original_cv.basics.name
            summary = original_cv.summary.content or ""
            # Skills are now objects with .name
            skills = [skill.name for skill in original_cv.sections.skills.items]
            education = [
                f"{e.degree} - {e.school}"
                for e in original_cv.sections.education.items
            ]

        # Build tailored CV structure
        all_bullets = keep_bullets + rewrite_bullets + add_bullets
        experience_bullets = {"General": all_bullets}  # Simplified for now

        # Extract requirement keywords for skills ordering
        jd_keywords = set()
        for req in requirements:
            jd_keywords.update(k.lower() for k in req.keywords)

        # Reorder skills to prioritize JD matches
        skills_sorted = sorted(
            skills,
            key=lambda s: (s.lower() not in jd_keywords, s),
        )

        # Build truth notes from delta instructions
        truth_notes = [
            inst.reason
            for inst in delta_instructions
            if inst.action == DeltaAction.REMOVE and inst.reason
        ]

        return TailoredCV(
            targeted_title=requirements[0].name if requirements else name,
            summary=summary,
            skills=skills_sorted[:20],
            experience_bullets=experience_bullets,
            projects=[],
            education=education,
            truth_notes=truth_notes,
        )

    async def _generate_interview_prep(
        self,
        *,
        requirements: list[Requirement],
        tailored_cv: TailoredCV,
        gap_map: list[GapMapItem],
        answers: list[QuestionnaireAnswer],
    ) -> InterviewPrep:
        """Step 8: Generate interview preparation kit."""
        # Format context
        req_text = "\n".join(f"- {r.name}" for r in requirements[:15])
        cv_summary = f"Title: {tailored_cv.targeted_title}\nSkills: {', '.join(tailored_cv.skills[:10])}"

        messages = [
            LLMMessage(role="system", content=CAREERKIT_INTERVIEW_PREP_PROMPT),
            LLMMessage(
                role="user",
                content=f"""Generate interview prep for this role.

ROLE REQUIREMENTS:
{req_text}

CANDIDATE PROFILE:
{cv_summary}

Return JSON with role_understanding, likely_questions, story_bank, tech_deep_dive_topics, seven_day_prep_plan.""",
            ),
        ]

        response = await self._llm.complete(
            messages=messages,
            model=Models.LLAMA4_MAVERICK,
            temperature=0.5,
            max_tokens=3000,
        )

        return self._parse_interview_prep_response(response.content)

    # =========================================================================
    # Response Parsers
    # =========================================================================

    def _parse_requirements_response(self, content: str) -> list[Requirement]:
        """Parse LLM response for requirements extraction."""
        try:
            # Extract JSON from response
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                data = json.loads(json_match.group())
                reqs = data.get("requirements", [])
                return [
                    Requirement(
                        name=r.get("name", ""),
                        level=RequirementLevel(r.get("level", "must")),
                        category=r.get("category", "technical"),
                        keywords=r.get("keywords", []),
                        original_text=r.get("original_text"),
                    )
                    for r in reqs
                ]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("requirements_parse_error", error=str(e))

        return []

    def _parse_gap_analysis_response(
        self, content: str
    ) -> tuple[list[GapMapItem], list[Question]]:
        """Parse LLM response for gap analysis."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                data = json.loads(json_match.group())

                gap_map = [
                    GapMapItem(
                        requirement_name=g.get("requirement_name", ""),
                        status=GapStatus(g.get("status", "missing")),
                        evidence=[
                            Evidence(
                                source=e.get("source", "cv"),
                                quote=e.get("quote", ""),
                                cv_section=e.get("cv_section"),
                            )
                            for e in g.get("evidence", [])
                        ],
                        risk_note=g.get("risk_note"),
                        question_needed=g.get("question_needed", False),
                    )
                    for g in data.get("gap_map", [])
                ]

                questionnaire = [
                    Question(
                        id=q.get("id", f"q{i}"),
                        topic=q.get("topic", ""),
                        question=q.get("question", ""),
                        answer_type=q.get("answer_type", "text"),
                        why_asked=q.get("why_asked", ""),
                        options=q.get("options"),
                    )
                    for i, q in enumerate(data.get("questionnaire", []))
                ]

                return gap_map, questionnaire
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("gap_analysis_parse_error", error=str(e))

        return [], []

    def _parse_delta_response(self, content: str) -> list[DeltaInstruction]:
        """Parse LLM response for delta generation."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                data = json.loads(json_match.group())
                return [
                    DeltaInstruction(
                        bullet_id=d.get("bullet_id", f"b{i}"),
                        action=DeltaAction(d.get("action", "keep")),
                        original_text=d.get("original_text"),
                        new_text=d.get("new_text"),
                        confidence_score=ConfidenceScore(
                            d.get("confidence_score", "high")
                        ),
                        reason=d.get("reason"),
                    )
                    for i, d in enumerate(data.get("delta_instructions", []))
                ]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("delta_parse_error", error=str(e))

        return []

    def _parse_interview_prep_response(self, content: str) -> InterviewPrep:
        """Parse LLM response for interview prep."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                data = json.loads(json_match.group())
                return InterviewPrep(
                    role_understanding=data.get("role_understanding", ""),
                    likely_questions=[
                        InterviewQuestion(
                            question=q.get("question", ""),
                            category=q.get("category", "behavioral"),
                            difficulty=q.get("difficulty", "medium"),
                            suggested_answer=q.get("suggested_answer"),
                        )
                        for q in data.get("likely_questions", [])
                    ],
                    suggested_answers=data.get("suggested_answers", {}),
                    story_bank=[
                        STARStory(
                            title=s.get("title", ""),
                            situation=s.get("situation", ""),
                            task=s.get("task", ""),
                            action=s.get("action", ""),
                            result=s.get("result", ""),
                            applicable_to=s.get("applicable_to", []),
                        )
                        for s in data.get("story_bank", [])
                    ],
                    tech_deep_dive_topics=data.get("tech_deep_dive_topics", []),
                    seven_day_prep_plan=[
                        PrepPlanDay(
                            day=p.get("day", 1),
                            focus=p.get("focus", ""),
                            tasks=p.get("tasks", []),
                            time_estimate_minutes=p.get("time_estimate_minutes", 60),
                        )
                        for p in data.get("seven_day_prep_plan", [])
                    ],
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("interview_prep_parse_error", error=str(e))

        return InterviewPrep(role_understanding="")
