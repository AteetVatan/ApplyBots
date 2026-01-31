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

1. **Discover Jobs** - Automatically finds and matches jobs to your profile
2. **Generate Applications** - Creates tailored cover letters and answers using AI
3. **Submit Applications** - Automates form filling on job application portals
4. **Track Everything** - Maintains complete audit trails and screenshots

### Key Principle: Truth-Lock Technology

The platform **NEVER fabricates information**. All AI-generated content is verified against your actual resume to ensure 100% truthfulness.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│                    (Browser - Next.js Frontend)                         │
│   ┌─────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ ┌─────────────┐   │
│   │  Auth   │ │ Dashboard │ │  Jobs  │ │ Resumes  │ │  AI Chat    │   │
│   │ (OAuth) │ │   Page    │ │  List  │ │ Manager  │ │  Interface  │   │
│   └─────────┘ └───────────┘ └────────┘ └──────────┘ └─────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP/REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                      │
│                  (FastAPI Backend + Rate Limiting)                      │
│   ┌────────┐ ┌─────────┐ ┌──────┐ ┌─────────────┐ ┌─────────┐         │
│   │ /auth  │ │/resumes │ │/jobs │ │/applications│ │/agents  │ /billing│
│   └────────┘ └─────────┘ └──────┘ └─────────────┘ └─────────┘         │
└────────────────────────────────┬────────────────────────────────────────┘
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
│  │ Match     │  │   │  Status Monitor │   │                 │
│  │ Apply     │  │   │  Email Notifs   │   │                 │
│  │ QC/Critic │  │   └─────────────────┘   └─────────────────┘
│  └───────────┘  │           │
└─────────────────┘           ▼
         │            ┌─────────────────┐
         │            │  EXTERNAL APIs  │
         └───────────>│  SendGrid       │
                      │  Google OAuth   │
                      │  GitHub OAuth   │
                      │  Together AI    │
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
| **PyMuPDF** | PDF processing | 1.24.0 | Extract text from resumes |
| **MinIO** | Object storage | Latest | S3-compatible file storage |
| **ChromaDB** | Vector database | 0.4.22 | Semantic search with embeddings |
| **Pydantic** | Data validation | 2.6.3 | Type validation & settings |
| **Together AI** | LLM provider | - | AI model API (DeepSeek, Llama 4, Qwen) |
| **SendGrid** | Email service | - | Transactional email notifications |
| **BeautifulSoup** | Web scraping | 4.12 | HTML parsing for job scrapers |
| **prometheus_client** | Metrics | - | Application monitoring |

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
| **Radix UI** | UI components | Various | Accessible component primitives |
| **Framer Motion** | Animations | 10.18.0 | Smooth UI animations |

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
│   │   ├── domain/          # Domain entities (User, Job, Application, etc.)
│   │   ├── ports/           # Interfaces (Protocols) for dependencies
│   │   ├── services/        # Business logic services
│   │   └── exceptions.py    # Domain-specific exceptions
│   │
│   ├── infra/               # 🔌 INFRASTRUCTURE (IO Operations)
│   │   ├── db/              # Database models & repositories
│   │   ├── auth/            # JWT authentication implementation
│   │   ├── storage/         # S3/MinIO file storage
│   │   ├── ats_adapters/    # Greenhouse, Lever automation
│   │   └── services/        # Resume parsing, billing, etc.
│   │
│   ├── api/                 # 🌐 REST API LAYER
│   │   ├── v1/              # API version 1 endpoints
│   │   └── deps.py          # Dependency injection
│   │
│   ├── agents/              # 🤖 AI AGENT ORCHESTRATION
│   │   ├── workflows.py     # Agent coordination logic
│   │   ├── prompts.py       # System prompts for each agent
│   │   └── config.py        # LLM configurations
│   │
│   ├── workers/             # ⚙️ BACKGROUND TASKS
│   │   ├── celery_app.py    # Celery configuration
│   │   ├── job_ingestion.py # Scheduled job scraping
│   │   └── application_submitter.py
│   │
│   └── schemas/             # 📋 API Request/Response Models
│       ├── auth.py
│       ├── job.py
│       └── application.py
│
├── migrations/              # Database migrations (Alembic)
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container image definition
```

### Core Layer (Business Logic)

The **Core Layer** contains pure business logic with **NO external dependencies** (no database calls, no HTTP requests). This makes it:
- Easy to test (no mocking needed)
- Easy to understand (just Python logic)
- Reusable across different implementations

#### Domain Models (`core/domain/`)

Domain models are simple Python dataclasses representing business entities:

```python
# User - Represents a platform user
@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: UserRole        # Enum: USER or ADMIN
    email_verified: bool
    created_at: datetime

