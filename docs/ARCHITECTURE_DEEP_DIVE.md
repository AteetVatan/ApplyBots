# ApplyBots - Complete Architecture & Technology Deep Dive

> **For Beginners**: This document explains every module, technology, and concept used in the ApplyBots application in simple terms.

---

## 📖 Table of Contents

1. [What is ApplyBots?](#what-is-applybots)
2. [High-Level Architecture](#high-level-architecture)
3. [Technology Stack Overview](#technology-stack-overview)
4. [Backend Deep Dive](#backend-deep-dive)
   - [Project Structure](#backend-project-structure)
   - [Core Layer (Business Logic)](#core-layer-business-logic)
   - [Infrastructure Layer (IO & External Services)](#infrastructure-layer)
   - [API Layer (REST Endpoints)](#api-layer)
   - [Agents Module (AI Orchestration)](#agents-module)
   - [Workers Module (Background Tasks)](#workers-module)
5. [Frontend Deep Dive](#frontend-deep-dive)
6. [Infrastructure Services](#infrastructure-services)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Security & Best Practices](#security--best-practices)
9. [Glossary](#glossary)

---

## What is ApplyBots?

ApplyBots is an **AI-powered job application platform** that helps job seekers:

1. **Discover Jobs** - Automatically finds and matches jobs to your profile from multiple sources
2. **Generate Applications** - Creates tailored cover letters and answers using AI
3. **Submit Applications** - Automates form filling on job application portals
4. **Track Everything** - Maintains complete audit trails and screenshots with Kanban-style tracking
5. **Career Tools** - Interview roleplay, offer negotiation analysis, and career path planning
6. **Company Intelligence** - Research companies before applying with news, financials, and hiring signals
7. **Gamification** - Streaks, achievements, and wellness features to stay motivated

### Key Principle: Truth-Lock Technology

The platform **NEVER fabricates information**. All AI-generated content is verified against your actual resume to ensure 100% truthfulness.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                     │
│                    (Browser - Next.js 16 Frontend)                          │
│   ┌─────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ ┌─────────────────────┐│
│   │  Auth   │ │ Dashboard │ │  Jobs  │ │ Resumes  │ │    Career Tools     ││
│   │ (OAuth) │ │  (Kanban) │ │  List  │ │ Builder  │ │Interview|Nego|Paths ││
│   └─────────┘ └───────────┘ └────────┘ └──────────┘ └─────────────────────┘│
│   ┌─────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ ┌─────────────────────┐│
│   │Campaigns│ │ AI Chat   │ │ Alerts │ │Gamificat.│ │ Company Intel       ││
│   └─────────┘ └───────────┘ └────────┘ └──────────┘ └─────────────────────┘│
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTP/REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                          │
│                  (FastAPI Backend + Rate Limiting)                          │
│ ┌────────┐ ┌─────────┐ ┌──────┐ ┌─────────────┐ ┌─────────┐ ┌────────────┐│
│ │ /auth  │ │/resumes │ │/jobs │ │/applications│ │/agents  │ │  /tools    ││
│ └────────┘ └─────────┘ └──────┘ └─────────────┘ └─────────┘ └────────────┘│
│ ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌───────────┐ ┌────────────┐│
│ │/campaigns│ │/resume-build │ │/gamificat. │ │/wellness  │ │/company    ││
│ └──────────┘ └──────────────┘ └────────────┘ └───────────┘ └────────────┘│
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   AI AGENTS     │   │  BACKGROUND     │   │  DATA LAYER     │
│ (AutoGen Group  │   │  WORKERS        │   │                 │
│     Chat)       │   │  (Celery)       │   │  PostgreSQL     │
│  ┌───────────┐  │   │                 │   │  Redis          │
│  │Orchestrate│  │   │  Job Ingestion  │   │  MinIO (S3)     │
│  │ Resume    │  │   │  App Submitter  │   │  ChromaDB       │
│  │ Match     │  │   │  Alert Generate │   │                 │
│  │ Apply     │  │   │  Status Monitor │   │                 │
│  │ QC/Critic │  │   └─────────────────┘   └─────────────────┘
│  └───────────┘  │           │
└─────────────────┘           ▼
         │            ┌─────────────────┐
         │            │  EXTERNAL APIs  │
         └───────────>│  Together AI    │
                      │  SendGrid       │
                      │  Google/GitHub  │
                      │  Adzuna/Jooble  │
                      │  NewsAPI        │
                      │  SEC EDGAR      │
                      │  Stripe         │
                      └─────────────────┘
```

---

## Technology Stack Overview

### Backend Technologies

| Technology | Purpose | Version | Why We Use It |
|------------|---------|---------|---------------|
| **Python** | Main language | 3.11+ | Easy to read, great AI/ML libraries |
| **FastAPI** | Web framework | 0.109.0 | Fast, automatic docs, async support |
| **SQLAlchemy** | Database ORM | 2.0.25 | Type-safe database operations |
| **PostgreSQL** | Primary database | 16 | Reliable, feature-rich SQL database |
| **Redis** | Cache & message queue | 7 | Fast caching, Celery broker |
| **Celery** | Background tasks | 5.3.6 | Distributed task processing |
| **AutoGen** | AI agent framework | 0.2.10 | Multi-agent orchestration |
| **Playwright** | Browser automation | 1.41.0 | Reliable web automation |
| **pdfplumber** | PDF processing | 0.10.0+ | Extract text from resumes |
| **WeasyPrint** | PDF generation | 60.0+ | Generate resume PDFs from HTML |
| **MinIO** | Object storage | Latest | S3-compatible file storage |
| **ChromaDB** | Vector database | 0.4.22 | Semantic search with embeddings |
| **Pydantic** | Data validation | 2.6.3 | Type validation & settings |
| **Together AI** | LLM provider | - | AI model API (DeepSeek, Llama 4, Qwen) |
| **SendGrid** | Email service | - | Transactional email notifications |
| **structlog** | Structured logging | 24.1.0 | JSON logging with context |
| **tenacity** | Retry logic | 8.2.3 | Resilient external calls |
| **Stripe** | Payments | 7.10.0 | Subscription billing |

### Frontend Technologies

| Technology | Purpose | Version | Why We Use It |
|------------|---------|---------|---------------|
| **Next.js** | React framework | 16.1.6 | Server components, App Router |
| **React** | UI library | 18.2 | Component-based UI |
| **TypeScript** | Type-safe JavaScript | 5.3.3 | Catch errors at compile time |
| **TanStack Query** | Server state management | 5.17.9 | Data fetching & caching |
| **Tailwind CSS** | Styling | 3.4.1 | Utility-first CSS framework |
| **Zod** | Runtime validation | 3.22.4 | Validate API responses |
| **Zustand** | State management | 4.5.0 | Simple global state |
| **Immer** | Immutable state | 11.1.3 | Safe state mutations |
| **Radix UI** | UI components | Various | Accessible component primitives |
| **Framer Motion** | Animations | 10.18.0 | Smooth UI animations |
| **dnd-kit** | Drag & Drop | 6.3.1 | Kanban board interactions |
| **react-resizable-panels** | Split panes | 4.5.6 | Resume builder layout |
| **Vitest** | Testing | 4.0.18 | Fast unit testing |
| **Playwright** | E2E Testing | 1.41.0 | Browser automation tests |

---

## Backend Deep Dive

### Backend Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application settings (pydantic-settings)
│   │
│   ├── core/                # 🏛️ BUSINESS LOGIC (Pure Python, No IO)
│   │   ├── domain/          # Domain entities
│   │   │   ├── user.py      # User, UserRole
│   │   │   ├── job.py       # Job, JobRequirements, JobSource, RemoteType
│   │   │   ├── resume.py    # Resume, ParsedResume
│   │   │   ├── application.py # Application, ApplicationStatus, ApplicationStage
│   │   │   ├── campaign.py  # Campaign, CampaignJob, RecommendationMode
│   │   │   ├── subscription.py # Subscription, Plan
│   │   │   ├── profile.py   # Profile, Preferences
│   │   │   ├── alert.py     # Alert, AlertType, AlertPreferences
│   │   │   ├── gamification.py # Achievements, Streaks, Points
│   │   │   ├── wellness.py  # WellnessInsight, BurnoutSignals
│   │   │   └── company_intel.py # CompanyIntelligence, NewsArticle, Financials
│   │   ├── ports/           # Interfaces (Protocols) for dependencies
│   │   │   ├── repositories.py # Repository protocols
│   │   │   ├── storage.py   # File storage protocol
│   │   │   ├── llm.py       # LLM client protocol
│   │   │   ├── vector_store.py # Vector store protocol
│   │   │   └── ats.py       # ATS adapter protocol
│   │   ├── services/        # Business logic services
│   │   │   ├── matcher.py   # Job-candidate match scoring
│   │   │   ├── truth_lock.py # AI content verification
│   │   │   ├── plan_gating.py # Plan limit enforcement
│   │   │   ├── ai_content_service.py # AI content generation
│   │   │   ├── ats_scoring_service.py # Resume ATS scoring
│   │   │   ├── career_tools.py # Interview, Negotiation, Career services
│   │   │   ├── company_intel.py # Company intelligence aggregation
│   │   │   ├── gamification.py # Achievement & streak tracking
│   │   │   ├── wellness.py  # Burnout detection & tips
│   │   │   ├── alerts.py    # Alert generation
│   │   │   ├── skill_gap.py # Skill gap analysis
│   │   │   ├── cover_letter.py # Cover letter generation
│   │   │   ├── question_answerer.py # Screening question answers
│   │   │   ├── recruiter_outreach.py # Outreach message generation
│   │   │   ├── analytics.py # Application analytics
│   │   │   ├── ab_testing.py # Resume A/B testing
│   │   │   ├── answer_learning.py # Few-shot learning from edits
│   │   │   ├── job_feedback.py # User feedback on jobs
│   │   │   ├── job_preference.py # Job preference learning
│   │   │   ├── job_validator.py # Negative keyword filtering
│   │   │   ├── recommendation_mode.py # Keyword vs learned mode
│   │   │   ├── timing_intel.py # Best time to apply analysis
│   │   │   └── remote_intel.py # Remote work compatibility
│   │   └── exceptions.py    # Domain-specific exceptions
│   │
│   ├── infra/               # 🔌 INFRASTRUCTURE (IO Operations)
│   │   ├── db/              # Database models & repositories
│   │   │   ├── models.py    # SQLAlchemy ORM models
│   │   │   ├── session.py   # Database session management
│   │   │   └── repositories/ # Repository implementations
│   │   │       ├── user.py, job.py, resume.py, application.py
│   │   │       ├── campaign.py, subscription.py, profile.py
│   │   │       ├── alert.py, gamification.py, audit.py
│   │   │       └── resume_draft.py
│   │   ├── auth/            # Authentication
│   │   │   ├── jwt.py       # JWT token management
│   │   │   ├── password.py  # Password hashing
│   │   │   ├── oauth.py     # Google/GitHub OAuth clients
│   │   │   └── service.py   # Auth service (login, signup, refresh)
│   │   ├── storage/         # S3/MinIO file storage
│   │   ├── llm/             # LLM client implementations
│   │   │   └── together_client.py # Together AI client
│   │   ├── vector/          # Vector store implementations
│   │   │   └── chroma_store.py # ChromaDB client
│   │   ├── ats_adapters/    # ATS automation adapters
│   │   │   ├── base.py, greenhouse.py, lever.py
│   │   ├── scrapers/        # Job board scrapers
│   │   │   ├── base.py      # Base scraper class
│   │   │   ├── adzuna.py    # Adzuna API adapter
│   │   │   ├── jooble.py    # Jooble API adapter
│   │   │   ├── themuse.py   # TheMuse API adapter
│   │   │   ├── stackoverflow.py # Stack Overflow scraper
│   │   │   └── wellfound.py # Wellfound scraper
│   │   ├── company_intel/   # Company intelligence clients
│   │   │   ├── clearbit_client.py # Company data from Clearbit
│   │   │   ├── wikipedia_client.py # Company info from Wikipedia
│   │   │   ├── news_client.py # News from NewsAPI
│   │   │   └── sec_edgar_client.py # SEC filings for financials
│   │   ├── notifications/   # Email notifications
│   │   │   └── email.py     # SendGrid email service
│   │   └── services/        # Infrastructure services
│   │       ├── resume_service.py # Resume upload & parsing
│   │       ├── application_service.py # Application management
│   │       ├── billing_service.py # Stripe billing
│   │       └── pdf_generator.py # WeasyPrint PDF generation
│   │
│   ├── api/                 # 🌐 REST API LAYER
│   │   ├── v1/              # API version 1 endpoints
│   │   │   ├── router.py    # Main router
│   │   │   ├── auth.py      # Authentication + OAuth
│   │   │   ├── profile.py   # User profile
│   │   │   ├── resumes.py   # Resume upload/management
│   │   │   ├── resume_builder.py # Resume builder API
│   │   │   ├── jobs.py      # Job listings
│   │   │   ├── applications.py # Applications + Kanban stages
│   │   │   ├── campaigns.py # Campaign (copilot) management
│   │   │   ├── agents.py    # AI chat
│   │   │   ├── tools.py     # Career tools (Interview/Nego/Career)
│   │   │   ├── alerts.py    # Alert notifications
│   │   │   ├── gamification.py # Achievements & streaks
│   │   │   ├── analytics.py # Application analytics
│   │   │   ├── wellness.py  # Wellness insights
│   │   │   ├── company_intel.py # Company intelligence
│   │   │   └── billing.py   # Subscriptions
│   │   ├── deps.py          # Dependency injection
│   │   └── middleware/      # API middleware
│   │       ├── rate_limit.py # Redis-based rate limiting
│   │       └── metrics.py   # Prometheus metrics
│   │
│   ├── agents/              # 🤖 AI AGENT ORCHESTRATION
│   │   ├── config.py        # LLM configurations per agent role
│   │   ├── prompts.py       # System prompts for each agent
│   │   ├── tools.py         # Functions agents can call
│   │   └── workflows.py     # AutoGen GroupChat orchestration
│   │
│   ├── workers/             # ⚙️ BACKGROUND TASKS (Celery)
│   │   ├── celery_app.py    # Celery configuration
│   │   ├── job_ingestion.py # Scheduled job scraping
│   │   ├── application_submitter.py # Form filling automation
│   │   ├── status_monitor.py # Application status tracking
│   │   └── alert_generator.py # Alert generation
│   │
│   └── schemas/             # 📋 API Request/Response Models
│       ├── auth.py, job.py, application.py, profile.py
│       ├── resume_builder.py, campaign.py, agent.py
│       ├── career_tools.py, company_intel.py
│       ├── gamification.py, wellness.py, alert.py
│       ├── analytics.py, billing.py
│
├── migrations/              # Database migrations (Alembic)
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container image definition
```

### Core Layer (Business Logic)

The **Core Layer** contains pure business logic with **NO external dependencies** (no database calls, no HTTP requests). This makes it:
- Easy to test (no mocking needed)
- Easy to understand (just Python logic)
- Reusable across different implementations

#### Domain Models (`core/domain/`)

Domain models are Python dataclasses representing business entities:

```python
# User - Platform user
@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: UserRole        # Enum: USER or ADMIN
    email_verified: bool
    created_at: datetime

# Job - A job listing with remote work analysis
@dataclass  
class Job:
    id: str
    external_id: str       # ID from source system
    title: str
    company: str
    location: str | None
    description: str
    url: str
    source: JobSource      # Enum: ADZUNA, JOOBLE, THEMUSE, MANUAL
    salary_min: int | None
    salary_max: int | None
    remote: bool
    remote_type: RemoteType  # REMOTE, HYBRID, ONSITE
    remote_score: int        # 0-100 remote compatibility
    timezone_requirements: list[str]
    requirements: JobRequirements  # skills, experience, education
    embedding: list[float] | None  # For semantic search

# Application - A job application with Kanban stages
@dataclass
class Application:
    id: str
    user_id: str
    job_id: str
    resume_id: str
    status: ApplicationStatus  # PENDING_REVIEW, APPROVED, SUBMITTING, etc.
    stage: ApplicationStage    # SAVED, APPLIED, INTERVIEWING, OFFER, REJECTED
    match_score: int           # 0-100 compatibility score
    match_explanation: MatchExplanation | None
    cover_letter: str | None
    generated_answers: dict[str, str]  # Question -> Answer
    notes: list[ApplicationNote]       # User notes on application
    qc_approved: bool          # Quality control approval
    stage_updated_at: datetime | None  # For Kanban tracking

# Campaign - Job application campaign (copilot)
@dataclass
class Campaign:
    id: str
    user_id: str
    name: str
    resume_id: str             # Resume for this campaign
    target_roles: list[str]
    target_locations: list[str]
    target_countries: list[str]
    target_companies: list[str]
    remote_only: bool
    salary_min: int | None
    salary_max: int | None
    negative_keywords: list[str]  # Keywords to avoid
    auto_apply: bool           # Auto-apply vs save for review
    daily_limit: int           # Max applications per day
    min_match_score: int       # Minimum match score to apply
    status: CampaignStatus     # DRAFT, ACTIVE, PAUSED, COMPLETED, ARCHIVED
    recommendation_mode: RecommendationMode  # KEYWORD or LEARNED
    jobs_applied: int
    interviews: int
    offers: int

# Alert - User notification
@dataclass
class Alert:
    id: str
    user_id: str
    alert_type: AlertType  # DREAM_JOB_MATCH, APPLICATION_STATUS_CHANGE, etc.
    title: str
    message: str
    data: dict
    read: bool
    created_at: datetime

# Gamification - Achievement system
@dataclass
class UserStreak:
    user_id: str
    current_streak: int
    longest_streak: int
    last_activity_date: date | None
    total_points: int

@dataclass
class UserAchievement:
    id: str
    user_id: str
    achievement_id: AchievementId  # FIRST_APPLY, STREAK_7, PERFECT_MATCH, etc.
    earned_at: datetime

# Wellness - Burnout prevention
@dataclass
class WellnessStatus:
    user_id: str
    activity_level: str        # "low", "moderate", "high", "very_high"
    rejection_streak: int
    days_since_last_positive: int | None
    burnout_risk: str          # "low", "medium", "high"
    recommended_action: str

# Company Intelligence
@dataclass
class CompanyIntelligence:
    company_name: str
    domain: str | None
    logo_url: str | None
    description: str | None
    industry: str | None
    size_range: str | None     # "1-10", "11-50", "51-200", etc.
    founded_year: int | None
    headquarters: str | None
    recent_news: list[NewsArticle]
    financials: CompanyFinancials | None  # From SEC EDGAR
    hiring_signals: HiringSignals
    wikipedia_summary: str | None
    confidence_score: int      # 0-100 based on data quality
```

#### Ports (Interfaces) (`core/ports/`)

Ports define **what** the core needs, not **how** it's implemented. Uses Python `Protocol` for interfaces:

```python
# Repository interface - defines data access methods
class UserRepository(Protocol):
    async def get_by_id(self, user_id: str) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def create(self, user: User) -> User: ...
    async def update(self, user: User) -> User: ...

# LLM interface - defines AI model operations
class LLMClient(Protocol):
    async def complete(
        self,
        *,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse: ...
    
    async def get_embedding(
        self,
        *,
        text: str,
        model: str,
    ) -> list[float]: ...

# Storage interface - defines file operations
class FileStorage(Protocol):
    async def upload(self, *, key: str, data: bytes, content_type: str) -> str: ...
    async def download(self, *, key: str) -> bytes: ...
    async def delete(self, *, key: str) -> None: ...

# Vector store interface
class VectorStore(Protocol):
    async def add_embedding(
        self, *, collection: str, doc_id: str, embedding: list[float], metadata: dict
    ) -> None: ...
    async def search_by_embedding(
        self, *, collection: str, embedding: list[float], top_k: int
    ) -> list[SearchResult]: ...
```

#### Core Services (`core/services/`)

Business logic services that operate on domain models:

**MatchService** - Calculates job-candidate compatibility:

```python
class MatchService:
    """Calculate match scores between resume and job."""
    
    def calculate_score(
        self, 
        *, 
        resume: ParsedResume, 
        job: Job,
        preferences: Preferences | None = None,
    ) -> tuple[int, MatchExplanation]:
        """
        Scoring weights:
        - Skills Match:     40%
        - Experience:       25%
        - Location:         15%
        - Salary:           10%
        - Culture Fit:      10%
        
        Returns: (score 0-100, detailed explanation)
        """
```

**TruthLockVerifier** - Prevents AI hallucinations:

```python
class TruthLockVerifier:
    """Verify AI-generated content against source documents."""
    
    async def verify_content(
        self,
        *,
        generated_content: str,
        source_documents: list[str],
        user_id: str,
    ) -> VerificationResult:
        """
        Checks for:
        - Experience years claims (must match resume)
        - Company names (must be in work history)
        - Education claims (degrees must exist)
        - Skill claims (skills must be listed)
        
        Returns violations if content fabricates information.
        """
```

**Career Tools Services** - Interview, Negotiation, Career Advisor:

```python
class InterviewRoleplayService:
    """Service for conducting mock interviews."""
    
    async def start_session(
        self,
        *,
        user_id: str,
        target_role: str,
        company_name: str | None = None,
        interview_type: InterviewType = InterviewType.MIXED,
        experience_level: ExperienceLevel = ExperienceLevel.MID,
        focus_areas: list[str] | None = None,
    ) -> InterviewStartResponse:
        """Start interview session with tailored questions."""
    
    async def submit_answer(
        self,
        *,
        session_id: str,
        question_id: str,
        answer: str,
    ) -> tuple[AnswerFeedback, InterviewQuestion | None, int, float]:
        """Submit answer, get feedback, and next question."""

class OfferNegotiationService:
    """Service for offer analysis and negotiation advice."""
    
    async def analyze_offer(
        self,
        *,
        offer: OfferDetails,
        target_role: str,
        location: str,
        years_experience: int,
    ) -> NegotiationAnalyzeResponse:
        """Analyze offer against market data."""
    
    async def get_strategy(
        self,
        *,
        offer: OfferDetails,
        target_salary: float | None = None,
        risk_tolerance: Literal["low", "medium", "high"] = "medium",
    ) -> NegotiationStrategyResponse:
        """Get negotiation scripts and strategy."""

class CareerAdvisorService:
    """Service for career assessment and path recommendations."""
    
    async def assess_career(
        self,
        *,
        current_role: str,
        years_experience: int,
        skills: list[str],
    ) -> CareerAssessResponse:
        """Assess current position, skills, and market positioning."""
    
    async def get_career_paths(
        self,
        *,
        current_role: str,
        skills: list[str],
        timeline_months: int = 12,
    ) -> CareerPathsResponse:
        """Get recommended career paths with learning roadmap."""
```

**ATSScoringService** - Resume ATS compatibility:

```python
class ATSScoringService:
    """Score resume for ATS compatibility."""
    
    def calculate_ats_score(
        self,
        *,
        resume_content: dict,
        target_job: Job | None = None,
    ) -> ATSScoreResult:
        """
        Score based on:
        - Keyword optimization
        - Formatting compatibility
        - Section completeness
        - Bullet point structure
        """
```

**GamificationService** - Achievements and streaks:

```python
class GamificationService:
    """Track achievements, streaks, and points."""
    
    async def record_activity(
        self,
        *,
        user_id: str,
        activity_type: str,
    ) -> list[UserAchievement]:
        """Record activity and check for new achievements."""
    
    async def get_progress(
        self,
        *,
        user_id: str,
    ) -> GamificationProgress:
        """Get user's streak, points, and achievements."""
```

**WellnessService** - Burnout prevention:

```python
class WellnessService:
    """Monitor wellness and provide support."""
    
    async def check_wellness(
        self,
        *,
        user_id: str,
    ) -> WellnessStatus:
        """Analyze activity for burnout signals."""
    
    async def get_insight(
        self,
        *,
        user_id: str,
    ) -> WellnessInsight:
        """Get personalized wellness tip or encouragement."""
```

#### Exception Hierarchy (`core/exceptions.py`)

Domain-specific exceptions for proper error handling:

```python
# Base exception
class DomainError(Exception):
    message: str
    code: str  # Machine-readable code

# Authentication
class InvalidCredentialsError(AuthenticationError)
class TokenExpiredError(AuthenticationError)
class TokenInvalidError(AuthenticationError)
class SessionRevokedError(AuthenticationError)

# Authorization  
class PlanLimitExceededError(AuthorizationError)  # Daily limit reached
class InsufficientPermissionsError(AuthorizationError)

# Resources
class ResourceNotFoundError(DomainError)
class ResourceAlreadyExistsError(DomainError)

# Validation
class ValidationError(DomainError)

# Application Processing
class TruthLockViolationError(ApplicationError)  # AI generated false info
class QCRejectionError(ApplicationError)          # Failed quality check
class LowMatchScoreError(ApplicationError)        # Below threshold

# Automation
class CaptchaDetectedError(AutomationError)       # Manual intervention needed
class MFARequiredError(AutomationError)           # 2FA blocking automation
class FormFieldNotFoundError(AutomationError)     # Form structure changed

# External Services
class ExternalServiceError(DomainError)           # API failures
```

---

### Infrastructure Layer

The **Infrastructure Layer** handles all external interactions (IO):

#### Database (`infra/db/`)

**ORM Models** (`models.py`) - SQLAlchemy models mapping to database tables:

```python
class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    
    # Relationships
    profile: Mapped["ProfileModel"] = relationship(back_populates="user")
    resumes: Mapped[List["ResumeModel"]] = relationship(back_populates="user")
    resume_drafts: Mapped[List["ResumeDraftModel"]] = relationship(back_populates="user")
    applications: Mapped[List["ApplicationModel"]] = relationship(back_populates="user")
    campaigns: Mapped[List["CampaignModel"]] = relationship(back_populates="user")
    subscription: Mapped["SubscriptionModel"] = relationship(back_populates="user")
    alerts: Mapped[List["AlertModel"]] = relationship(back_populates="user")
    user_streak: Mapped["UserStreakModel"] = relationship(back_populates="user")
    achievements: Mapped[List["UserAchievementModel"]] = relationship(back_populates="user")

class ApplicationModel(Base):
    __tablename__ = "applications"
    
    # ... standard fields ...
    stage: Mapped[ApplicationStage]  # For Kanban UI
    stage_updated_at: Mapped[datetime | None]
    
    # Timing intelligence columns
    applied_day_of_week: Mapped[int | None]
    applied_hour: Mapped[int | None]
    days_after_posting: Mapped[int | None]
    
    # Notes relationship for Kanban
    notes: Mapped[List["ApplicationNoteModel"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )

class ResumeDraftModel(Base):
    """Resume draft for builder with autosave."""
    __tablename__ = "resume_drafts"
    
    content: Mapped[dict]  # JSON resume data
    template_id: Mapped[str]  # Selected template
    ats_score: Mapped[int | None]  # Calculated ATS score
    is_published: Mapped[bool]

class CampaignModel(Base):
    """Campaign (copilot) for targeted job search."""
    __tablename__ = "campaigns"
    
    # Search criteria
    target_roles: Mapped[list]
    target_locations: Mapped[list]
    negative_keywords: Mapped[list]
    
    # Behavior settings
    auto_apply: Mapped[bool]
    daily_limit: Mapped[int]
    min_match_score: Mapped[int]
    
    # Recommendation mode
    recommendation_mode: Mapped[RecommendationMode]  # KEYWORD or LEARNED
    
    # Relationships
    campaign_jobs: Mapped[List["CampaignJobModel"]] = relationship()

class AnswerEditModel(Base):
    """User edits to AI-generated answers for few-shot learning."""
    __tablename__ = "answer_edits"
    
    question_normalized: Mapped[str]  # For similarity matching
    question_original: Mapped[str]
    original_answer: Mapped[str]
    edited_answer: Mapped[str]
```

#### LLM Client (`infra/llm/together_client.py`)

Together AI client implementation:

```python
class TogetherLLMClient:
    """Together AI LLM client implementing LLMClient protocol."""
    
    async def complete(
        self,
        *,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Complete a chat with Together AI."""
    
    async def get_embedding(
        self,
        *,
        text: str,
        model: str = "BAAI/bge-large-en-v1.5",
    ) -> list[float]:
        """Generate embedding vector (1024 dimensions)."""
```

#### Job Scrapers (`infra/scrapers/`)

Multiple job source integrations:

```python
class BaseJobScraper(ABC):
    """Base class for job scrapers."""
    
    @abstractmethod
    async def scrape_jobs(
        self,
        *,
        keywords: list[str],
        location: str | None = None,
        limit: int = 20,
    ) -> list[Job]: ...

# Implementations:
class AdzunaAdapter(BaseJobScraper):
    """Adzuna job board API integration."""

class JoobleAdapter(BaseJobScraper):
    """Jooble job aggregator API integration."""

class TheMuseAdapter(BaseJobScraper):
    """TheMuse job board API integration."""

class StackOverflowAdapter(BaseJobScraper):
    """Stack Overflow jobs scraper."""

class WellFoundAdapter(BaseJobScraper):
    """Wellfound (AngelList) scraper."""
```

#### Company Intelligence (`infra/company_intel/`)

Multiple data source clients:

```python
class WikipediaClient:
    """Fetch company info from Wikipedia."""
    
    async def get_company_summary(self, company_name: str) -> WikipediaSummary | None:
        """Get company description and URL."""

class SECEdgarClient:
    """Fetch financial data from SEC EDGAR."""
    
    async def get_company_financials(self, company_name: str) -> CompanyFinancials | None:
        """Get revenue, employees, etc. from 10-K filings."""

class NewsClient:
    """Fetch recent news from NewsAPI."""
    
    async def get_company_news(self, company_name: str, limit: int = 5) -> list[NewsArticle]:
        """Get recent news articles with sentiment."""

class ClearbitClient:
    """Fetch company data from Clearbit."""
    
    async def get_company_data(self, domain: str) -> ClearbitCompany | None:
        """Get logo, industry, size, etc."""
```

#### PDF Generator (`infra/services/pdf_generator.py`)

Resume PDF generation using WeasyPrint:

```python
class PDFGenerator:
    """Generate PDF resumes from templates."""
    
    async def generate_resume_pdf(
        self,
        *,
        content: dict,
        template_id: str,
    ) -> bytes:
        """
        1. Load Jinja2 template
        2. Render HTML with content
        3. Convert to PDF with WeasyPrint
        """
```

---

### API Layer

REST API endpoints built with FastAPI:

#### Router Structure (`api/v1/router.py`)

```python
api_router = APIRouter()

# Core endpoints
api_router.include_router(auth.router, prefix="/auth")           # Authentication + OAuth
api_router.include_router(profile.router, prefix="/profile")     # User profile
api_router.include_router(resumes.router, prefix="/resumes")     # Resume management
api_router.include_router(resume_builder.router, prefix="/resume-builder")  # Builder
api_router.include_router(jobs.router, prefix="/jobs")           # Job listings
api_router.include_router(applications.router, prefix="/applications")  # Applications
api_router.include_router(campaigns.router, prefix="/campaigns") # Campaigns
api_router.include_router(agents.router, prefix="/agents")       # AI chat
api_router.include_router(billing.router, prefix="/billing")     # Subscriptions

# Career tools
api_router.include_router(tools.router, prefix="/tools")         # Interview/Nego/Career

# Engagement features
api_router.include_router(alerts.router)                         # Notifications
api_router.include_router(gamification.router)                   # Achievements
api_router.include_router(analytics.router)                      # Analytics
api_router.include_router(wellness.router)                       # Wellness
api_router.include_router(company_intel.router)                  # Company research
```

#### API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/signup` | POST | Create new account |
| `/auth/login` | POST | Login, get tokens |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/logout` | POST | Invalidate session |
| `/auth/google-login` | GET | Initiate Google OAuth |
| `/auth/google-callback` | GET | Handle Google OAuth callback |
| `/auth/github-login` | GET | Initiate GitHub OAuth |
| `/auth/github-callback` | GET | Handle GitHub OAuth callback |
| `/profile` | GET/PUT | Get/update user profile |
| `/resumes` | GET/POST | List resumes / Upload new |
| `/resumes/{id}` | GET/DELETE | Get/delete resume |
| `/resumes/{id}/set-primary` | POST | Set as primary resume |
| `/resume-builder/drafts` | GET/POST | List/create drafts |
| `/resume-builder/drafts/{id}` | GET/PUT/DELETE | Manage draft |
| `/resume-builder/drafts/{id}/export` | POST | Export to PDF |
| `/resume-builder/ai/summary` | POST | AI summary generation |
| `/resume-builder/ai/skills` | POST | AI skills suggestions |
| `/resume-builder/ai/ats-score` | POST | Calculate ATS score |
| `/jobs` | GET | List matching jobs |
| `/jobs/{id}` | GET | Get job details |
| `/jobs/refresh` | POST | Trigger job ingestion |
| `/applications` | GET/POST | List/create applications |
| `/applications/grouped` | GET | Get applications by Kanban stage |
| `/applications/{id}/stage` | PATCH | Update Kanban stage |
| `/applications/{id}/notes` | POST | Add note to application |
| `/applications/{id}/approve` | POST | Approve for submission |
| `/campaigns` | GET/POST | List/create campaigns |
| `/campaigns/{id}` | GET/PUT/DELETE | Manage campaign |
| `/campaigns/{id}/jobs` | GET | Get campaign's matched jobs |
| `/agents/chat` | POST | Send message to AI |
| `/agents/chat/stream` | POST | Stream AI response |
| `/tools/interview/start` | POST | Start mock interview |
| `/tools/interview/respond` | POST | Submit answer, get feedback |
| `/tools/interview/end` | POST | End session, get summary |
| `/tools/negotiation/analyze` | POST | Analyze job offer |
| `/tools/negotiation/strategy` | POST | Get negotiation scripts |
| `/tools/career/assess` | POST | Assess career position |
| `/tools/career/paths` | POST | Get career path recommendations |
| `/alerts` | GET | List user alerts |
| `/alerts/{id}/read` | POST | Mark alert as read |
| `/alerts/preferences` | GET/PUT | Manage alert preferences |
| `/gamification/progress` | GET | Get achievements & streak |
| `/gamification/leaderboard` | GET | Get leaderboard |
| `/analytics/dashboard` | GET | Get analytics data |
| `/wellness/status` | GET | Get wellness status |
| `/wellness/insight` | GET | Get wellness tip |
| `/company/{name}/intelligence` | GET | Get company research |
| `/billing/usage` | GET | Get usage stats |
| `/billing/checkout` | POST | Start Stripe checkout |

---

### Agents Module

AI-powered multi-agent system using AutoGen with GroupChat:

#### Agent Roles (`agents/prompts.py`)

Each agent has a specialized role:

| Agent | Role | LLM Model |
|-------|------|-----------|
| **Orchestrator** | Coordinates all agents, delegates tasks | DeepSeek-R1 |
| **ResumeAgent** | Parses and optimizes resumes | Qwen3-235B |
| **JobScraperAgent** | Finds and filters jobs | Llama-4-Scout |
| **MatchAgent** | Scores job-candidate fit | Llama-4-Maverick |
| **ApplyAgent** | Generates cover letters, answers | Llama-3.3-70B |
| **QualityControlAgent** | Reviews all output | DeepSeek-V3 |
| **CriticAgent** | Provides improvement feedback | Qwen-QwQ |

#### LLM Configurations (`agents/config.py`)

```python
class Models:
    """Together AI model identifiers."""
    
    # Orchestration and reasoning
    DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1-0528"
    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3.1"
    
    # Fast extraction and scraping
    LLAMA4_SCOUT = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
    LLAMA4_MAVERICK = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    
    # Content generation
    LLAMA3_70B = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    
    # Document understanding
    QWEN3_235B = "Qwen/Qwen3-235B-A22B-fp8-tput"
    
    # Reasoning and critique
    QWEN_QWQ = "Qwen/QwQ-32B"
    
    # Code generation
    QWEN3_CODER = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
    
    # Embeddings (1024 dimensions)
    BGE_LARGE = "BAAI/bge-large-en-v1.5"
```

#### Workflow Orchestration (`agents/workflows.py`)

Uses AutoGen's GroupChat for multi-agent collaboration:

```python
class JobApplicationWorkflow:
    """Orchestrates multi-agent job application process using AutoGen GroupChat."""
    
    def __init__(self, *, user_id: str, db_session: AsyncSession, settings: Settings):
        self._agents = self._setup_agents()
        self._group_chat = GroupChat(
            agents=list(self._agents.values()),
            messages=[],
            max_round=20,
            speaker_selection_method="auto",
        )
        self._manager = GroupChatManager(
            groupchat=self._group_chat,
            llm_config=LLM_CONFIG_ORCHESTRATOR,
        )
    
    async def process_message(self, message: str, session_id: str | None = None) -> AgentResponse:
        """Process user message through AutoGen GroupChat."""
    
    async def stream_process(self, message: str) -> AsyncIterator[StreamResponse]:
        """Stream agent responses for real-time UI updates."""
    
    async def optimize_resume(self, *, resume_id: str, job_id: str) -> OptimizationResult:
        """Optimize resume for a specific job using agent collaboration."""
```

---

### Workers Module

Background task processing with Celery:

#### Celery Configuration (`workers/celery_app.py`)

```python
celery_app = Celery(
    "ApplyBots",
    broker=settings.redis_url,      # Redis as message broker
    backend=settings.redis_url,     # Redis for results
    include=[
        "app.workers.job_ingestion",
        "app.workers.application_submitter",
        "app.workers.status_monitor",
        "app.workers.alert_generator",
    ],
)

# Windows compatibility: use solo pool
worker_pool = "solo" if sys.platform == "win32" else "prefork"

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "ingest-jobs-4-hourly": {
        "task": "app.workers.job_ingestion.ingest_jobs_scheduled",
        "schedule": 14400.0,  # Every 4 hours
    },
    "reset-daily-usage": {
        "task": "app.workers.job_ingestion.reset_daily_usage",
        "schedule": 86400.0,  # Every 24 hours
    },
}
```

#### Task Types

**Job Ingestion** - Fetches new jobs from multiple sources:

```python
@celery_app.task
def ingest_jobs_scheduled():
    """
    1. Query multiple job APIs (Adzuna, Jooble, TheMuse)
    2. Deduplicate against existing jobs
    3. Extract requirements with AI
    4. Generate embeddings (BGE-Large)
    5. Store embeddings in ChromaDB
    6. Store job data in PostgreSQL
    """
```

**Application Submitter** - Automated form filling:

```python
@celery_app.task
def submit_application(application_id: str):
    """
    1. Load application data
    2. Detect ATS type (Greenhouse, Lever)
    3. Select appropriate ATS adapter
    4. Launch browser with Playwright
    5. Fill form fields using adapter
    6. Capture screenshots at each step
    7. Handle errors (CAPTCHA → manual)
    8. Store audit trail
    9. Update status
    """
```

**Alert Generator** - Generate notifications:

```python
@celery_app.task
def generate_alerts():
    """
    1. Check for dream job matches (score >= threshold)
    2. Check for application status changes
    3. Check for interview reminders
    4. Check for achievement unlocks
    5. Generate and store alerts
    """
```

---

## Frontend Deep Dive

### Frontend Project Structure

```
frontend/src/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group (no layout)
│   │   ├── layout.tsx            # Auth pages layout
│   │   ├── login/page.tsx        # Login page (with OAuth)
│   │   └── signup/page.tsx       # Signup page (with OAuth)
│   │
│   ├── (dashboard)/              # Dashboard route group (with layout)
│   │   ├── layout.tsx            # Sidebar layout
│   │   ├── error.tsx             # Error boundary
│   │   └── dashboard/
│   │       ├── page.tsx          # Main dashboard
│   │       ├── jobs/page.tsx     # Job listings
│   │       ├── applications/page.tsx  # Kanban board
│   │       ├── resumes/
│   │       │   ├── page.tsx      # Resume list
│   │       │   └── builder/page.tsx  # Resume builder
│   │       ├── chat/page.tsx     # AI assistant
│   │       ├── tools/
│   │       │   ├── page.tsx      # Career tools hub
│   │       │   ├── interview/page.tsx  # Mock interview
│   │       │   ├── negotiation/page.tsx  # Offer analysis
│   │       │   └── career/page.tsx  # Career advisor
│   │       ├── profile/page.tsx
│   │       └── billing/page.tsx
│   │
│   ├── api/v1/[...path]/route.ts # API proxy to backend
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Landing page
│
├── components/
│   ├── applications/             # Application tracking components
│   │   ├── KanbanBoard.tsx       # Drag-and-drop Kanban
│   │   ├── StageColumn.tsx       # Column in Kanban
│   │   ├── ApplicationCard.tsx   # Card in Kanban
│   │   ├── DetailDrawer.tsx      # Application detail panel
│   │   ├── drawer/               # Drawer sub-components
│   │   │   ├── DrawerNotes.tsx   # Notes section
│   │   │   ├── DrawerTimeline.tsx # Activity timeline
│   │   │   └── DrawerFooter.tsx  # Action buttons
│   │   ├── SearchFilter.tsx      # Search and filters
│   │   ├── StatsBar.tsx          # Pipeline statistics
│   │   └── ProTips.tsx           # Contextual tips
│   │
│   └── resume-builder/           # Resume builder components
│       ├── EditorPanel.tsx       # Form-based editor
│       ├── PreviewPanel.tsx      # Live preview
│       ├── TemplateSelector.tsx  # Template picker
│       ├── AIAssistantDrawer.tsx # AI suggestions drawer
│       ├── ai-drawer/            # AI drawer sub-components
│       │   ├── SummaryMode.tsx   # AI summary generation
│       │   ├── SkillsMode.tsx    # AI skills suggestions
│       │   └── ATSMode.tsx       # ATS scoring
│       ├── sections/             # Editor sections
│       │   ├── ContactSection.tsx
│       │   ├── SummarySection.tsx
│       │   ├── ExperienceSection.tsx
│       │   ├── EducationSection.tsx
│       │   ├── SkillsSection.tsx
│       │   └── ProjectsSection.tsx
│       └── templates/            # PDF templates
│           ├── ProfessionalModern.tsx
│           ├── ClassicTraditional.tsx
│           ├── TechMinimalist.tsx
│           ├── TwoColumn.tsx
│           └── ATSOptimized.tsx
│
├── hooks/                        # Custom React hooks
│   ├── useJobs.ts               # Job data fetching
│   └── useApplications.ts       # Application data with Kanban
│
├── i18n/                        # Internationalization
│   ├── config.ts                # Language configuration
│   ├── core/                    # Translation utilities
│   │   ├── createTranslator.ts
│   │   └── interpolate.ts
│   ├── locales/                 # Language files
│   │   ├── en.ts
│   │   └── de.ts
│   └── next/                    # Next.js integration
│
├── lib/                         # Utilities
│   ├── api.ts                   # Typed API client with Zod schemas
│   └── utils.ts                 # Helper functions
│
├── providers/                   # React Context providers
│   ├── AuthProvider.tsx         # Authentication state
│   └── Providers.tsx            # Combined providers wrapper
│
└── stores/                      # Global state
    └── resume-builder-store.ts  # Zustand store for builder
```

### Key Frontend Concepts

#### API Client (`lib/api.ts`)

Type-safe API client with comprehensive Zod schemas:

```typescript
// Application Kanban schemas
export const ApplicationStageSchema = z.enum([
  "saved", "applied", "interviewing", "offer", "rejected"
]);

export const ApplicationSchema = z.object({
  id: z.string(),
  job_id: z.string(),
  job_title: z.string(),
  company: z.string(),
  status: z.string(),
  stage: ApplicationStageSchema,  // For Kanban
  match_score: z.number(),
  notes: z.array(ApplicationNoteSchema),
  stage_updated_at: z.string().nullable(),
});

// Career tools schemas
export const InterviewStartResponseSchema = z.object({
  session_id: z.string(),
  target_role: z.string(),
  first_question: InterviewQuestionSchema,
  total_questions: z.number(),
  estimated_duration_minutes: z.number(),
});

export const NegotiationAnalyzeResponseSchema = z.object({
  total_compensation: z.number(),
  market_comparison: MarketComparisonSchema,
  strengths: z.array(z.string()),
  concerns: z.array(z.string()),
  negotiation_room: z.enum(["low", "medium", "high"]),
});

// API methods
class APIClient {
  // Applications with Kanban
  async getGroupedApplications(): Promise<GroupedApplicationsResponse>
  async updateApplicationStage(id: string, stage: ApplicationStage): Promise<Application>
  async addApplicationNote(applicationId: string, content: string): Promise<ApplicationNote>
  
  // Career tools
  async startInterview(params: InterviewStartRequest): Promise<InterviewStartResponse>
  async respondToInterview(params: InterviewRespondRequest): Promise<InterviewRespondResponse>
  async analyzeOffer(params: OfferAnalyzeRequest): Promise<NegotiationAnalyzeResponse>
  async getCareerPaths(params: CareerPathsRequest): Promise<CareerPathsResponse>
}
```

#### Resume Builder Store (`stores/resume-builder-store.ts`)

Zustand store with Immer for immutable updates:

```typescript
interface ResumeBuilderState {
  content: ResumeContent;
  templateId: string;
  isDirty: boolean;
  atsScore: number | null;
  
  // Actions
  setContactInfo: (info: ContactInfo) => void;
  addExperience: (exp: Experience) => void;
  updateExperience: (id: string, exp: Partial<Experience>) => void;
  setTemplate: (templateId: string) => void;
  setATSScore: (score: number) => void;
}

const useResumeBuilderStore = create<ResumeBuilderState>()(
  immer((set) => ({
    // State
    content: defaultContent,
    templateId: 'professional-modern',
    isDirty: false,
    atsScore: null,
    
    // Actions with Immer
    setContactInfo: (info) => set((state) => {
      state.content.contact = info;
      state.isDirty = true;
    }),
    // ...
  }))
);
```

---

## Infrastructure Services

### PostgreSQL (Database)

Primary relational database storing:

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `profiles` | User preferences, contact info, negative keywords |
| `resumes` | Uploaded resumes with parsed data & embeddings |
| `resume_drafts` | Resume builder drafts with autosave |
| `jobs` | Job listings with embeddings & remote analysis |
| `applications` | Application records with Kanban stages & notes |
| `application_notes` | Notes on applications |
| `campaigns` | Job search campaigns (copilots) |
| `campaign_jobs` | Campaign-job associations with scores |
| `subscriptions` | Plan & billing info |
| `refresh_sessions` | JWT refresh tokens |
| `agent_sessions` | AI chat history |
| `audit_logs` | Automation action logs |
| `alerts` | User notifications |
| `alert_preferences` | Alert settings per user |
| `user_streaks` | Activity streak tracking |
| `user_achievements` | Earned achievements |
| `answer_edits` | User edits for few-shot learning |

### Redis (Cache & Queue)

- **Session cache** - Fast user lookups
- **Rate limiting** - Sliding window counter
- **Celery broker** - Task message queue
- **Celery backend** - Task results storage

### MinIO (Object Storage)

S3-compatible storage for:
- **Resumes** - Original PDF/DOCX files
- **Screenshots** - Automation audit trail
- **Generated documents** - Cover letters, PDFs

### ChromaDB (Vector Database)

Stores embeddings for semantic search:

| Collection | Purpose |
|------------|---------|
| `resumes` | Resume embeddings for matching |
| `jobs` | Job description embeddings |

**Embedding Model:**
- Model: `BAAI/bge-large-en-v1.5`
- Dimensions: 1024
- Provider: Together AI

---

## Data Flow Diagrams

### Job Application Flow with Kanban

```
User           Frontend        Backend         Celery Worker      ATS Site
 │                │               │                  │               │
 │ Click "Apply"  │               │                  │               │
 │───────────────>│               │                  │               │
 │                │ POST /applications               │               │
 │                │──────────────>│                  │               │
 │                │               │ Calculate match  │               │
 │                │               │ Generate cover   │               │
 │                │               │ Truth-lock verify│               │
 │                │ Application   │ Stage: SAVED     │               │
 │                │<─────created──│                  │               │
 │ Review & Edit  │               │                  │               │
 │───────────────>│               │                  │               │
 │                │ PATCH /stage  │                  │               │
 │                │──────────────>│                  │               │
 │                │               │ Stage: APPLIED   │               │
 │                │ POST /approve │                  │               │
 │                │──────────────>│                  │               │
 │                │               │ Queue submission │               │
 │                │               │─────────────────>│               │
 │                │               │                  │ Launch browser│
 │                │               │                  │──────────────>│
 │                │               │                  │ Fill form     │
 │                │               │                  │ Screenshot    │
 │                │               │                  │<──────────────│
 │                │               │ Update stage     │               │
 │ (Kanban moves) │ Stage: INTERVIEW               │               │
 │<───────────────│<──────────────│                  │               │
```

### Interview Roleplay Flow

```
User           Frontend        Backend (Tools API)      LLM (Together AI)
 │                │                    │                       │
 │ Start Interview│                    │                       │
 │───────────────>│                    │                       │
 │                │ POST /tools/interview/start               │
 │                │───────────────────>│                       │
 │                │                    │ Generate questions    │
 │                │                    │──────────────────────>│
 │                │                    │<──────────────────────│
 │                │ session_id + first_question               │
 │                │<───────────────────│                       │
 │ Answer Q1      │                    │                       │
 │───────────────>│                    │                       │
 │                │ POST /tools/interview/respond             │
 │                │───────────────────>│                       │
 │                │                    │ Evaluate answer       │
 │                │                    │──────────────────────>│
 │                │                    │<──────────────────────│
 │ Feedback +     │                    │                       │
 │ next question  │<───────────────────│                       │
 │   ...repeat... │                    │                       │
 │ End Interview  │                    │                       │
 │───────────────>│                    │                       │
 │                │ POST /tools/interview/end                 │
 │                │───────────────────>│                       │
 │ Summary with   │                    │                       │
 │ recommendations│<───────────────────│                       │
```

---

## Security & Best Practices

### Non-Negotiable Rules

1. **No CAPTCHA Bypass** - Automation aborts, flags for manual
2. **No ToS Violations** - Only safe ATS platforms (Greenhouse, Lever)
3. **Truth-Lock** - All AI content verified against resume
4. **Audit Everything** - Complete logs + screenshots
5. **No Hardcoded Secrets** - Everything via environment variables

### Authentication Security

```python
# Passwords: bcrypt with cost factor
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# JWTs: Short-lived access, longer refresh
access_token: 30 minutes
refresh_token: 7 days

# OAuth providers: Google and GitHub
# Uses authorization code flow with PKCE

# Sensitive data: Pydantic SecretStr
jwt_secret_key: SecretStr  # Never logged or exposed
together_api_key: SecretStr
sendgrid_api_key: SecretStr
```

### Rate Limiting

```python
# Redis-based sliding window rate limiting
# Configurable limits per plan:
#   Free:    100 requests/minute
#   Premium: 500 requests/minute
#   Elite:   2000 requests/minute

# Headers returned:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

### Feature Flags

```python
# Gradual feature rollout via settings
feature_company_intel: bool = True
feature_gamification: bool = True
feature_wellness: bool = True
feature_advanced_analytics: bool = True
```

---

## Glossary

| Term | Definition |
|------|------------|
| **ATS** | Applicant Tracking System - Software companies use to manage applications (Greenhouse, Lever) |
| **AutoGen** | Microsoft's framework for building multi-agent AI systems |
| **Celery** | Distributed task queue for Python, processes background jobs |
| **ChromaDB** | Vector database for storing and searching embeddings |
| **CORS** | Cross-Origin Resource Sharing - Browser security for API requests |
| **DIP** | Dependency Inversion Principle - Core depends on abstractions |
| **dnd-kit** | React drag-and-drop library for Kanban board |
| **Embedding** | Vector representation of text for semantic similarity search |
| **FastAPI** | Modern Python web framework with automatic OpenAPI docs |
| **GroupChat** | AutoGen feature for coordinating multiple AI agents |
| **Immer** | Library for immutable state updates in JavaScript |
| **JWT** | JSON Web Token - Secure token for authentication |
| **Kanban** | Visual board with columns representing application stages |
| **LLM** | Large Language Model - AI model like DeepSeek, Llama, Qwen |
| **MinIO** | S3-compatible object storage for files |
| **OAuth** | Open Authorization - Protocol for secure delegated access |
| **ORM** | Object-Relational Mapping - Map database tables to classes |
| **Port** | Interface defining what the core layer needs (Protocol) |
| **Rate Limiting** | Control API request frequency per user/IP |
| **Redis** | In-memory data store for caching and queuing |
| **SendGrid** | Email delivery service for notifications |
| **Truth-Lock** | System ensuring AI doesn't fabricate information |
| **Vector Search** | Finding similar documents using embedding similarity |
| **WeasyPrint** | Python library for HTML to PDF conversion |
| **Zod** | TypeScript library for runtime type validation |
| **Zustand** | Lightweight state management for React |

---

## Quick Start Commands

```bash
# Start all services
make dev

# Individual services
make backend    # FastAPI server
make frontend   # Next.js dev server
make worker     # Celery worker

# Database
make migrate    # Run migrations

# Testing
make test       # Run all tests
make lint       # Check code style
```

---

## Further Reading

- [DESIGN_DOCUMENT.md](./DESIGN_DOCUMENT.md) - Original design specifications
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Detailed setup instructions
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [AutoGen Docs](https://microsoft.github.io/autogen/)
- [Together AI Docs](https://docs.together.ai/)

---

*Document updated for ApplyBots v0.3.0 - Includes Career Tools, Company Intelligence, Gamification, Wellness, Resume Builder, Kanban Tracking, and Multi-Source Job Aggregation*
