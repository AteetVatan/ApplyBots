"""Tests for truth-lock verification service.

Standards: python_clean.mdc
- AAA pattern
- Test edge cases
"""

import pytest

from app.core.domain.job import Job, JobRequirements, JobSource
from app.core.domain.resume import ParsedResume, WorkExperience, Education
from app.core.exceptions import TruthLockViolationError
from app.core.services.truth_lock import TruthLockVerifier


class TestTruthLockVerifier:
    """Tests for TruthLockVerifier."""

    @pytest.fixture
    def verifier(self) -> TruthLockVerifier:
        """Create verifier instance."""
        return TruthLockVerifier()

    @pytest.fixture
    def resume_with_experience(self) -> ParsedResume:
        """Create a resume with work experience."""
        return ParsedResume(
            full_name="John Doe",
            skills=["Python", "FastAPI", "Docker"],
            work_experience=[
                WorkExperience(
                    company="TechCorp",
                    title="Software Engineer",
                    start_date="2020-01",
                    end_date="2023-06",
                ),
            ],
            education=[
                Education(
                    institution="State University",
                    degree="Bachelor of Science",
                    field_of_study="Computer Science",
                ),
            ],
            total_years_experience=3.5,
        )

    @pytest.fixture
    def sample_job(self) -> Job:
        """Create a sample job."""
        return Job(
            id="job-123",
            external_id="ext-123",
            title="Python Developer",
            company="NewCorp",
            source=JobSource.MANUAL,
            requirements=JobRequirements(
                required_skills=["Python", "FastAPI"],
            ),
        )

    def test_verify_valid_content(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test verification passes for valid content."""
        # Arrange
        content = """
        I have 3 years of experience in software engineering.
        At TechCorp, I developed Python applications using FastAPI.
        I hold a Bachelor of Science in Computer Science.
        """

        # Act
        result = verifier.verify(
            content=content,
            resume=resume_with_experience,
            job=sample_job,
        )

        # Assert
        assert result.passed is True
        assert len(result.violations) == 0

    def test_verify_inflated_experience(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test detection of inflated experience claims."""
        # Arrange
        content = """
        I have 10 years of experience in Python development.
        """

        # Act
        result = verifier.verify(
            content=content,
            resume=resume_with_experience,
            job=sample_job,
        )

        # Assert
        assert result.passed is False
        assert len(result.violations) > 0
        assert any("years" in v.lower() for v in result.violations)

    def test_verify_fabricated_company(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test detection of fabricated company names."""
        # Arrange
        content = """
        At Google, I led a team of engineers developing Python applications.
        """

        # Act
        result = verifier.verify(
            content=content,
            resume=resume_with_experience,
            job=sample_job,
        )

        # Assert
        assert result.passed is False
        assert len(result.violations) > 0
        assert any("Google" in v for v in result.violations)

    def test_verify_fabricated_degree(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test detection of fabricated education."""
        # Arrange
        content = """
        With my PhD in Machine Learning from MIT, I bring expertise.
        """

        # Act
        result = verifier.verify(
            content=content,
            resume=resume_with_experience,
            job=sample_job,
        )

        # Assert
        assert result.passed is False
        assert len(result.violations) > 0

    def test_verify_or_raise_throws_on_violation(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test that verify_or_raise throws TruthLockViolationError."""
        # Arrange
        content = "I have 15 years of experience as a tech lead at Amazon."

        # Act & Assert
        with pytest.raises(TruthLockViolationError) as exc_info:
            verifier.verify_or_raise(
                content=content,
                resume=resume_with_experience,
                job=sample_job,
            )

        assert len(exc_info.value.violations) > 0

    def test_verify_skill_warning_not_violation(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test that skill claims generate warnings, not violations."""
        # Arrange - mention a skill from job req not in resume
        sample_job.requirements.required_skills.append("Kubernetes")
        content = """
        I am proficient in Kubernetes for container orchestration.
        """

        # Act
        result = verifier.verify(
            content=content,
            resume=resume_with_experience,
            job=sample_job,
        )

        # Assert - should be warning, not blocking violation
        assert len(result.warnings) > 0
        assert any("kubernetes" in w.lower() for w in result.warnings)

    def test_extract_verified_claims(
        self,
        verifier: TruthLockVerifier,
        resume_with_experience: ParsedResume,
        sample_job: Job,
    ) -> None:
        """Test extraction of verified claims."""
        # Arrange
        content = """
        At TechCorp, I used Python extensively with FastAPI.
        """

        # Act
        result = verifier.verify(
            content=content,
            resume=resume_with_experience,
            job=sample_job,
        )

        # Assert
        assert len(result.verified_claims) > 0
        assert any("TechCorp" in c for c in result.verified_claims)