# Job - A job listing
@dataclass  
class Job:
    id: str
    external_id: str       # ID from source system
    title: str
    company: str
    location: str | None
    description: str
    url: str
    source: JobSource      # Enum: REMOTIVE, GREENHOUSE, LEVER, MANUAL
    salary_min: int | None
    salary_max: int | None
    remote: bool
    requirements: JobRequirements  # skills, experience, education
    embedding: list[float] | None  # For semantic search

# Application - A job application
@dataclass
class Application:
    id: str
    user_id: str
    job_id: str
    resume_id: str
    status: ApplicationStatus  # PENDING_REVIEW, APPROVED, SUBMITTING, etc.
    match_score: int           # 0-100 compatibility score
    match_explanation: MatchExplanation | None
    cover_letter: str | None
    generated_answers: dict[str, str]  # Question -> Answer
    qc_approved: bool          # Quality control approval

# Campaign - Job application campaign for organized job searching
@dataclass
class Campaign:
    id: str
    user_id: str
    name: str
    target_roles: list[str]
    target_locations: list[str]
    status: CampaignStatus     # DRAFT, ACTIVE, PAUSED, COMPLETED, ARCHIVED
    start_date: datetime
    end_date: datetime | None
    jobs_applied: int
    interviews_secured: int
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

# Storage interface - defines file operations
class FileStorage(Protocol):
    async def upload(self, *, key: str, data: bytes, content_type: str) -> str: ...
    async def download(self, *, key: str) -> bytes: ...
    async def delete(self, *, key: str) -> None: ...
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
        preferences: Preferences | None
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

**CoverLetterService** - Generates personalized cover letters:

```python
class CoverLetterService:
    """Service for generating and verifying cover letters."""
    
    async def generate_cover_letter(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        user_id: str,
    ) -> CoverLetterResult:
        """
        1. Generate cover letter using LLM
        2. Verify with Truth-Lock
        3. Return content with verification status
        """
```

**QuestionAnswererService** - Answers screening questions:

```python
class QuestionAnswererService:
    """Service for answering job application screening questions."""
    
    async def answer_question(
        self,
        *,
        question: str,
        resume: ParsedResume,
        job: Job,
        user_id: str,
    ) -> QuestionAnswerResult:
        """
        1. Generate answer based on resume and job context
        2. Verify with Truth-Lock
        3. Return answer with verification status
        """
```

**SkillGapService** - Analyzes skill gaps and recommends courses:

```python
class SkillGapService:
    """Service for analyzing skill gaps and recommending learning resources."""
    
    async def analyze_skill_gap(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        user_id: str,
    ) -> SkillGapAnalysis:
        """
        1. Compare resume skills vs job requirements
        2. Identify missing skills
        3. Suggest relevant courses/resources
        """
```

**RecruiterOutreachService** - Generates personalized outreach messages:

```python
class RecruiterOutreachService:
    """Service for generating personalized recruiter outreach messages."""
    
    async def generate_outreach_message(
        self,
        *,
        user_profile: Profile,
        resume: ParsedResume,
        job: Job,
        recruiter_name: str | None = None,
    ) -> OutreachMessage:
        """
        Generate professional outreach message for recruiters.
        """
```

**AnalyticsService** - Interview preparation analytics:

