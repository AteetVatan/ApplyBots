"""Truth-lock verification service.

Standards: python_clean.mdc
- Pure business logic
- Prevent hallucinations in generated content
"""

import re
from dataclasses import dataclass

from app.core.domain.job import Job
from app.core.domain.resume import ParsedResume
from app.core.exceptions import TruthLockViolationError


@dataclass
class VerificationResult:
    """Result of truth-lock verification."""

    passed: bool
    violations: list[str]
    warnings: list[str]
    verified_claims: list[str]


class TruthLockVerifier:
    """Verify generated content against source documents.

    Ensures AI-generated cover letters and answers don't contain
    fabricated claims not supported by the resume or job description.
    """

    # Common patterns that indicate potential fabrications
    YEARS_PATTERN = re.compile(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", re.IGNORECASE)
    COMPANY_PATTERN = re.compile(r"(?:at|with|for)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+for|\s+where|,|\.)", re.IGNORECASE)
    DEGREE_PATTERN = re.compile(r"(bachelor|master|phd|doctorate|mba|bs|ms|ba|ma)\s+(?:in|of)?\s*([a-zA-Z\s]+)", re.IGNORECASE)
    SKILL_CLAIM_PATTERN = re.compile(r"(?:proficient|expert|experienced|skilled)\s+(?:in|with)\s+([a-zA-Z\s,]+)", re.IGNORECASE)

    def verify(
        self,
        *,
        content: str,
        resume: ParsedResume,
        job: Job,
    ) -> VerificationResult:
        """Verify content against resume and job description.

        Args:
            content: Generated content to verify
            resume: Source resume data
            job: Job being applied to

        Returns:
            VerificationResult with pass/fail and details
        """
        violations: list[str] = []
        warnings: list[str] = []
        verified: list[str] = []

        # Check years of experience claims
        years_violations = self._verify_experience_years(
            content=content, resume=resume
        )
        violations.extend(years_violations)

        # Check company name claims
        company_violations = self._verify_companies(content=content, resume=resume)
        violations.extend(company_violations)

        # Check education claims
        education_violations = self._verify_education(content=content, resume=resume)
        violations.extend(education_violations)

        # Check skill claims
        skill_warnings = self._verify_skills(
            content=content, resume=resume, job=job
        )
        warnings.extend(skill_warnings)

        # Track verified claims
        verified = self._extract_verified_claims(
            content=content, resume=resume, job=job
        )

        return VerificationResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            verified_claims=verified,
        )

    def verify_or_raise(
        self,
        *,
        content: str,
        resume: ParsedResume,
        job: Job,
    ) -> VerificationResult:
        """Verify content and raise if violations found."""
        result = self.verify(content=content, resume=resume, job=job)

        if not result.passed:
            raise TruthLockViolationError(result.violations)

        return result

    def _verify_experience_years(
        self,
        *,
        content: str,
        resume: ParsedResume,
    ) -> list[str]:
        """Verify years of experience claims."""
        violations = []
        matches = self.YEARS_PATTERN.findall(content)

        resume_years = resume.total_years_experience or 0

        for claimed_years in matches:
            claimed = int(claimed_years)
            # Allow 1 year tolerance for rounding
            if claimed > resume_years + 1:
                violations.append(
                    f"Claimed {claimed} years experience but resume shows ~{resume_years:.0f} years"
                )

        return violations

    def _verify_companies(
        self,
        *,
        content: str,
        resume: ParsedResume,
    ) -> list[str]:
        """Verify company name claims."""
        violations = []
        resume_companies = {
            exp.company.lower() for exp in resume.work_experience
        }

        matches = self.COMPANY_PATTERN.findall(content)

        for company in matches:
            company_lower = company.strip().lower()
            # Check if company is in resume (fuzzy match)
            if not any(company_lower in rc or rc in company_lower for rc in resume_companies):
                # Could be referring to target company
                violations.append(f"Company '{company.strip()}' not found in resume")

        return violations

    def _verify_education(
        self,
        *,
        content: str,
        resume: ParsedResume,
    ) -> list[str]:
        """Verify education claims."""
        violations = []
        resume_degrees = {
            (edu.degree.lower(), edu.field_of_study.lower() if edu.field_of_study else "")
            for edu in resume.education
        }

        matches = self.DEGREE_PATTERN.findall(content)

        for degree_type, field in matches:
            degree_lower = degree_type.lower()
            field_lower = field.strip().lower()

            # Check if claimed degree exists in resume
            found = any(
                degree_lower in rd[0] or rd[0] in degree_lower
                for rd in resume_degrees
            )

            if not found:
                violations.append(
                    f"Claimed degree '{degree_type} in {field.strip()}' not found in resume"
                )

        return violations

    def _verify_skills(
        self,
        *,
        content: str,
        resume: ParsedResume,
        job: Job,
    ) -> list[str]:
        """Verify skill claims - returns warnings not violations."""
        warnings = []
        resume_skills = {s.lower() for s in resume.skills}
        job_skills = {
            s.lower()
            for s in job.requirements.required_skills + job.requirements.preferred_skills
        }

        matches = self.SKILL_CLAIM_PATTERN.findall(content)

        for skill_text in matches:
            skills = [s.strip().lower() for s in skill_text.split(",")]
            for skill in skills:
                if skill and skill not in resume_skills:
                    if skill in job_skills:
                        warnings.append(
                            f"Skill '{skill}' claimed but not in resume (is in job requirements)"
                        )

        return warnings

    def _extract_verified_claims(
        self,
        *,
        content: str,
        resume: ParsedResume,
        job: Job,
    ) -> list[str]:
        """Extract claims that are verified by source documents."""
        verified = []

        # Add verified skills
        resume_skills = {s.lower() for s in resume.skills}
        for skill in resume_skills:
            if skill.lower() in content.lower():
                verified.append(f"Skill: {skill}")

        # Add verified companies
        for exp in resume.work_experience:
            if exp.company.lower() in content.lower():
                verified.append(f"Company: {exp.company}")

        return verified
