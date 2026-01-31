"""Pytest fixtures for testing.

Standards: python_clean.mdc
- Fixtures for reusable test setup
- Async fixtures for database testing
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.domain.job import Job, JobRequirements, JobSource
from app.core.domain.resume import ParsedResume
from app.core.domain.user import User
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id="test-user-123",
        email="test@example.com",
        password_hash="$2b$12$hashed_password",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_resume() -> ParsedResume:
    """Create a sample parsed resume for testing."""
    return ParsedResume(
        full_name="John Doe",
        email="john@example.com",
        phone="+1 555-123-4567",
        location="San Francisco, CA",
        summary="Experienced software engineer",
        skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS"],
        total_years_experience=5.0,
    )


@pytest.fixture
def sample_job() -> Job:
    """Create a sample job for testing."""
    return Job(
        id="test-job-123",
        external_id="remotive_12345",
        title="Senior Software Engineer",
        company="TechCorp Inc.",
        location="Remote",
        description="We are looking for a senior engineer with Python experience.",
        url="https://jobs.example.com/123",
        source=JobSource.REMOTIVE,
        remote=True,
        requirements=JobRequirements(
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            preferred_skills=["Docker", "AWS", "React"],
            experience_years_min=3,
            experience_years_max=7,
        ),
        posted_at=datetime.utcnow(),
        ingested_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    mock = AsyncMock()
    mock.get_by_id.return_value = None
    mock.get_by_email.return_value = None
    mock.create.return_value = None
    mock.update.return_value = None
    return mock


@pytest.fixture
def mock_file_storage():
    """Create a mock file storage."""
    mock = AsyncMock()
    mock.upload.return_value = "https://storage.example.com/file.pdf"
    mock.download.return_value = b"file content"
    mock.delete.return_value = None
    mock.exists.return_value = True
    return mock