```python
class AnalyticsService:
    """Service for generating interview preparation analytics."""
    
    async def get_interview_prep_analytics(
        self,
        *,
        resume: ParsedResume,
        job: Job,
        user_id: str,
    ) -> InterviewPrepAnalytics:
        """
        1. Analyze resume against job description
        2. Generate potential interview questions
        3. Identify weak areas to prepare for
        """
```

**ABTestingService** - A/B testing for resumes:

```python
class ABTestingService:
    """Service for A/B testing different resume versions."""
    
    async def run_resume_ab_test(
        self,
        *,
        user_id: str,
        resume_a_id: str,
        resume_b_id: str,
        duration_days: int = 7,
    ) -> ResumeABTestResult:
        """
        Compare two resume versions by tracking application outcomes.
        """
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

# Authorization  
class PlanLimitExceededError(AuthorizationError)  # Daily limit reached
class InsufficientPermissionsError(AuthorizationError)

# Application Processing
class TruthLockViolationError(ApplicationError)  # AI generated false info
class QCRejectionError(ApplicationError)          # Failed quality check

# Automation
class CaptchaDetectedError(AutomationError)       # Manual intervention needed
class MFARequiredError(AutomationError)           # 2FA blocking automation
class FormFieldNotFoundError(AutomationError)     # Form structure changed
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
    applications: Mapped[List["ApplicationModel"]] = relationship(back_populates="user")
```

**Repositories** (`db/repositories/`) - Implement port interfaces:

```python
class SQLUserRepository:
    """SQLAlchemy implementation of UserRepository port."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
```

#### Authentication (`infra/auth/`)

**JWT Token Management** (`jwt.py`):

```python
def create_token(
    *,
    user_id: str,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta,
    token_type: Literal["access", "refresh"],
) -> str:
    """Create a JWT token with expiration."""

def decode_access_token(*, token: str, secret_key: str, algorithm: str) -> dict:
    """Decode and validate access token."""
```

**Password Hashing** (`password.py`):

```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""

def verify_password(password: str, hash: str) -> bool:
    """Verify password against hash."""
```

**Auth Service** (`service.py`):

```python
class AuthService:
    async def signup(self, *, email: str, password: str, full_name: str) -> TokenPair:
        """Create account, return access + refresh tokens."""
    
    async def login(self, *, email: str, password: str) -> TokenPair:
        """Authenticate user, return tokens."""
    
    async def refresh(self, *, refresh_token: str) -> TokenPair:
        """Get new tokens using refresh token."""
    
    async def oauth_login_or_signup(self, *, user_info: OAuthUserInfo) -> TokenPair:
        """Login or signup user via OAuth (Google, GitHub)."""
```

**OAuth Clients** (`oauth.py`):

```python
class GoogleOAuthClient:
    """Google OAuth client for authentication."""
    
    def get_authorization_url(self) -> str:
        """Generate Google OAuth authorization URL."""
    
    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token."""
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Fetch user information from Google."""

class GitHubOAuthClient:
    """GitHub OAuth client for authentication."""
    # Similar methods as GoogleOAuthClient
```

#### Email Notifications (`infra/notifications/`)

**SendGrid Email Service** (`email.py`):

```python
class SendGridEmailService:
    """SendGrid implementation of EmailService."""
    
    async def send_email(self, *, message: EmailMessage) -> None:
        """Send an email using SendGrid API."""
```

#### Storage (`infra/storage/`)

**S3-Compatible Storage** (`s3.py`):

```python
class S3FileStorage:
    """MinIO/S3 file storage implementation."""
    
    async def upload(self, *, key: str, data: bytes, content_type: str) -> str:
        """Upload file to S3, return URL."""
        
    async def download(self, *, key: str) -> bytes:
        """Download file from S3."""
        
    async def get_presigned_url(self, *, key: str, expires_in: int) -> str:
        """Get temporary URL for file access."""
```

#### ATS Adapters (`infra/ats_adapters/`)

Adapters for different Applicant Tracking Systems:

```python
class BaseATSAdapter(ABC):
    """Base class for ATS automation."""
    
    @abstractmethod
    async def detect(self, *, url: str) -> bool:
        """Check if this adapter handles the URL."""
    
    @abstractmethod
    async def fill_form(self, *, page: Page, data: ApplicationData) -> None:
        """Fill the application form."""
    
    @abstractmethod
    async def submit(self, *, page: Page) -> SubmissionResult:
        """Submit the application."""
    
    async def check_blockers(self, *, page: Page) -> None:
        """Detect CAPTCHA, MFA - abort if found (never bypass!)."""
    
    async def _capture_screenshot(self, *, page: Page, step: str) -> str:
        """Capture screenshot for audit trail."""

# Implementations:
class GreenhouseAdapter(BaseATSAdapter):
    """Handles jobs.greenhouse.io applications."""

class LeverAdapter(BaseATSAdapter):
    """Handles jobs.lever.co applications."""
```

#### Resume Service (`infra/services/resume_service.py`)

Handles resume upload, text extraction, parsing, and embedding generation:

```python
class ResumeService:
    def __init__(
        self,
        *,
        storage: FileStorage,
        resume_repository: ResumeRepository,
        llm_client: LLMClient,      # For embedding generation
        vector_store: VectorStore,   # For storing embeddings
    ) -> None:
        ...
    
    async def upload_and_parse(
        self,
        *,
        user_id: str,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> Resume:
        """
        1. Upload to S3 storage
        2. Extract text (PDF or DOCX)
        3. Parse into structured data
        4. Generate embedding for semantic search
        5. Store embedding in vector database
        6. Save to database
        """
    
    async def _extract_pdf_text(self, content: bytes) -> str:
        """
        PDF extraction strategy:
        1. Try native text extraction (PyMuPDF)
        2. If empty, check for images (scanned PDF)
        3. If images found, attempt OCR (Tesseract)
        """
    
    async def _parse_resume_text(self, text: str) -> ParsedResume:
        """
        Extract structured data:
        - Full name, email, phone
        - Skills (keyword matching)
        - Work experience
        - Education
        """
    
    async def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding for text using LLM client."""
```

#### Job Scrapers (`infra/scrapers/`)

Web scrapers for external job boards:

```python
class BaseScraper:
    """Base class for web scrapers."""
    
    async def _get_page_content(self, url: str) -> str:
        """Fetch page content with httpx."""
    
    def _parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content."""

class StackOverflowScraper(BaseScraper, JobScraper):
    """Scraper for Stack Overflow job listings."""
    
    async def scrape_jobs(
        self, *, keywords: list[str], location: str | None = None, limit: int = 20
    ) -> list[Job]:
        """Scrape job listings from Stack Overflow."""

class WellFoundScraper(BaseScraper, JobScraper):
    """Scraper for Wellfound (formerly AngelList) job listings."""
    
    async def scrape_jobs(
        self, *, keywords: list[str], location: str | None = None, limit: int = 20
    ) -> list[Job]:
        """Scrape job listings from Wellfound."""
```

#### Rate Limiting (`api/middleware/rate_limit.py`)

Redis-based rate limiting:

```python
class RedisRateLimiter:
    """Redis implementation of RateLimiter using sliding window."""
    
    async def allow_request(self, *, key: str, limit: int, window: int) -> bool:
        """Check if a request is allowed."""
    
    async def get_remaining_requests(self, *, key: str, window: int) -> int:
        """Get remaining requests for a key within a window."""

class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply rate limiting to incoming requests."""
```

---

### API Layer

REST API endpoints built with FastAPI:

#### Router Structure (`api/v1/router.py`)

