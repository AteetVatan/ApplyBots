"""Match scoring service.

Standards: python_clean.mdc
- Pure business logic, no IO
- Functions <=15 LOC
- kw-only args after *
- No magic numbers (use MatchWeights)
"""

from app.core.domain.application import MatchExplanation, MatchWeights
from app.core.domain.job import Job
from app.core.domain.profile import Preferences
from app.core.domain.resume import ParsedResume


class MatchService:
    """Calculate job-candidate match scores.

    Pure business logic - no IO dependencies.
    """

    def __init__(self, *, weights: MatchWeights | None = None) -> None:
        """Initialize with optional custom weights."""
        self._weights = weights or MatchWeights()

    def calculate_score(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        preferences: Preferences | None = None,
    ) -> tuple[int, MatchExplanation]:
        """Calculate match score (0-100) with detailed explanation."""
        skills_result = self._score_skills(resume=resume, job=job)
        experience_result = self._score_experience(resume=resume, job=job)
        location_result = self._score_location(
            resume=resume, job=job, preferences=preferences
        )
        salary_result = self._score_salary(job=job, preferences=preferences)
        culture_score = self._score_culture(resume=resume, job=job)

        total = int(
            skills_result[0] * self._weights.SKILLS
            + experience_result[0] * self._weights.EXPERIENCE
            + location_result[0] * self._weights.LOCATION
            + salary_result[0] * self._weights.SALARY
            + culture_score * self._weights.CULTURE
        )

        explanation = MatchExplanation(
            skills_score=skills_result[0],
            skills_matched=skills_result[1],
            skills_missing=skills_result[2],
            experience_score=experience_result[0],
            experience_gap=experience_result[1],
            location_score=location_result[0],
            location_match=location_result[1],
            salary_score=salary_result[0],
            salary_in_range=salary_result[1],
            culture_score=culture_score,
            overall_recommendation=self._get_recommendation(total),
        )

        return total, explanation

    def _score_skills(
        self,
        *,
        resume: ParsedResume,
        job: Job,
    ) -> tuple[int, list[str], list[str]]:
        """Score skill match, return (score, matched, missing)."""
        resume_skills = {s.lower() for s in resume.skills}
        required = {s.lower() for s in job.requirements.required_skills}
        preferred = {s.lower() for s in job.requirements.preferred_skills}

        matched_required = resume_skills & required
        matched_preferred = resume_skills & preferred
        missing_required = required - resume_skills

        if not required and not preferred:
            return 100, list(resume_skills), []

        required_pct = len(matched_required) / len(required) if required else 1.0
        preferred_pct = len(matched_preferred) / len(preferred) if preferred else 1.0

        # Required skills worth 70%, preferred 30%
        score = int((required_pct * 70) + (preferred_pct * 30))
        matched = list(matched_required | matched_preferred)
        missing = list(missing_required)

        return score, matched, missing

    def _score_experience(
        self,
        *,
        resume: ParsedResume,
        job: Job,
    ) -> tuple[int, str | None]:
        """Score experience match, return (score, gap description)."""
        years = resume.total_years_experience or 0
        min_years = job.requirements.experience_years_min or 0
        max_years = job.requirements.experience_years_max

        if years >= min_years:
            if max_years and years > max_years + 3:
                return 70, f"Overqualified ({years} years vs {max_years} max)"
            return 100, None

        gap = min_years - years
        if gap <= 1:
            return 80, f"Slightly under ({gap} year gap)"
        if gap <= 2:
            return 60, f"Under-experienced ({gap} year gap)"
        return 40, f"Significant gap ({gap} years needed)"

    def _score_location(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        preferences: Preferences | None,
    ) -> tuple[int, bool]:
        """Score location match, return (score, is_match)."""
        if job.remote:
            return 100, True

        if preferences and preferences.remote_only:
            return 0, False

        resume_loc = (resume.location or "").lower()
        job_loc = (job.location or "").lower()

        if not job_loc:
            return 100, True

        if resume_loc and job_loc in resume_loc:
            return 100, True

        if preferences and preferences.target_locations:
            for loc in preferences.target_locations:
                if loc.lower() in job_loc:
                    return 80, True

        return 50, False

    def _score_salary(
        self,
        *,
        job: Job,
        preferences: Preferences | None,
    ) -> tuple[int, bool | None]:
        """Score salary match, return (score, in_range or None if unknown)."""
        if not preferences or not preferences.salary_min:
            return 100, None

        if not job.salary_min and not job.salary_max:
            return 70, None  # Unknown, slight penalty

        job_max = job.salary_max or job.salary_min or 0

        if job_max >= preferences.salary_min:
            return 100, True

        gap_pct = (preferences.salary_min - job_max) / preferences.salary_min
        if gap_pct <= 0.1:
            return 80, False
        if gap_pct <= 0.2:
            return 60, False
        return 40, False

    def _score_culture(
        self,
        *,
        resume: ParsedResume,
        job: Job,
    ) -> int:
        """Score culture fit based on keywords and patterns."""
        # Simplified culture scoring - can be enhanced with NLP
        description_lower = job.description.lower()

        culture_keywords = [
            "collaborative",
            "innovative",
            "fast-paced",
            "startup",
            "enterprise",
            "remote-first",
            "work-life balance",
        ]

        matches = sum(1 for kw in culture_keywords if kw in description_lower)
        return min(100, 60 + (matches * 10))

    def _get_recommendation(self, score: int) -> str:
        """Get recommendation based on score."""
        if score >= 80:
            return "Strong match - highly recommended to apply"
        if score >= 60:
            return "Good match - worth applying"
        if score >= 40:
            return "Moderate match - consider if interested"
        return "Low match - may not be the best fit"
