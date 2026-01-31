"""Skill gap analysis service.

Standards: python_clean.mdc
- Data-driven recommendations
- Course mappings
"""

from dataclasses import dataclass, field

import structlog

from app.core.domain.job import Job
from app.core.domain.resume import ParsedResume

logger = structlog.get_logger(__name__)


@dataclass
class CourseRecommendation:
    """Course recommendation for skill development."""

    title: str
    provider: str  # Coursera, Udemy, LinkedIn Learning
    url: str
    duration: str  # "4 weeks", "10 hours"
    level: str  # beginner, intermediate, advanced


@dataclass
class SkillGap:
    """Identified skill gap with recommendations."""

    skill: str
    importance: str  # required, preferred
    gap_type: str  # missing, weak
    courses: list[CourseRecommendation] = field(default_factory=list)


@dataclass
class SkillGapAnalysis:
    """Complete skill gap analysis result."""

    resume_skills: list[str]
    target_skills: list[str]
    matched_skills: list[str]
    gaps: list[SkillGap]
    match_percentage: float
    top_priority_skills: list[str]


# Predefined course mappings for common skills
SKILL_COURSES: dict[str, list[CourseRecommendation]] = {
    "python": [
        CourseRecommendation(
            title="Python for Everybody Specialization",
            provider="Coursera",
            url="https://www.coursera.org/specializations/python",
            duration="8 months",
            level="beginner",
        ),
        CourseRecommendation(
            title="Complete Python Bootcamp",
            provider="Udemy",
            url="https://www.udemy.com/course/complete-python-bootcamp/",
            duration="22 hours",
            level="beginner",
        ),
    ],
    "javascript": [
        CourseRecommendation(
            title="JavaScript: The Complete Guide",
            provider="Udemy",
            url="https://www.udemy.com/course/javascript-the-complete-guide/",
            duration="52 hours",
            level="intermediate",
        ),
    ],
    "react": [
        CourseRecommendation(
            title="React - The Complete Guide",
            provider="Udemy",
            url="https://www.udemy.com/course/react-the-complete-guide/",
            duration="48 hours",
            level="intermediate",
        ),
        CourseRecommendation(
            title="Advanced React and Redux",
            provider="Udemy",
            url="https://www.udemy.com/course/react-redux/",
            duration="21 hours",
            level="advanced",
        ),
    ],
    "typescript": [
        CourseRecommendation(
            title="Understanding TypeScript",
            provider="Udemy",
            url="https://www.udemy.com/course/understanding-typescript/",
            duration="15 hours",
            level="intermediate",
        ),
    ],
    "aws": [
        CourseRecommendation(
            title="AWS Certified Solutions Architect",
            provider="Coursera",
            url="https://www.coursera.org/professional-certificates/aws-cloud-solutions-architect",
            duration="6 months",
            level="intermediate",
        ),
        CourseRecommendation(
            title="Ultimate AWS Certified Cloud Practitioner",
            provider="Udemy",
            url="https://www.udemy.com/course/aws-certified-cloud-practitioner-new/",
            duration="14 hours",
            level="beginner",
        ),
    ],
    "docker": [
        CourseRecommendation(
            title="Docker and Kubernetes: The Complete Guide",
            provider="Udemy",
            url="https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/",
            duration="22 hours",
            level="intermediate",
        ),
    ],
    "kubernetes": [
        CourseRecommendation(
            title="Certified Kubernetes Administrator (CKA)",
            provider="Linux Foundation",
            url="https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/",
            duration="Self-paced",
            level="advanced",
        ),
    ],
    "sql": [
        CourseRecommendation(
            title="The Complete SQL Bootcamp",
            provider="Udemy",
            url="https://www.udemy.com/course/the-complete-sql-bootcamp/",
            duration="9 hours",
            level="beginner",
        ),
    ],
    "machine learning": [
        CourseRecommendation(
            title="Machine Learning Specialization",
            provider="Coursera",
            url="https://www.coursera.org/specializations/machine-learning-introduction",
            duration="3 months",
            level="intermediate",
        ),
    ],
    "data science": [
        CourseRecommendation(
            title="IBM Data Science Professional Certificate",
            provider="Coursera",
            url="https://www.coursera.org/professional-certificates/ibm-data-science",
            duration="10 months",
            level="beginner",
        ),
    ],
    "node.js": [
        CourseRecommendation(
            title="Node.js - The Complete Guide",
            provider="Udemy",
            url="https://www.udemy.com/course/nodejs-the-complete-guide/",
            duration="40 hours",
            level="intermediate",
        ),
    ],
    "graphql": [
        CourseRecommendation(
            title="GraphQL with React: The Complete Developers Guide",
            provider="Udemy",
            url="https://www.udemy.com/course/graphql-with-react-course/",
            duration="13 hours",
            level="intermediate",
        ),
    ],
}