```python
api_router = APIRouter()

# All available endpoints:
api_router.include_router(auth.router, prefix="/auth")           # Authentication + OAuth
api_router.include_router(profile.router, prefix="/profile")     # User profile
api_router.include_router(resumes.router, prefix="/resumes")     # Resume management
api_router.include_router(jobs.router, prefix="/jobs")           # Job listings
api_router.include_router(applications.router, prefix="/applications")  # Applications
api_router.include_router(agents.router, prefix="/agents")       # AI chat
api_router.include_router(billing.router, prefix="/billing")     # Subscriptions
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
| `/profile` | GET | Get user profile |
| `/profile` | PUT | Update profile |
| `/resumes/upload` | POST | Upload new resume |
| `/resumes` | GET | List user's resumes |
| `/resumes/{id}` | GET | Get resume details |
| `/resumes/{id}` | DELETE | Delete a resume |
| `/resumes/{id}/set-primary` | POST | Set resume as primary |
| `/jobs` | GET | List matching jobs |
| `/jobs/{id}` | GET | Get job details |
| `/jobs/refresh` | POST | Trigger job ingestion |
| `/applications` | GET | List user's applications |
| `/applications` | POST | Create new application |
| `/applications/{id}/approve` | POST | Approve for submission |
| `/agents/chat` | POST | Send message to AI |
| `/agents/chat/stream` | POST | Stream AI response |
| `/billing/usage` | GET | Get usage stats |
| `/billing/checkout` | POST | Start Stripe checkout |

#### Dependency Injection (`api/deps.py`)

FastAPI dependencies for common operations:

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Extract and validate user from JWT token."""

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session with automatic cleanup."""
```

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
    
    # Reasoning models
    DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1-0528"
    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3.1"
    
    # Fast extraction
    LLAMA4_SCOUT = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
    LLAMA4_MAVERICK = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    
    # Content generation
    LLAMA3_70B = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    
    # Document understanding
    QWEN3_235B = "Qwen/Qwen3-235B-A22B-fp8-tput"
    
    # Embeddings
    BGE_LARGE = "BAAI/bge-large-en-v1.5"
```

#### Agent Tools (`agents/tools.py`)

Functions that AutoGen agents can call:

```python
# Tools for database interactions
async def get_jobs(user_id: str, limit: int = 10, offset: int = 0, query: str | None = None) -> str:
    """Get a list of jobs matching user preferences."""

async def get_job_by_id(job_id: str) -> str:
    """Get details of a specific job by its ID."""

async def get_primary_resume(user_id: str) -> str:
    """Get the user's primary resume."""

async def optimize_resume(resume_id: str, job_id: str) -> str:
    """Optimize a resume for a specific job."""

async def create_application(user_id: str, job_id: str, resume_id: str) -> str:
    """Create a new job application."""
```

#### Workflow Orchestration (`agents/workflows.py`)

Uses AutoGen's GroupChat for multi-agent collaboration:

```python
class JobApplicationWorkflow:
    """Orchestrates multi-agent job application process using AutoGen GroupChat."""
    
    def __init__(self, *, user_id: str, db_session: AsyncSession, settings: Settings, ...):
        self._agents = self._setup_autogen_agents()
        self._groupchat = GroupChat(
            agents=list(self._agents.values()),
            messages=[],
            max_round=20,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
        )
        self._manager = GroupChatManager(
            groupchat=self._groupchat,
            llm_config=LLM_CONFIG_ORCHESTRATOR,
        )
    
    def _setup_autogen_agents(self) -> dict[str, Agent]:
        """Set up AutoGen agents with their configurations and tools."""
        # UserProxyAgent for tool execution
        user_proxy = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
        )
        
        # Register tools with user_proxy
        user_proxy.register_function(
            function_map={
                "get_jobs": get_jobs,
                "get_job_by_id": get_job_by_id,
                "get_primary_resume": get_primary_resume,
                "optimize_resume": optimize_resume,
                "create_application": create_application,
            }
        )
        
        # Define specialized agents
        orchestrator = AssistantAgent(name="Orchestrator", ...)
        resume_agent = AssistantAgent(name="ResumeAgent", ...)
        match_agent = AssistantAgent(name="MatchAgent", ...)
        # ... more agents
        
        return {
            "user_proxy": user_proxy,
            "orchestrator": orchestrator,
            "resume_agent": resume_agent,
            # ...
        }
    
    async def process_message(self, message: str, session_id: str | None = None) -> AgentResponse:
        """
        Process user message through AutoGen GroupChat:
        1. Add message to group chat
        2. Initiate chat with GroupChatManager
        3. Agents collaborate to respond
        4. Return final response with involved agents
        """
    
    async def stream_process(self, message: str) -> AsyncIterator[StreamResponse]:
        """Stream agent responses for real-time UI updates."""
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
    ],
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "ingest-jobs-hourly": {
        "task": "app.workers.job_ingestion.ingest_jobs_scheduled",
        "schedule": 3600.0,  # Every hour
    },
    "reset-daily-usage": {
        "task": "app.workers.job_ingestion.reset_daily_usage",
        "schedule": 86400.0,  # Every 24 hours
    },
    "monitor-applications-daily": {
        "task": "app.workers.status_monitor.monitor_applications_task",
        "schedule": 86400.0,  # Every 24 hours
    },
}
```

#### Task Types

**Job Ingestion** - Fetches new jobs from sources with embedding generation:

```python
@celery_app.task
def ingest_jobs_scheduled():
    """
    Scheduled task to fetch new jobs:
    1. Query Remotive API for new listings
    2. Deduplicate against existing jobs
    3. Extract requirements with AI
    4. Generate embeddings for semantic search
    5. Store embeddings in ChromaDB
    6. Store job data in database
    """
