"""Agent schemas.

Standards: python_clean.mdc
- Pydantic for validation
- Explicit types
"""

from datetime import datetime

from pydantic import BaseModel


class AgentMessage(BaseModel):
    """Message in agent conversation."""

    role: str  # "user", "assistant", or specific agent name
    content: str
    timestamp: datetime | None = None


class ChatRequest(BaseModel):
    """Request to chat with agents."""

    message: str
    session_id: str | None = None  # Continue existing session


class ChatResponse(BaseModel):
    """Response from agent chat."""

    message: str
    session_id: str
    agents_involved: list[str]
    actions_taken: list[str]


class OptimizeRequest(BaseModel):
    """Request to optimize resume for a job."""

    resume_id: str
    job_id: str


class OptimizeResponse(BaseModel):
    """Response from resume optimization."""

    original_match_score: int
    optimized_match_score: int
    suggestions: list[str]
    tailored_summary: str | None
    highlighted_skills: list[str]


class BulkApplyRequest(BaseModel):
    """Request to bulk apply to multiple jobs."""

    job_ids: list[str]
    resume_id: str | None = None  # Uses primary resume if not specified
    auto_submit: bool = False  # If True, skip review queue
