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
│   │  Auth   │ │ Dashboard │ │  Jobs  │ │ Review   │ │  AI Chat    │   │
│   │ Pages   │ │   Page    │ │  List  │ │ Apps     │ │  Interface  │   │
│   └─────────┘ └───────────┘ └────────┘ └──────────┘ └─────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP/REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                      │
│                      (FastAPI Backend)                                  │
│   ┌────────┐ ┌─────────┐ ┌──────┐ ┌─────────────┐ ┌─────────┐         │
│   │ /auth  │ │/profile │ │/jobs │ │/applications│ │/agents  │ /billing│
│   └────────┘ └─────────┘ └──────┘ └─────────────┘ └─────────┘         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   AI AGENTS     │   │  BACKGROUND     │   │  DATA LAYER     │
│   (AutoGen)     │   │  WORKERS        │   │                 │
│                 │   │  (Celery)       │   │  PostgreSQL     │
│  ┌───────────┐  │   │                 │   │  Redis          │
│  │Orchestrate│  │   │  Job Ingestion  │   │  MinIO (S3)     │
│  │ Resume    │  │   │  App Submitter  │   │  ChromaDB       │
│  │ Match     │  │   │                 │   │                 │
│  │ Apply     │  │   └─────────────────┘   └─────────────────┘
│  │ QC        │  │
│  └───────────┘  │
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
    
    def verify(
        self,
        *,
        content: str,        # AI-generated text
        resume: ParsedResume,
        job: Job,
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

Handles resume upload, text extraction, and parsing:

```python
class ResumeService:
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
        4. Save to database
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
```

---

### API Layer

REST API endpoints built with FastAPI:

#### Router Structure (`api/v1/router.py`)

```python
api_router = APIRouter()

# All available endpoints:
api_router.include_router(auth.router, prefix="/auth")           # Authentication
api_router.include_router(profile.router, prefix="/profile")     # User profile
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
| `/profile` | GET | Get user profile |
| `/profile` | PUT | Update profile |
| `/profile/resume` | POST | Upload resume |
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

AI-powered multi-agent system using AutoGen:

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

#### Workflow Orchestration (`agents/workflows.py`)

```python
class JobApplicationWorkflow:
    """Orchestrates multi-agent job application process."""
    
    async def process_message(self, message: str) -> AgentResponse:
        """
        Process user message:
        1. Analyze intent (job search, resume, apply, general)
        2. Route to appropriate handler
        3. Coordinate agent responses
        """
    
    async def stream_process(self, message: str) -> AsyncIterator[StreamResponse]:
        """Stream agent responses for real-time UI updates."""
    
    async def optimize_resume(self, *, resume_id: str, job_id: str) -> OptimizationResult:
        """
        Optimize resume for specific job:
        1. Calculate match score
        2. Identify skill gaps
        3. Generate tailored summary
        4. Suggest improvements
        """
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
}
```

#### Task Types

**Job Ingestion** - Fetches new jobs from sources:

```python
@celery_app.task
def ingest_jobs_scheduled():
    """
    Scheduled task to fetch new jobs:
    1. Query Remotive API for new listings
    2. Deduplicate against existing jobs
    3. Extract requirements with AI
    4. Generate embeddings for search
    5. Store in database
    """
```

**Application Submitter** - Automated form filling:

```python
@celery_app.task
def submit_application(application_id: str):
    """
    Submit approved application:
    1. Load application data
    2. Detect ATS type (Greenhouse, Lever)
    3. Launch browser with Playwright
    4. Fill form fields
    5. Capture screenshots at each step
    6. Handle errors (CAPTCHA → manual)
    7. Update status
    """
```

---

## Frontend Deep Dive

### Frontend Project Structure

```
frontend/src/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group (no layout)
│   │   ├── login/page.tsx        # Login page
│   │   └── signup/page.tsx       # Signup page
│   │
│   ├── (dashboard)/              # Dashboard route group (with layout)
│   │   ├── layout.tsx            # Sidebar layout
│   │   └── dashboard/
│   │       ├── page.tsx          # Main dashboard
│   │       ├── jobs/page.tsx     # Job listings
│   │       ├── applications/page.tsx
│   │       ├── chat/page.tsx     # AI assistant
│   │       ├── profile/page.tsx
│   │       └── billing/page.tsx
│   │
│   ├── api/v1/[...path]/route.ts # API proxy to backend
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Landing page
│
├── hooks/                        # Custom React hooks
│   ├── useJobs.ts               # Job data fetching
│   └── useApplications.ts       # Application data fetching
│
├── lib/                         # Utilities
│   ├── api.ts                   # Typed API client
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

// Type-safe API client
class APIClient {
  async getJobs(params): Promise<JobListResponse> {
    return this.request(`/jobs?${query}`, {}, JobListResponseSchema);
  }
  
  async createApplication(jobId: string): Promise<Application> {
    return this.request("/applications", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId }),
    });
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
| `users` | User accounts |
| `profiles` | User preferences, contact info |
| `resumes` | Uploaded resumes with parsed data |
| `jobs` | Job listings with embeddings |
| `applications` | Application records & status |
| `subscriptions` | Plan & billing info |
| `refresh_sessions` | JWT refresh tokens |
| `agent_sessions` | AI chat history |
| `audit_logs` | Automation action logs |

### Redis (Cache & Queue)

- **Session cache** - Fast user lookups
- **Rate limiting** - Track API requests
- **Celery broker** - Task message queue
- **Celery backend** - Task results storage

### MinIO (Object Storage)

S3-compatible storage for:

- **Resumes** - Original PDF/DOCX files
- **Screenshots** - Automation audit trail
- **Generated documents** - Cover letters

### ChromaDB (Vector Database)

Stores embeddings for semantic search:

```python
# Example: Find similar jobs to resume
resume_embedding = embed(resume_text)  # 1536-dimensional vector
similar_jobs = chromadb.query(
    embedding=resume_embedding,
    n_results=10,
)
```

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

# Sensitive data: Pydantic SecretStr
jwt_secret_key: SecretStr  # Never logged or exposed
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
| **CORS** | Cross-Origin Resource Sharing - Browser security for API requests |
| **DIP** | Dependency Inversion Principle - Core depends on abstractions, not implementations |
| **Embedding** | Vector representation of text for semantic similarity search |
| **FastAPI** | Modern Python web framework with automatic OpenAPI docs |
| **JWT** | JSON Web Token - Secure token for authentication |
| **LLM** | Large Language Model - AI model like DeepSeek, Llama, Qwen |
| **MinIO** | S3-compatible object storage for files |
| **ORM** | Object-Relational Mapping - Map database tables to Python classes |
| **Port** | Interface defining what the core layer needs (Protocol in Python) |
| **Redis** | In-memory data store for caching and message queuing |
| **Truth-Lock** | System ensuring AI doesn't fabricate information |
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

*Document generated for ApplyBots v0.1.0*
