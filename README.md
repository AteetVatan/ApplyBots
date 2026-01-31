# ApplyBots - AI-Powered Job Application Platform

An agentic AI-powered automated job application platform that helps job seekers discover opportunities, generate tailored applications, and submit them efficiently while maintaining complete truthfulness.

## 🌟 Features

- **Smart Job Matching** - AI analyzes your resume against job requirements with detailed scoring
- **Truth-Lock Technology** - Ensures all generated content is factually accurate to your resume
- **Automated Applications** - Playwright-based automation for Greenhouse and Lever ATS systems
- **Human-in-the-Loop** - Review and edit everything before submission
- **Audit Trail** - Complete logging and screenshots of every automation step
- **Multi-Agent System** - AutoGen-powered agents for specialized tasks

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js App Router)                 │
│  ┌─────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ │
│  │  Auth   │ │ Dashboard │ │  Jobs  │ │ Review   │ │  Chat   │ │
│  └─────────┘ └───────────┘ └────────┘ └──────────┘ └─────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    API Gateway (FastAPI)                         │
│  /auth  /profile  /jobs  /applications  /agents  /billing       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               AutoGen Agent Orchestration                        │
│  ┌────────────┐ ┌────────┐ ┌───────┐ ┌───────┐ ┌────┐ ┌──────┐ │
│  │Orchestrator│ │ Resume │ │ Match │ │ Apply │ │ QC │ │Critic│ │
│  └────────────┘ └────────┘ └───────┘ └───────┘ └────┘ └──────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               Background Workers (Celery)                        │
│  ┌──────────────────┐ ┌─────────────────────────┐               │
│  │  Job Ingestion   │ │  Application Submitter  │               │
│  └──────────────────┘ └─────────────────────────┘               │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────┐ ┌───────┐ ┌───────┐ ┌─────────┐ ┌────────────┐   │
│  │PostgreSQL│ │ Redis │ │ MinIO │ │ChromaDB │ │Together AI │   │
│  └──────────┘ └───────┘ └───────┘ └─────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- Together AI API key

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd applybots

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# - TOGETHER_API_KEY (required)
# - STRIPE_SECRET_KEY (for payments)
# - JWT_SECRET_KEY (generate a secure key)
```

### 2. Start Development Environment

```bash
# Start all services with Docker Compose
make dev

# Or start services individually:
make dev-up          # Start infrastructure services
make backend         # Run backend API (in separate terminal)
make frontend        # Run frontend (in separate terminal)
make worker          # Run Celery worker (in separate terminal)
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8080/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

### 4. Run Database Migrations

```bash
make migrate
```

## 📁 Project Structure

```
applybots/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI endpoints
│   │   ├── agents/        # AutoGen agent configurations
│   │   ├── core/          # Domain models, ports, services
│   │   ├── infra/         # Database, storage, external services
│   │   ├── schemas/       # Pydantic request/response models
│   │   └── workers/       # Celery background tasks
│   ├── migrations/        # Alembic database migrations
│   └── tests/             # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities and API client
│   │   └── providers/     # React context providers
│   └── __tests__/         # Frontend tests
├── docker/                # Docker Compose configuration
└── docs/                  # Design documents
```

## 🧪 Running Tests

```bash
# Run all backend tests
make test

# Run with coverage
make test-cov

# Run frontend tests
make test-frontend

# Run E2E tests
make test-e2e
```

## 🔒 Security & Compliance

### Non-Negotiable Guardrails

1. **No CAPTCHA Bypass** - Automation aborts and flags for manual intervention
2. **No ToS-Violating Automation** - Only safe platforms (Greenhouse, Lever)
3. **Truth-Lock Enforcement** - All generated content verified against resume
4. **Audit Everything** - Complete logs and screenshots for every action
5. **Secrets via Environment** - No hardcoded credentials

### Data Handling

- GDPR-aligned data retention
- User data export/delete capabilities
- Encrypted storage for sensitive information
- No PII in logs

## 🔧 Available Make Commands

```bash
make help           # Show all available commands
make dev            # Start full development environment
make backend        # Run backend locally
make frontend       # Run frontend locally
make worker         # Run Celery worker
make migrate        # Run database migrations
make test           # Run all tests
make lint           # Run linters
make format         # Format code
make clean          # Clean generated files
```

## 📊 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - Async ORM with type hints
- **AutoGen** - Multi-agent AI orchestration
- **Celery** - Distributed task queue
- **Playwright** - Browser automation

### Frontend
- **Next.js 14** - React framework with App Router
- **TanStack Query** - Server state management
- **Tailwind CSS** - Utility-first styling
- **Zod** - Runtime type validation

### Infrastructure
- **PostgreSQL** - Primary database
- **Redis** - Cache and message broker
- **MinIO** - S3-compatible object storage
- **ChromaDB** - Vector database for embeddings

### AI/ML
- **Together AI** - LLM provider (DeepSeek, Llama 4, Qwen3)
- **AutoGen** - Agent orchestration framework

## 📝 Environment Variables

See `.env.example` for all required environment variables.

**Required for basic operation:**
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `TOGETHER_API_KEY` - Together AI API key

**Required for payments:**
- `STRIPE_SECRET_KEY` - Stripe API key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret

## 🤝 Contributing

1. Follow the coding standards in `.cursor/rules/`
2. Write tests for new features
3. Run `make lint` and `make format` before committing
4. Update documentation as needed

## 📄 License

[MIT License](LICENSE)

---

Built with ❤️ for job seekers everywhere.
