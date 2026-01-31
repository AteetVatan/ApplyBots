"""Tests for match scoring service.

Standards: python_clean.mdc
- AAA pattern (Arrange, Act, Assert)
- Descriptive test names
"""

import pytest

from app.core.domain.job import Job, JobRequirements, JobSource
from app.core.domain.profile import Preferences
from app.core.domain.resume import ParsedResume
from app.core.services.matcher import MatchService


class TestMatchService:
    """Tests for MatchService."""

    def test_calculate_score_perfect_match(
        self,
        sample_resume: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test scoring with perfect skill match."""
        # Arrange
        service = MatchService()

        # Act
        score, explanation = service.calculate_score(
            resume=sample_resume,
            job=sample_job,
        )

        # Assert
        assert score >= 70  # Should be high match
        assert len(explanation.skills_matched) > 0
        assert "Python" in explanation.skills_matched

    def test_calculate_score_no_skills_match(self) -> None:
        """Test scoring with no matching skills."""
        # Arrange
        service = MatchService()
        resume = ParsedResume(
            full_name="Jane Doe",
            skills=["Java", "Spring", "Oracle"],
            total_years_experience=5.0,
        )
        job = Job(
            id="job-123",
            external_id="ext-123",
            title="Python Developer",
            company="Example Co",
            source=JobSource.MANUAL,
            requirements=JobRequirements(
                required_skills=["Python", "Django", "PostgreSQL"],
            ),
        )

        # Act
        score, explanation = service.calculate_score(
            resume=resume,
            job=job,
        )

        # Assert
        assert score < 50  # Should be low match
        assert len(explanation.skills_missing) == 3
        assert "Python" in explanation.skills_missing

    def test_calculate_score_experience_gap(self) -> None:
        """Test scoring with experience gap."""
        # Arrange
        service = MatchService()
        resume = ParsedResume(
            full_name="Junior Dev",
            skills=["Python", "FastAPI"],
            total_years_experience=1.0,
        )
        job = Job(
            id="job-456",
            external_id="ext-456",
            title="Senior Engineer",
            company="Example Co",
            source=JobSource.MANUAL,
            requirements=JobRequirements(
                required_skills=["Python"],
                experience_years_min=5,
            ),
        )

        # Act
        score, explanation = service.calculate_score(
            resume=resume,
            job=job,
        )

        # Assert
        assert explanation.experience_gap is not None
        assert "gap" in explanation.experience_gap.lower()

    def test_calculate_score_with_preferences(self) -> None:
        """Test scoring considers user preferences."""
        # Arrange
        service = MatchService()
        resume = ParsedResume(
            full_name="Remote Dev",
            skills=["Python"],
            total_years_experience=3.0,
        )
        job = Job(
            id="job-789",
            external_id="ext-789",
            title="Python Developer",
            company="Office Co",
            location="New York, NY",
            remote=False,
            source=JobSource.MANUAL,
            requirements=JobRequirements(required_skills=["Python"]),
        )
        preferences = Preferences(
            remote_only=True,
        )

        # Act
        score, explanation = service.calculate_score(
            resume=resume,
            job=job,
            preferences=preferences,
        )

        # Assert
        assert explanation.location_match is False
        assert explanation.location_score == 0

    def test_calculate_score_recommendation_strong(
        self,
        sample_resume: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test recommendation text for strong match."""
        # Arrange
        service = MatchService()

        # Act
        score, explanation = service.calculate_score(
            resume=sample_resume,
            job=sample_job,
        )

        # Assert
        if score >= 80:
            assert "Strong match" in explanation.overall_recommendation
        elif score >= 60:
            assert "Good match" in explanation.overall_recommendation