class SkillGapService:
    """Service for analyzing skill gaps and recommending courses."""

    def analyze(
        self,
        *,
        resume: ParsedResume,
        jobs: list[Job],
    ) -> SkillGapAnalysis:
        """Analyze skill gaps between resume and target jobs.

        Args:
            resume: Candidate's parsed resume
            jobs: List of target jobs

        Returns:
            Complete skill gap analysis with recommendations
        """
        # Normalize resume skills
        resume_skills = set(s.lower() for s in (resume.skills or []))

        # Collect all required and preferred skills from jobs
        required_skills: dict[str, int] = {}  # skill -> count
        preferred_skills: dict[str, int] = {}

        for job in jobs:
            if job.requirements:
                for skill in job.requirements.required_skills:
                    skill_lower = skill.lower()
                    required_skills[skill_lower] = required_skills.get(skill_lower, 0) + 1

                for skill in job.requirements.preferred_skills:
                    skill_lower = skill.lower()
                    preferred_skills[skill_lower] = preferred_skills.get(skill_lower, 0) + 1

        # All target skills (union of required and preferred)
        all_target_skills = set(required_skills.keys()) | set(preferred_skills.keys())

        # Find matches and gaps
        matched_skills = resume_skills & all_target_skills
        missing_skills = all_target_skills - resume_skills

        # Calculate match percentage
        match_percentage = (
            len(matched_skills) / len(all_target_skills) * 100
            if all_target_skills
            else 100.0
        )

        # Build skill gaps with recommendations
        gaps: list[SkillGap] = []

        for skill in missing_skills:
            importance = "required" if skill in required_skills else "preferred"

            # Get course recommendations
            courses = self._get_courses_for_skill(skill)

            gaps.append(
                SkillGap(
                    skill=skill.title(),
                    importance=importance,
                    gap_type="missing",
                    courses=courses,
                )
            )

        # Sort gaps by importance and frequency
        gaps.sort(
            key=lambda g: (
                0 if g.importance == "required" else 1,
                -required_skills.get(g.skill.lower(), 0),
            )
        )

        # Top priority skills (required skills that appear in multiple jobs)
        top_priority = [
            skill
            for skill, count in sorted(
                required_skills.items(), key=lambda x: -x[1]
            )[:5]
            if skill not in resume_skills
        ]

        logger.info(
            "skill_gap_analysis_complete",
            resume_skills_count=len(resume_skills),
            target_skills_count=len(all_target_skills),
            matched_count=len(matched_skills),
            gaps_count=len(gaps),
            match_percentage=match_percentage,
        )

        return SkillGapAnalysis(
            resume_skills=list(resume.skills or []),
            target_skills=list(all_target_skills),
            matched_skills=list(matched_skills),
            gaps=gaps,
            match_percentage=match_percentage,
            top_priority_skills=top_priority,
        )

    def _get_courses_for_skill(self, skill: str) -> list[CourseRecommendation]:
        """Get course recommendations for a skill.

        Args:
            skill: Skill to find courses for

        Returns:
            List of course recommendations
        """
        skill_lower = skill.lower()

        # Direct match
        if skill_lower in SKILL_COURSES:
            return SKILL_COURSES[skill_lower]

        # Partial match (e.g., "react.js" -> "react")
        for key, courses in SKILL_COURSES.items():
            if key in skill_lower or skill_lower in key:
                return courses

        # No courses found
        return []

    def get_learning_path(
        self,
        *,
        gaps: list[SkillGap],
        max_courses: int = 5,
    ) -> list[CourseRecommendation]:
        """Generate a prioritized learning path.

        Args:
            gaps: List of skill gaps
            max_courses: Maximum number of courses to recommend

        Returns:
            Prioritized list of courses
        """
        seen_urls: set[str] = set()
        learning_path: list[CourseRecommendation] = []

        # Prioritize required skills
        for gap in gaps:
            if gap.importance == "required":
                for course in gap.courses:
                    if course.url not in seen_urls:
                        learning_path.append(course)
                        seen_urls.add(course.url)

                    if len(learning_path) >= max_courses:
                        return learning_path

        # Add preferred skills if room
        for gap in gaps:
            if gap.importance == "preferred":
                for course in gap.courses:
                    if course.url not in seen_urls:
                        learning_path.append(course)
                        seen_urls.add(course.url)

                    if len(learning_path) >= max_courses:
                        return learning_path

        return learning_path
