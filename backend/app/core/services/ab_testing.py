"""A/B testing service for resumes.

Standards: python_clean.mdc
- Statistical significance testing
- Dataclass results
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random

import structlog

logger = structlog.get_logger(__name__)


class ABTestStatus(str, Enum):
    """A/B test status."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    INCONCLUSIVE = "inconclusive"


@dataclass
class ResumeVariant:
    """Resume variant in an A/B test."""

    resume_id: str
    name: str  # "Variant A", "Variant B"
    applications: int = 0
    interviews: int = 0
    offers: int = 0
    response_rate: float = 0.0


@dataclass
class ABTestResult:
    """Result of an A/B test."""

    test_id: str
    variant_a: ResumeVariant
    variant_b: ResumeVariant
    winner: str | None  # "A", "B", or None if inconclusive
    confidence: float  # Statistical confidence (0-100%)
    improvement: float  # Percentage improvement of winner over loser
    is_significant: bool  # Whether result is statistically significant


@dataclass
class ResumeABTest:
    """A/B test for comparing two resume variants."""

    id: str
    user_id: str
    name: str
    resume_a_id: str
    resume_b_id: str
    status: ABTestStatus

    # Metrics
    applications_a: int = 0
    applications_b: int = 0
    interviews_a: int = 0
    interviews_b: int = 0
    offers_a: int = 0
    offers_b: int = 0

    # Configuration
    min_applications: int = 20  # Min applications before declaring winner
    confidence_threshold: float = 95.0  # Required confidence %

    winner: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class ABTestingService:
    """Service for A/B testing resume variants."""

    def __init__(self, *, test_repository) -> None:
        """Initialize A/B testing service.

        Args:
            test_repository: Repository for A/B tests
        """
        self._test_repo = test_repository

    def select_variant(self, test: ResumeABTest) -> str:
        """Select which resume variant to use for an application.

        Uses simple random assignment for fair testing.

        Args:
            test: The A/B test

        Returns:
            "A" or "B" indicating selected variant
        """
        return "A" if random.random() < 0.5 else "B"

    def record_application(
        self,
        *,
        test: ResumeABTest,
        variant: str,
    ) -> ResumeABTest:
        """Record an application for a variant.

        Args:
            test: The A/B test
            variant: "A" or "B"

        Returns:
            Updated test
        """
        if variant == "A":
            test.applications_a += 1
        else:
            test.applications_b += 1

        return test

    def record_interview(
        self,
        *,
        test: ResumeABTest,
        variant: str,
    ) -> ResumeABTest:
        """Record an interview for a variant.

        Args:
            test: The A/B test
            variant: "A" or "B"

        Returns:
            Updated test
        """
        if variant == "A":
            test.interviews_a += 1
        else:
            test.interviews_b += 1

        return test

    def analyze_results(self, test: ResumeABTest) -> ABTestResult:
        """Analyze A/B test results.

        Args:
            test: The A/B test

        Returns:
            ABTestResult with statistical analysis
        """
        # Calculate response rates
        rate_a = (test.interviews_a / test.applications_a * 100) if test.applications_a > 0 else 0.0
        rate_b = (test.interviews_b / test.applications_b * 100) if test.applications_b > 0 else 0.0

        variant_a = ResumeVariant(
            resume_id=test.resume_a_id,
            name="Variant A",
            applications=test.applications_a,
            interviews=test.interviews_a,
            offers=test.offers_a,
            response_rate=rate_a,
        )

        variant_b = ResumeVariant(
            resume_id=test.resume_b_id,
            name="Variant B",
            applications=test.applications_b,
            interviews=test.interviews_b,
            offers=test.offers_b,
            response_rate=rate_b,
        )

        # Check if we have enough data
        total_applications = test.applications_a + test.applications_b
        if total_applications < test.min_applications:
            return ABTestResult(
                test_id=test.id,
                variant_a=variant_a,
                variant_b=variant_b,
                winner=None,
                confidence=0.0,
                improvement=0.0,
                is_significant=False,
            )

        # Calculate statistical significance
        confidence = self._calculate_confidence(
            n1=test.applications_a,
            n2=test.applications_b,
            p1=rate_a / 100,
            p2=rate_b / 100,
        )

        # Determine winner
        winner = None
        improvement = 0.0
        is_significant = confidence >= test.confidence_threshold

        if is_significant:
            if rate_a > rate_b:
                winner = "A"
                improvement = ((rate_a - rate_b) / rate_b * 100) if rate_b > 0 else 0.0
            elif rate_b > rate_a:
                winner = "B"
                improvement = ((rate_b - rate_a) / rate_a * 100) if rate_a > 0 else 0.0

        logger.info(
            "ab_test_analyzed",
            test_id=test.id,
            winner=winner,
            confidence=confidence,
            is_significant=is_significant,
        )

        return ABTestResult(
            test_id=test.id,
            variant_a=variant_a,
            variant_b=variant_b,
            winner=winner,
            confidence=confidence,
            improvement=improvement,
            is_significant=is_significant,
        )

    def _calculate_confidence(
        self,
        *,
        n1: int,
        n2: int,
        p1: float,
        p2: float,
    ) -> float:
        """Calculate statistical confidence using z-test.

        Args:
            n1: Sample size for variant A
            n2: Sample size for variant B
            p1: Conversion rate for variant A
            p2: Conversion rate for variant B

        Returns:
            Confidence level (0-100%)
        """
        import math

        if n1 == 0 or n2 == 0:
            return 0.0

        # Pooled proportion
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)

        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))

        if se == 0:
            return 0.0

        # Z-score
        z = abs(p1 - p2) / se

        # Convert z-score to confidence (simplified)
        # Using approximation for standard normal CDF
        confidence = (1 - math.exp(-0.717 * z - 0.416 * z * z)) * 100

        return min(99.9, max(0.0, confidence))

    def should_conclude_test(self, test: ResumeABTest) -> bool:
        """Check if test should be concluded.

        Args:
            test: The A/B test

        Returns:
            True if test should be concluded
        """
        total = test.applications_a + test.applications_b

        # Conclude if we have enough applications and statistical significance
        if total >= test.min_applications:
            result = self.analyze_results(test)
            return result.is_significant

        # Also conclude if test has been running too long (30 days max)
        days_running = (datetime.utcnow() - test.created_at).days
        if days_running >= 30:
            return True

        return False
