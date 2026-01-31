"""Tests for application stage functionality.

Standards: python_clean.mdc
- pytest AAA pattern
- Fixtures for reusable setup
"""

from datetime import datetime

import pytest

from app.core.domain.application import (
    Application,
    ApplicationNote,
    ApplicationStage,
    ApplicationStatus,
)


class TestApplicationStage:
    """Tests for ApplicationStage enum."""

    def test_stage_values(self) -> None:
        """Verify all expected stage values exist."""
        # Arrange & Act
        stages = [s.value for s in ApplicationStage]

        # Assert
        assert "saved" in stages
        assert "applied" in stages
        assert "interviewing" in stages
        assert "offer" in stages
        assert "rejected" in stages

    def test_stage_from_value(self) -> None:
        """Test creating stage from string value."""
        # Arrange & Act
        stage = ApplicationStage("saved")

        # Assert
        assert stage == ApplicationStage.SAVED

    def test_invalid_stage_raises(self) -> None:
        """Test that invalid stage value raises error."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            ApplicationStage("invalid_stage")


class TestApplicationNote:
    """Tests for ApplicationNote dataclass."""

    def test_create_note(self) -> None:
        """Test creating an application note."""
        # Arrange & Act
        note = ApplicationNote(
            id="note-123",
            content="Follow up with recruiter",
            created_at=datetime(2026, 1, 31, 12, 0, 0),
        )

        # Assert
        assert note.id == "note-123"
        assert note.content == "Follow up with recruiter"
        assert note.created_at == datetime(2026, 1, 31, 12, 0, 0)

    def test_note_default_created_at(self) -> None:
        """Test that note has default created_at."""
        # Arrange & Act
        note = ApplicationNote(
            id="note-456",
            content="Test note",
        )

        # Assert
        assert note.created_at is not None
        assert isinstance(note.created_at, datetime)


class TestApplicationWithStage:
    """Tests for Application with stage field."""

    def test_application_default_stage(self) -> None:
        """Test that application defaults to SAVED stage."""
        # Arrange & Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
        )

        # Assert
        assert app.stage == ApplicationStage.SAVED

    def test_application_with_custom_stage(self) -> None:
        """Test creating application with custom stage."""
        # Arrange & Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
            stage=ApplicationStage.INTERVIEWING,
        )

        # Assert
        assert app.stage == ApplicationStage.INTERVIEWING

    def test_application_with_notes(self) -> None:
        """Test application with notes."""
        # Arrange
        notes = [
            ApplicationNote(id="n1", content="First note"),
            ApplicationNote(id="n2", content="Second note"),
        ]

        # Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
            notes=notes,
        )

        # Assert
        assert len(app.notes) == 2
        assert app.notes[0].content == "First note"
        assert app.notes[1].content == "Second note"

    def test_application_default_empty_notes(self) -> None:
        """Test that application defaults to empty notes list."""
        # Arrange & Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
        )

        # Assert
        assert app.notes == []

    def test_application_stage_updated_at(self) -> None:
        """Test application stage_updated_at field."""
        # Arrange
        updated_at = datetime(2026, 1, 31, 14, 0, 0)

        # Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
            stage_updated_at=updated_at,
        )

        # Assert
        assert app.stage_updated_at == updated_at

    def test_application_stage_updated_at_default_none(self) -> None:
        """Test stage_updated_at defaults to None."""
        # Arrange & Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
        )

        # Assert
        assert app.stage_updated_at is None

    def test_application_status_and_stage_independent(self) -> None:
        """Test that status and stage are independent fields."""
        # Arrange & Act
        app = Application(
            id="app-123",
            user_id="user-456",
            job_id="job-789",
            resume_id="resume-111",
            status=ApplicationStatus.SUBMITTED,
            stage=ApplicationStage.APPLIED,
        )

        # Assert
        assert app.status == ApplicationStatus.SUBMITTED
        assert app.stage == ApplicationStage.APPLIED