```

**Application Submitter** - Automated form filling with ATS adapters:

```python
@celery_app.task
def submit_application(application_id: str):
    """
    Submit approved application:
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

**Status Monitor** - Monitors application statuses and sends notifications:

```python
@celery_app.task
def monitor_applications_task():
    """
    Monitor application statuses:
    1. Fetch applications due for status check
    2. Check external ATS for status updates
    3. Update application status in database
    4. Send email notification via SendGrid
    5. Log status changes
    """
```

---

## Frontend Deep Dive

### Frontend Project Structure

```
frontend/src/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group (no layout)
│   │   ├── login/page.tsx        # Login page (with OAuth buttons)
│   │   └── signup/page.tsx       # Signup page (with OAuth buttons)
│   │
│   ├── (dashboard)/              # Dashboard route group (with layout)
│   │   ├── layout.tsx            # Sidebar layout
│   │   └── dashboard/
│   │       ├── page.tsx          # Main dashboard
│   │       ├── jobs/page.tsx     # Job listings
│   │       ├── applications/page.tsx
│   │       ├── resumes/page.tsx  # Resume management
│   │       ├── chat/page.tsx     # AI assistant
│   │       ├── profile/page.tsx
│   │       └── billing/page.tsx
│   │
│   ├── api/v1/[...path]/route.ts # API proxy to backend
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Landing page
│
├── components/ui/                # Reusable UI components
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── input.tsx
│   └── ...
│
├── hooks/                        # Custom React hooks
│   ├── useJobs.ts               # Job data fetching
│   └── useApplications.ts       # Application data fetching
│
├── lib/                         # Utilities
│   ├── api.ts                   # Typed API client with Zod schemas
│   └── utils.ts                 # Helper functions
│
└── providers/                   # React Context providers
    ├── AuthProvider.tsx         # Authentication state
    └── Providers.tsx            # Combined providers wrapper
```

### Key Frontend Concepts

#### App Router (Next.js 14+)

- **Route Groups** `(auth)`, `(dashboard)` - Organize without affecting URL
- **Layouts** - Shared UI (sidebar) for nested routes
- **Server Components** - Default, render on server
- **Client Components** - Use `"use client"` for interactivity

#### API Client (`lib/api.ts`)

```typescript
// Zod schemas validate API responses at runtime
export const JobSchema = z.object({
  id: z.string(),
  title: z.string(),
  company: z.string(),
  location: z.string().nullable(),
  remote: z.boolean(),
  salary_min: z.number().nullable(),
  salary_max: z.number().nullable(),
  match_score: z.number().nullable(),
});

export const ResumeSchema = z.object({
  id: z.string(),
  filename: z.string(),
  is_primary: z.boolean(),
  uploaded_at: z.string(),
  parsed_data: z.object({
    full_name: z.string().nullable(),
    email: z.string().nullable(),
    phone: z.string().nullable(),
    skills: z.array(z.string()),
    total_years_experience: z.number().nullable(),
  }).nullable(),
});

// Type-safe API client
class APIClient {
  // Jobs
  async getJobs(params): Promise<JobListResponse> {
    return this.request(`/jobs?${query}`, {}, JobListResponseSchema);
  }
  
  async createApplication(jobId: string): Promise<Application> {
    return this.request("/applications", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId }),
    });
  }
  
  // Resumes
  async getResumes(): Promise<ResumeListResponse> {
    return this.request("/resumes", {}, ResumeListResponseSchema);
  }
  
  async uploadResume(file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append("file", file);
    return this.request("/resumes/upload", {
      method: "POST",
      body: formData,
    });
  }
  
  async deleteResume(id: string): Promise<void> {
    await this.request(`/resumes/${id}`, { method: "DELETE" });
  }
  
  async setPrimaryResume(id: string): Promise<Resume> {
    return this.request(`/resumes/${id}/set-primary`, { method: "POST" });
  }
}
```

#### Authentication (`providers/AuthProvider.tsx`)

```typescript
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// Token management
const TOKEN_KEY = "ApplyBots_access_token";
const REFRESH_KEY = "ApplyBots_refresh_token";

// Usage in components
function Dashboard() {
  const { user, logout } = useAuth();
  
  if (!user) return <Redirect to="/login" />;
  
  return <div>Welcome, {user.email}</div>;
}
```

---

## Infrastructure Services

### PostgreSQL (Database)

Primary relational database storing:

| Table | Purpose |
|-------|---------|
| `users` | User accounts (includes OAuth fields) |
| `profiles` | User preferences, contact info, negative keywords |
| `resumes` | Uploaded resumes with parsed data & embeddings |
| `jobs` | Job listings with embeddings |
| `applications` | Application records & status |
| `campaigns` | Job search campaigns for organized tracking |
| `subscriptions` | Plan & billing info |
| `refresh_sessions` | JWT refresh tokens |
| `agent_sessions` | AI chat history |
| `audit_logs` | Automation action logs |

**Key Fields Added:**

```python
# User model - OAuth support
class UserModel(Base):
    ...
    oauth_provider: str | None       # "google" or "github"
    oauth_provider_id: str | None    # Provider's user ID

# Profile model - Negative keywords
class ProfileModel(Base):
    ...
    preferences: dict  # Includes negative_keywords: list[str]

# Resume model - Embeddings
class ResumeModel(Base):
    ...
    embedding: list[float] | None    # Vector for semantic search
```

### Redis (Cache & Queue)

- **Session cache** - Fast user lookups
- **Rate limiting** - Sliding window counter for API requests
- **Celery broker** - Task message queue
- **Celery backend** - Task results storage

**Rate Limiting Keys:**

```
# Format: rate_limit:{user_id}:{endpoint}
rate_limit:user123:/api/v1/jobs

# Sliding window implementation
# Stores timestamps as sorted set scores
ZADD key timestamp member
ZCOUNT key (now - window) now
```

### MinIO (Object Storage)

S3-compatible storage for:

- **Resumes** - Original PDF/DOCX files
- **Screenshots** - Automation audit trail
- **Generated documents** - Cover letters

### ChromaDB (Vector Database)

Stores embeddings for semantic search:

**Collections:**

| Collection | Purpose |
|------------|---------|
| `resumes` | Resume embeddings for matching |
| `jobs` | Job description embeddings |

```python
# Adding embeddings during ingestion
await vector_store.add_embedding(
    collection="jobs",
    doc_id=job.id,
    embedding=embedding,
    metadata={
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote": job.remote,
    },
)

# Searching for similar jobs
similar_jobs = await vector_store.search_by_embedding(
    collection="jobs",
    embedding=resume_embedding,  # 1024-dimensional vector (BGE-Large)
    top_k=10,
)
```

**Embedding Model:**
- Model: `BAAI/bge-large-en-v1.5`
- Dimensions: 1024
- Provider: Together AI

---

## Data Flow Diagrams

### User Signup Flow

```
User                Frontend            Backend              Database
 │                     │                  │                    │
 │ Enter email/pass    │                  │                    │
 │────────────────────>│                  │                    │
 │                     │ POST /auth/signup│                    │
 │                     │─────────────────>│                    │
 │                     │                  │ Check email exists │
 │                     │                  │───────────────────>│
 │                     │                  │<───────────────────│
 │                     │                  │ Hash password      │
 │                     │                  │ Create user        │
 │                     │                  │───────────────────>│
 │                     │                  │ Create profile     │
 │                     │                  │───────────────────>│
 │                     │                  │ Generate JWT       │
 │                     │ tokens (access,  │                    │
 │                     │<─────────refresh)│                    │
 │ Store in localStorage                  │                    │
 │<────────────────────│                  │                    │
 │ Redirect /dashboard │                  │                    │
```

### Job Application Flow

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
 │                │ Application   │                  │               │
 │                │<─────created──│                  │               │
 │ Review & Edit  │               │                  │               │
 │───────────────>│               │                  │               │
 │                │ POST /approve │                  │               │
 │                │──────────────>│                  │               │
 │                │               │ Queue submission │               │
 │                │               │─────────────────>│               │
 │                │               │                  │ Launch browser│
 │                │               │                  │──────────────>│
 │                │               │                  │ Fill form     │
 │                │               │                  │ Screenshot    │
 │                │               │                  │<──────────────│
 │                │               │ Update status    │               │
 │                │ Status update │<─────────────────│               │
 │<───────────────│               │                  │               │
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
# Securely stores client secrets in environment variables

# Sensitive data: Pydantic SecretStr
jwt_secret_key: SecretStr  # Never logged or exposed
google_oauth_client_secret: SecretStr
github_oauth_client_secret: SecretStr
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

### Data Protection

- **GDPR-aligned** - User data export/delete
- **No PII in logs** - Structured logging sanitizes sensitive fields
- **Encrypted storage** - Sensitive fields encrypted at rest

---

## Glossary

| Term | Definition |
|------|------------|
| **ATS** | Applicant Tracking System - Software companies use to manage applications (Greenhouse, Lever) |
| **AutoGen** | Microsoft's framework for building multi-agent AI systems |
| **Celery** | Distributed task queue for Python, processes background jobs |
| **ChromaDB** | Vector database for storing and searching embeddings |
| **CORS** | Cross-Origin Resource Sharing - Browser security for API requests |
| **DIP** | Dependency Inversion Principle - Core depends on abstractions, not implementations |
| **Embedding** | Vector representation of text for semantic similarity search |
| **FastAPI** | Modern Python web framework with automatic OpenAPI docs |
| **GroupChat** | AutoGen feature for coordinating multiple AI agents in conversation |
| **JWT** | JSON Web Token - Secure token for authentication |
| **LLM** | Large Language Model - AI model like DeepSeek, Llama, Qwen |
| **MinIO** | S3-compatible object storage for files |
| **OAuth** | Open Authorization - Protocol for secure delegated access (Google, GitHub login) |
| **ORM** | Object-Relational Mapping - Map database tables to Python classes |
| **Port** | Interface defining what the core layer needs (Protocol in Python) |
| **Rate Limiting** | Mechanism to control API request frequency per user/IP |
| **Redis** | In-memory data store for caching and message queuing |
| **SendGrid** | Email delivery service for transactional emails |
| **Truth-Lock** | System ensuring AI doesn't fabricate information |
| **Vector Search** | Finding similar documents using embedding similarity |
| **Zod** | TypeScript library for runtime type validation |

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

---

*Document updated for ApplyBots v0.2.0 - Includes AutoGen GroupChat, OAuth, Resume Management, and more*
