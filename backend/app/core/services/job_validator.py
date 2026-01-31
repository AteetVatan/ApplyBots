"""Job validation and scam detection service.

Standards: python_clean.mdc
- Rule-based validation
- Pattern matching for scam detection
"""

from dataclasses import dataclass, field
from enum import Enum

import structlog

from app.core.domain.job import Job

logger = structlog.get_logger(__name__)


class ValidationFlag(str, Enum):
    """Validation flag types."""

    SCAM_INDICATOR = "scam_indicator"
    SUSPICIOUS = "suspicious"
    LOW_QUALITY = "low_quality"
    UNVERIFIED_COMPANY = "unverified_company"
    MISSING_INFO = "missing_info"


@dataclass
class ValidationIssue:
    """A validation issue found in a job listing."""

    flag: ValidationFlag
    message: str
    severity: int  # 1-10, higher is worse


@dataclass
class ValidationResult:
    """Result of job validation."""

    job_id: str
    score: int  # 0-100, higher is better
    is_verified: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    passed: bool = True


# Scam indicators - phrases commonly found in scam job postings
SCAM_INDICATORS = [
    "wire transfer",
    "money order",
    "send money",
    "western union",
    "work from home $",
    "make $5000/week",
    "no experience needed",
    "unlimited income",
    "be your own boss",
    "financial freedom",
    "get rich quick",
    "easy money",
    "processing fees",
    "upfront payment",
    "pay to apply",
    "send your bank details",
    "social security number",
    "immediate start guaranteed",
    "mlm",
    "multi-level marketing",
    "pyramid",
    "recruitment bonus",
]

# Suspicious patterns
SUSPICIOUS_PATTERNS = [
    "gmail.com",  # Company using Gmail for business
    "yahoo.com",
    "hotmail.com",
    "no interview needed",
    "hiring immediately no questions",
    "too good to be true",
    "guaranteed income",
    "risk free",
    "secret shopper",
    "envelope stuffing",
    "data entry from home $",
    "click ads for money",
]

# Low quality indicators
LOW_QUALITY_INDICATORS = [
    "multiple exclamation marks!!!",
    "ALL CAPS",
    "💰💰💰",
    "🔥🔥🔥",
    "urgent!!!",
    "limited time",
]


class JobValidatorService:
    """Service for validating job listings and detecting scams.

    Analyzes job postings for red flags and quality indicators.
    """

    def validate(self, job: Job) -> ValidationResult:
        """Validate a job listing.

        Args:
            job: Job to validate

        Returns:
            ValidationResult with score and issues
        """
        issues: list[ValidationIssue] = []
        score = 100

        # Check for scam indicators
        scam_issues, scam_penalty = self._check_scam_indicators(job)
        issues.extend(scam_issues)
        score -= scam_penalty

        # Check for suspicious patterns
        suspicious_issues, suspicious_penalty = self._check_suspicious_patterns(job)
        issues.extend(suspicious_issues)
        score -= suspicious_penalty

        # Check for low quality content
        quality_issues, quality_penalty = self._check_quality(job)
        issues.extend(quality_issues)
        score -= quality_penalty

        # Check for missing information
        missing_issues, missing_penalty = self._check_missing_info(job)
        issues.extend(missing_issues)
        score -= missing_penalty

        # Normalize score
        score = max(0, min(100, score))

        # Determine if job passes validation
        is_verified = score >= 70
        passed = score >= 50  # Minimum threshold

        logger.info(
            "job_validated",
            job_id=job.id,
            score=score,
            issues_count=len(issues),
            passed=passed,
        )

        return ValidationResult(
            job_id=job.id,
            score=score,
            is_verified=is_verified,
            issues=issues,
            passed=passed,
        )

    def _check_scam_indicators(
        self,
        job: Job,
    ) -> tuple[list[ValidationIssue], int]:
        """Check for scam indicators in job listing."""
        issues = []
        penalty = 0

        text_to_check = (
            f"{job.title} {job.description} {job.company}"
        ).lower()

        for indicator in SCAM_INDICATORS:
            if indicator in text_to_check:
                issues.append(
                    ValidationIssue(
                        flag=ValidationFlag.SCAM_INDICATOR,
                        message=f"Contains scam indicator: '{indicator}'",
                        severity=9,
                    )
                )
                penalty += 20  # High penalty for scam indicators

        return issues, penalty

    def _check_suspicious_patterns(
        self,
        job: Job,
    ) -> tuple[list[ValidationIssue], int]:
        """Check for suspicious patterns."""
        issues = []
        penalty = 0

        text_to_check = (
            f"{job.title} {job.description} {job.company}"
        ).lower()

        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in text_to_check:
                issues.append(
                    ValidationIssue(
                        flag=ValidationFlag.SUSPICIOUS,
                        message=f"Contains suspicious pattern: '{pattern}'",
                        severity=5,
                    )
                )
                penalty += 10

        return issues, penalty

    def _check_quality(
        self,
        job: Job,
    ) -> tuple[list[ValidationIssue], int]:
        """Check content quality."""
        issues = []
        penalty = 0

        description = job.description or ""

        # Check for excessive punctuation
        if "!!!" in description or "???" in description:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.LOW_QUALITY,
                    message="Excessive punctuation suggests low quality",
                    severity=3,
                )
            )
            penalty += 5

        # Check for all caps sections
        words = description.split()
        caps_words = sum(1 for w in words if w.isupper() and len(w) > 3)
        if caps_words > 5:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.LOW_QUALITY,
                    message="Excessive use of capital letters",
                    severity=3,
                )
            )
            penalty += 5

        # Check for very short descriptions
        if len(description) < 100:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.LOW_QUALITY,
                    message="Job description is too short",
                    severity=4,
                )
            )
            penalty += 10

        # Check for excessive emojis
        emoji_count = sum(1 for c in description if ord(c) > 0x1F300)
        if emoji_count > 5:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.LOW_QUALITY,
                    message="Excessive use of emojis",
                    severity=2,
                )
            )
            penalty += 5

        return issues, penalty

    def _check_missing_info(
        self,
        job: Job,
    ) -> tuple[list[ValidationIssue], int]:
        """Check for missing important information."""
        issues = []
        penalty = 0

        # Check for missing company name
        if not job.company or job.company.lower() in ["unknown", "n/a", ""]:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.MISSING_INFO,
                    message="Company name is missing",
                    severity=6,
                )
            )
            penalty += 15

        # Check for missing description
        if not job.description or len(job.description) < 50:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.MISSING_INFO,
                    message="Job description is missing or too short",
                    severity=5,
                )
            )
            penalty += 10

        # Check for missing URL
        if not job.url:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.MISSING_INFO,
                    message="Job application URL is missing",
                    severity=7,
                )
            )
            penalty += 15

        # Check for missing location
        if not job.location or job.location.lower() in ["unknown", "n/a", ""]:
            issues.append(
                ValidationIssue(
                    flag=ValidationFlag.MISSING_INFO,
                    message="Job location is not specified",
                    severity=3,
                )
            )
            penalty += 5

        return issues, penalty

    def filter_verified_jobs(
        self,
        jobs: list[Job],
        *,
        min_score: int = 70,
    ) -> list[Job]:
        """Filter jobs to only include verified ones.

        Args:
            jobs: List of jobs to filter
            min_score: Minimum validation score required

        Returns:
            List of verified jobs
        """
        verified = []

        for job in jobs:
            result = self.validate(job)
            if result.score >= min_score:
                verified.append(job)

        logger.info(
            "jobs_filtered",
            total=len(jobs),
            verified=len(verified),
            min_score=min_score,
        )

        return verified
