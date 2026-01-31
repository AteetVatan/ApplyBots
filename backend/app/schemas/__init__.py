"""Pydantic schemas for API request/response validation."""

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenPayload,
)
from app.schemas.profile import (
    PreferencesResponse,
    PreferencesUpdate,
    ProfileResponse,
    ProfileUpdate,
    ResumeResponse,
)
from app.schemas.job import (
    JobDetailResponse,
    JobFilters,
    JobListResponse,
    MatchAnalysis,
)
from app.schemas.application import (
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApproveRequest,
    CreateApplicationRequest,
    EditApplicationRequest,
)
from app.schemas.agent import (
    AgentMessage,
    BulkApplyRequest,
    ChatRequest,
    ChatResponse,
    OptimizeRequest,
    OptimizeResponse,
)
from app.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PlansResponse,
    PortalResponse,
    UsageResponse,
)

__all__ = [
    # Auth
    "AuthResponse",
    "LoginRequest",
    "RefreshRequest",
    "SignupRequest",
    "TokenPayload",
    # Profile
    "PreferencesResponse",
    "PreferencesUpdate",
    "ProfileResponse",
    "ProfileUpdate",
    "ResumeResponse",
    # Jobs
    "JobDetailResponse",
    "JobFilters",
    "JobListResponse",
    "MatchAnalysis",
    # Applications
    "ApplicationDetailResponse",
    "ApplicationListResponse",
    "ApproveRequest",
    "CreateApplicationRequest",
    "EditApplicationRequest",
    # Agents
    "AgentMessage",
    "BulkApplyRequest",
    "ChatRequest",
    "ChatResponse",
    "OptimizeRequest",
    "OptimizeResponse",
    # Billing
    "CheckoutRequest",
    "CheckoutResponse",
    "PlansResponse",
    "PortalResponse",
    "UsageResponse",
]
