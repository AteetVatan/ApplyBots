# ApplyBots - Setup, Installation & Debugging Guide

This guide provides detailed instructions for setting up, installing, and debugging both the backend (Python/FastAPI) and frontend (Next.js) components of ApplyBots.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [OAuth Setup](#oauth-setup-optional)
6. [Environment Configuration](#environment-configuration)
7. [Running the Application](#running-the-application)
8. [Debugging](#debugging)
9. [Common Issues & Solutions](#common-issues--solutions)
10. [Testing](#testing)
11. [Code Quality](#code-quality)
12. [API Endpoints Reference](#api-endpoints-reference)
13. [Features Overview](#features-overview)
14. [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| Docker | Latest | Container services |
| Docker Compose | v2+ | Service orchestration |
| Git | Latest | Version control |

### Recommended Tools

- **VS Code** or **Cursor** - IDE with Python/TypeScript extensions
- **Postman** or **Bruno** - API testing
- **DBeaver** - Database management
- **Redis Insight** - Redis debugging

---

## Quick Start with Docker

The fastest way to get everything running:

```bash
# 1. Clone the repository
git clone <repository-url>
cd applybots

# 2. Copy environment template
cp env.example .env

# 3. Edit .env with your API keys (at minimum, set JWT_SECRET_KEY)
# Generate a secure key:
#   Linux/macOS: openssl rand -hex 32
#   Windows PowerShell: -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Minimum 0 -Maximum 16) })
#   Python: python -c "import secrets; print(secrets.token_hex(32))"

# 4. Start all services
make dev

# 5. Run database migrations (REQUIRED before using the app)
make migrate

# 6. (Optional) Seed sample jobs for testing
python scripts/seed_jobs.py
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Documentation: http://localhost:8080/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

---

## Backend Setup

### Option A: Docker (Recommended)

```bash
# Start infrastructure services
make dev-up

# View logs
make dev-logs
```

### Option B: Local Development

#### 1. Create Virtual Environment

```bash
cd backend

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt

# Install Playwright browsers (for automation)
playwright install chromium
playwright install-deps
```

#### 2b. Install Tesseract OCR (Optional but Recommended)

Tesseract OCR enables text extraction from scanned/image-based PDF resumes. Without it, only text-based PDFs can be processed.

**Windows:**
```powershell
# Option 1: Using Chocolatey (recommended)
choco install tesseract

# Option 2: Download installer from GitHub
# https://github.com/UB-Mannheim/tesseract/wiki
# After installing, add to PATH:
# C:\Program Files\Tesseract-OCR

# Verify installation
tesseract --version
```

**macOS:**
```bash
# Using Homebrew
brew install tesseract

# Verify installation
tesseract --version
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Verify installation
tesseract --version
```

> **Note:** When using Docker, Tesseract is automatically installed in the container. This step is only needed for local development.

#### 2c. Install Poppler (Required for PDF Image Extraction)

Poppler is required by `pdf2image` to convert PDF pages to images for OCR and AI Vision extraction. Without it, the OCR and Vision AI fallbacks won't work.

**Windows:**
```powershell
# Option 1: Using Chocolatey (recommended)
choco install poppler
```

**Option 2: Manual Installation (Windows)**

1. **Download** from: https://github.com/osser/poppler-windows/releases
2. **Extract** to: `C:\Program Files\poppler`
3. **Add to system PATH:**
   - Press `Win + R` → type `sysdm.cpl` → Enter
   - Click **Advanced** tab → **Environment Variables**
   - Under **System variables**, find and select **Path** → **Edit**
   - Click **New** → add `C:\Program Files\poppler\Library\bin`
   - Click **OK** on all dialogs
4. **Restart your terminal/IDE** (important!)

```powershell
# Verify installation (after restart)
pdfinfo -v
# or
pdftoppm -v
```

**macOS:**
```bash
# Using Homebrew
brew install poppler

# Verify installation
pdfinfo -v
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils

# Verify installation
pdfinfo -v
```

> **Note:** After installing Poppler on Windows, you must restart your terminal/IDE for the PATH changes to take effect.

#### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

**Required Environment Variables:**

```env
# Database (use Docker PostgreSQL or local)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ApplyBots

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (64 hex characters = 32 bytes)
# Generate with:
#   Linux/macOS: openssl rand -hex 32
#   Windows PowerShell: -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Minimum 0 -Maximum 16) })
#   Python: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your-secure-random-string

# Together AI (get from https://api.together.xyz/)
TOGETHER_API_KEY=your-api-key
```

**Optional Environment Variables (for full features):**

```env
# OAuth (for social login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:3000/api/auth/callback/github

# Email notifications
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@applybots.com

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

#### 4. Database Setup

```bash
# Ensure PostgreSQL is running (via Docker or local)
# Single-line version (works in both bash and PowerShell):
docker run -d --name ApplyBots-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ApplyBots -p 5432:5432 postgres:16-alpine

# Multi-line versions:
# Bash/Linux/macOS:
docker run -d --name ApplyBots-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ApplyBots \
  -p 5432:5432 postgres:16-alpine

# PowerShell (Windows):
docker run -d --name ApplyBots-postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=ApplyBots `
  -p 5432:5432 postgres:16-alpine

# Run migrations (REQUIRED before seeding)
cd backend

# Apply migrations to create database tables
alembic upgrade head

# Create initial migration (only needed once, if migrations/versions is empty)
alembic revision --autogenerate -m "Initial migration"

cd ..

# (Optional) Seed sample jobs (only after migrations are complete)
python ../scripts/seed_jobs.py
```

#### 5. Start Backend Server

```bash
# Development with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Or use make command from project root
cd ..
make backend
```

#### 6. Start Redis (Required for Celery)

Celery requires Redis as a message broker. Start Redis before starting the Celery worker:

**Option A: Standalone Redis Container (Recommended for Local Development)**

```bash
# Start Redis container
docker run -d --name ApplyBots-redis -p 6379:6379 redis:7-alpine

# Verify Redis is running
docker ps | grep redis
# Or on Windows PowerShell:
docker ps | Select-String redis

# Test Redis connection
docker exec ApplyBots-redis redis-cli ping
# Should return: PONG
```

**Option B: Docker Compose (All Services)**

```bash
# Start all services including Redis
make dev-up
# or
docker compose -f docker/docker-compose.yml up -d
```

**Managing Redis Container:**

```bash
# Start Redis (if stopped)
docker start ApplyBots-redis

# Stop Redis
docker stop ApplyBots-redis

# Remove Redis container (if needed)
docker rm ApplyBots-redis

# View Redis logs
docker logs ApplyBots-redis
```

**Note:** The container name `ApplyBots-redis` is used consistently across all documentation. If using Docker Compose, the container is automatically named `ApplyBots-redis`.

#### 7. Start MinIO (Required for File Uploads)

MinIO provides S3-compatible object storage for resume uploads and other files.

**Option A: Standalone MinIO Container (Recommended for Local Development)**

```bash
# Start MinIO container
docker run -d --name ApplyBots-minio \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -p 9000:9000 \
  -p 9001:9001 \
  minio/minio:latest server /data --console-address ":9001"

# PowerShell (Windows):
docker run -d --name ApplyBots-minio `
  -e MINIO_ROOT_USER=minioadmin `
  -e MINIO_ROOT_PASSWORD=minioadmin `
  -p 9000:9000 `
  -p 9001:9001 `
  minio/minio:latest server /data --console-address ":9001"

# Single-line version (works in both bash and PowerShell):
docker run -d --name ApplyBots-minio -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin -p 9000:9000 -p 9001:9001 minio/minio:latest server /data --console-address ":9001"
```

**Create the Storage Bucket (REQUIRED):**

```bash
# Create the bucket using MinIO client (mc)
docker exec ApplyBots-minio /bin/sh -c "mc alias set local http://localhost:9000 minioadmin minioadmin && mc mb local/applybots --ignore-existing"

# Should output: Bucket created successfully `local/applybots`.
```

> **Important:** S3 bucket names MUST be lowercase. The bucket name is `applybots` (not `ApplyBots`).

**Option B: Docker Compose (All Services)**

```bash
# Start all services including MinIO
make dev-up
# or
docker compose -f docker/docker-compose.yml up -d minio

# Then create the bucket
docker exec ApplyBots-minio /bin/sh -c "mc alias set local http://localhost:9000 minioadmin minioadmin && mc mb local/applybots --ignore-existing"
```

**Managing MinIO Container:**

```bash
# Start MinIO (if stopped)
docker start ApplyBots-minio

# Stop MinIO
docker stop ApplyBots-minio

# Remove MinIO container (if needed)
docker rm ApplyBots-minio

# View MinIO logs
docker logs ApplyBots-minio

# Access MinIO Console (Web UI)
# URL: http://localhost:9001
# Username: minioadmin
# Password: minioadmin
```

**Verify MinIO is Running:**

```bash
# Check container is running
docker ps | grep minio
# Or on Windows PowerShell:
docker ps | Select-String minio

# Test API endpoint
curl http://localhost:9000/minio/health/live
# Should return: healthy
```

#### 8. Start Celery Worker (Optional)

**Important for Windows Users:** Celery is automatically configured to use the `solo` pool on Windows to avoid multiprocessing issues. This is handled automatically by the configuration.

In a separate terminal:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info

# For scheduled tasks (beat scheduler)
celery -A app.workers.celery_app beat --loglevel=info
```

**Windows PowerShell:**
```powershell
cd backend
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
celery -A app.workers.celery_app beat --loglevel=info
```

**Note:** The `--pool=solo` flag is optional on Windows as it's automatically configured, but explicitly setting it ensures compatibility.

### Verify Services are Running

```bash
# Backend API health check
curl http://localhost:8080/health
# Should return: {"status":"healthy","version":"0.1.0"}

# MinIO health check
curl -I http://localhost:9000/minio/health/live
# Should return: HTTP/1.1 200 OK (empty body indicates healthy)

# Redis health check
docker exec ApplyBots-redis redis-cli ping
# Should return: PONG

# PostgreSQL health check
docker exec ApplyBots-postgres pg_isready -U postgres
# Should return: accepting connections
```

### Service Ports Summary

| Service | Port | Console/UI | Purpose |
|---------|------|------------|---------|
| Backend API | 8080 | http://localhost:8080/docs | FastAPI server |
| Frontend | 3000 | http://localhost:3000 | Next.js app |
| PostgreSQL | 5432 | - | Primary database |
| Redis | 6379 | - | Cache, queue broker |
| MinIO API | 9000 | - | Object storage API |
| MinIO Console | 9001 | http://localhost:9001 | Storage management UI |
| ChromaDB | 8000 | - | Vector database |
| Prometheus | 9090 | http://localhost:9090 | Metrics (optional) |
| Grafana | 3001 | http://localhost:3001 | Monitoring (optional) |

---

## Frontend Setup

> **Note:** The frontend uses **Next.js 16+** with the App Router, Server Components by default, and TypeScript strict mode.

### Option A: Docker (Recommended)

Frontend starts automatically with `make dev`.

### Option B: Local Development

#### 1. Install Node.js Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment

Create `.env.local` in the `frontend` directory:

```env
# =============================================================================
# Frontend Environment Configuration
# =============================================================================

# Backend API URL - the frontend proxies API requests to this URL
NEXT_PUBLIC_API_URL=http://localhost:8080
```

> **Architecture Note:** The frontend includes an API proxy at `src/app/api/v1/[...path]/route.ts` that forwards all `/api/v1/*` requests to the backend. This handles:
> - Proper Authorization header forwarding
> - CORS compliance
> - OAuth callback routing

#### 3. Start Development Server

```bash
npm run dev

# Or use make command from project root
cd ..
make frontend
```

#### 4. Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | Run TypeScript type checking |
| `npm run test` | Run Vitest tests |
| `npm run test:ui` | Run Vitest with UI |
| `npm run test:e2e` | Run Playwright E2E tests |

### Verify Frontend is Running

Open http://localhost:3000 in your browser.

---

## OAuth Setup (Optional)

To enable Google and GitHub login:

> **Architecture Note:** The OAuth flow uses the frontend as the callback endpoint. The frontend's API proxy (`/api/v1/[...path]`) forwards OAuth callbacks to the backend for token exchange. This ensures proper cookie handling and CORS compliance.

### Google OAuth

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth client ID**
5. Select **Web application**
6. Add authorized redirect URI: `http://localhost:3000/api/auth/callback/google`
7. Copy the Client ID and Client Secret to your `.env` file:
   ```env
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google
   ```

### GitHub OAuth

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the details:
   - **Application name**: ApplyBots (Local)
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Copy the Client ID and generate a Client Secret
5. Add both to your `.env` file:
   ```env
   GITHUB_CLIENT_ID=<your-client-id>
   GITHUB_CLIENT_SECRET=<your-client-secret>
   GITHUB_REDIRECT_URI=http://localhost:3000/api/auth/callback/github
   ```

### OAuth Flow Diagram

```
User clicks "Login with Google/GitHub"
         │
         ▼
Frontend redirects to provider
         │
         ▼
User authenticates with provider
         │
         ▼
Provider redirects to frontend callback URL
(e.g., http://localhost:3000/api/auth/callback/google)
         │
         ▼
Frontend API proxy forwards to backend
         │
         ▼
Backend exchanges code for tokens & creates session
         │
         ▼
User is logged in
```

---

## Environment Configuration

### Complete `.env` Template

```env
# =============================================================================
# Application
# =============================================================================
APP_NAME=ApplyBots
APP_ENV=development
DEBUG=true
APP_BASE_URL=http://localhost:8080

# =============================================================================
# Database
# =============================================================================
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ApplyBots

# =============================================================================
# Redis
# =============================================================================
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# Authentication (JWT)
# =============================================================================
# Generate JWT secret (64 hex characters = 32 bytes):
#   Linux/macOS: openssl rand -hex 32
#   Windows PowerShell: -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Minimum 0 -Maximum 16) })
#   Python: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=<generate-secure-64-hex-character-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# OAuth (Optional - for Google/GitHub login)
# =============================================================================
# Google OAuth: https://console.developers.google.com/
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google

# GitHub OAuth: https://github.com/settings/developers
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
GITHUB_REDIRECT_URI=http://localhost:3000/api/auth/callback/github

# =============================================================================
# Together AI
# =============================================================================
TOGETHER_API_KEY=<your-api-key>
TOGETHER_API_BASE=https://api.together.xyz/v1

# =============================================================================
# Stripe (Optional for MVP)
# =============================================================================
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_PREMIUM=price_xxx
STRIPE_PRICE_ID_ELITE=price_xxx

# =============================================================================
# S3/MinIO (File Storage)
# =============================================================================
# Note: S3 bucket names MUST be lowercase (AWS/MinIO requirement)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=applybots
S3_REGION=us-east-1

# =============================================================================
# ChromaDB (Vector Database)
# =============================================================================
CHROMA_HOST=localhost
CHROMA_PORT=8000

# =============================================================================
# SendGrid (Email Notifications)
# =============================================================================
# Get API key from https://sendgrid.com/
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=noreply@applybots.com

# =============================================================================
# Rate Limiting
# =============================================================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# =============================================================================
# Plan Limits (Daily application limits per subscription tier)
# =============================================================================
DAILY_APPLY_LIMIT_FREE=5
DAILY_APPLY_LIMIT_PREMIUM=20
DAILY_APPLY_LIMIT_ELITE=50

# =============================================================================
# Job Aggregator APIs (Optional - for job ingestion)
# =============================================================================
# Adzuna - Get keys from: https://developer.adzuna.com/
ADZUNA_APP_ID=<your-adzuna-app-id>
ADZUNA_API_KEY=<your-adzuna-api-key>

# Jooble - Get key from: https://jooble.org/api/about
JOOBLE_API_KEY=<your-jooble-api-key>

# The Muse - Get key from: https://www.themuse.com/developers
THEMUSE_API_KEY=<your-themuse-api-key>

# =============================================================================
# Company Intelligence APIs (Optional)
# =============================================================================
# NewsAPI - Get key from: https://newsapi.org/
NEWSAPI_KEY=<your-newsapi-key>

# =============================================================================
# Feature Flags (Enable/disable features)
# =============================================================================
FEATURE_COMPANY_INTEL=true
FEATURE_GAMIFICATION=true
FEATURE_WELLNESS=true
FEATURE_ADVANCED_ANALYTICS=true

# =============================================================================
# Alert Settings
# =============================================================================
ALERT_DREAM_JOB_DEFAULT_THRESHOLD=90
```

---

## Running the Application

### Full Stack (Docker)

```bash
# Start everything
make dev

# Stop everything
make dev-down

# View logs
make dev-logs

# Rebuild after code changes
make dev-rebuild
```

### Individual Services (Local)

| Service | Command | Port |
|---------|---------|------|
| Backend API | `make backend` | 8080 |
| Frontend | `make frontend` | 3000 |
| Celery Worker | `make worker` | - |
| Celery Worker (Windows) | `make worker-windows` | - |
| Celery Beat | `make worker-beat` | - |
| MinIO | `docker start ApplyBots-minio` | 9000, 9001 |
| PostgreSQL | `docker start ApplyBots-postgres` | 5432 |
| Redis | `docker start ApplyBots-redis` | 6379 |

### All Available Makefile Commands

Run `make help` to see all available commands. Key commands:

**Development:**
| Command | Description |
|---------|-------------|
| `make dev` | Start full development environment (Docker) |
| `make dev-up` | Start Docker services |
| `make dev-down` | Stop Docker services |
| `make dev-logs` | View Docker logs |
| `make dev-rebuild` | Rebuild and restart services |

**Individual Services:**
| Command | Description |
|---------|-------------|
| `make backend` | Run backend locally |
| `make frontend` | Run frontend locally |
| `make worker` | Run Celery worker (auto-detects Windows) |
| `make worker-windows` | Run Celery worker with explicit solo pool |
| `make worker-beat` | Run Celery beat scheduler |

**Database:**
| Command | Description |
|---------|-------------|
| `make migrate` | Run database migrations |
| `make migrate-new MSG="desc"` | Create new migration |
| `make migrate-down` | Rollback last migration |
| `make db-shell` | Open database shell |
| `make seed-jobs` | Seed database with sample jobs |

**Testing:**
| Command | Description |
|---------|-------------|
| `make test` | Run all backend tests |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make test-cov` | Run tests with coverage |
| `make test-frontend` | Run frontend tests |
| `make test-e2e` | Run E2E tests (Playwright) |

**Code Quality:**
| Command | Description |
|---------|-------------|
| `make lint` | Run linters (backend + frontend) |
| `make format` | Format backend code |
| `make typecheck` | Run type checking |

**Dependencies:**
| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make install-backend` | Install backend dependencies only |
| `make install-frontend` | Install frontend dependencies only |

**Utilities:**
| Command | Description |
|---------|-------------|
| `make clean` | Clean generated files |
| `make shell` | Open Python shell with app context |
| `make build` | Build production images |

---

## Debugging

### Backend Debugging

#### 1. VS Code / Cursor Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8080"
      ],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      },
      "jinja": true
    },
    {
      "name": "Pytest Debug",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "tests/"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

#### 2. Logging

Enable debug logging in `.env`:

```env
DEBUG=true
```

View structured logs:

```bash
# Backend logs show structured JSON in production
# Console format in development (DEBUG=true)
```

#### 3. Interactive Debugging

```python
# Add breakpoint anywhere in code
import pdb; pdb.set_trace()

# Or use VS Code/Cursor debugger with breakpoints
```

#### 4. Database Debugging

```bash
# Connect to PostgreSQL
make db-shell

# Or use psql directly
docker exec -it ApplyBots-postgres psql -U postgres -d ApplyBots

# Useful queries:
\dt                          # List tables
SELECT * FROM users LIMIT 5; # Check users
SELECT * FROM jobs LIMIT 5;  # Check jobs
```

#### 5. API Testing

```bash
# Interactive API docs
open http://localhost:8080/docs

# Example curl requests:

# Health check
curl http://localhost:8080/health

# Signup
# Single-line (works in both bash and PowerShell):
curl -X POST http://localhost:8080/api/v1/auth/signup -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Multi-line versions:
# Bash/Linux/macOS:
curl -X POST http://localhost:8080/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# PowerShell (Windows):
curl -X POST http://localhost:8080/api/v1/auth/signup `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\"}'

# Login
# Single-line (works in both bash and PowerShell):
curl -X POST http://localhost:8080/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Multi-line versions:
# Bash/Linux/macOS:
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# PowerShell (Windows):
curl -X POST http://localhost:8080/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\"}'
```

### Frontend Debugging

#### 1. Browser DevTools

- **React DevTools** - Component inspection
- **Network tab** - API request debugging
- **Console** - JavaScript errors

#### 2. VS Code / Cursor Configuration

Create `.vscode/launch.json` (add to existing):

```json
{
  "configurations": [
    {
      "name": "Next.js Debug",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "cwd": "${workspaceFolder}/frontend",
      "console": "integratedTerminal"
    }
  ]
}
```

#### 3. React Query Devtools

TanStack Query devtools are available in development. Open them with the floating button in the bottom-right corner.

#### 4. Logging

```typescript
// Add console logs for debugging
console.log('Debug value:', someValue);

// Use React Query devtools to inspect cache
```

### Celery Worker Debugging

```bash
# Run worker with verbose logging
celery -A app.workers.celery_app worker --loglevel=debug

# Check Redis queue (using ApplyBots-redis container)
docker exec ApplyBots-redis redis-cli LRANGE celery 0 -1

# Monitor tasks
celery -A app.workers.celery_app events

# Check Redis connection
docker exec ApplyBots-redis redis-cli ping
# Should return: PONG

# View Redis info
docker exec ApplyBots-redis redis-cli INFO
```

---

## Common Issues & Solutions

### Backend Issues

#### 1. Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Start if needed
docker start ApplyBots-postgres

# Verify connection
psql -h localhost -U postgres -d ApplyBots
```

#### 2. Module Not Found

```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Set PYTHONPATH
export PYTHONPATH=$PWD  # or set in .env
```

#### 3. Redis Connection Error

```
redis.exceptions.ConnectionError: Error connecting to localhost:6379
```

**Solution:**
```bash
# Start Redis
docker run -d --name ApplyBots-redis -p 6379:6379 redis:7-alpine

# Or use Docker Compose
make dev-up
```

#### 4. Celery Worker Errors on Windows

```
PermissionError: [WinError 5] Access is denied
OSError: [WinError 6] The handle is invalid
```

**Solution:**

The Celery configuration automatically uses the `solo` pool on Windows, but if you still encounter errors:

1. **Ensure Redis is running:**
   ```powershell
   # Check if Redis container is running
   docker ps | Select-String redis
   
   # Start Redis if needed
   docker start ApplyBots-redis
   ```

2. **Explicitly use solo pool:**
   ```powershell
   cd backend
   celery -A app.workers.celery_app worker --loglevel=info --pool=solo
   ```

3. **Verify Redis connection:**
   ```powershell
   # Test Redis connection
   docker exec -it ApplyBots-redis redis-cli ping
   # Should return: PONG
   ```

**Note:** The `solo` pool runs tasks in the same process (single-threaded), which is required on Windows due to multiprocessing limitations. This is automatically configured, but you can explicitly set it with `--pool=solo`.

#### 5. Alembic Migration Error

```
alembic.util.exc.CommandError: Can't locate revision
```

**Solution:**
```bash
# Reset migrations (development only!)
rm -rf migrations/versions/*
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

#### 6. MinIO Connection Error (File Upload Fails)

```
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "http://localhost:9000/..."
```

**Solution:**

1. **Start MinIO container:**
   ```bash
   # Check if MinIO is running
   docker ps | grep minio
   
   # Start MinIO if not running
   docker start ApplyBots-minio
   
   # Or start fresh
   docker run -d --name ApplyBots-minio -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin -p 9000:9000 -p 9001:9001 minio/minio:latest server /data --console-address ":9001"
   ```

2. **Create the bucket (if missing):**
   ```bash
   docker exec ApplyBots-minio /bin/sh -c "mc alias set local http://localhost:9000 minioadmin minioadmin && mc mb local/applybots --ignore-existing"
   ```

3. **Verify environment variables:**
   ```env
   S3_ENDPOINT=http://localhost:9000
   S3_ACCESS_KEY=minioadmin
   S3_SECRET_KEY=minioadmin
   S3_BUCKET=applybots  # MUST be lowercase!
   ```

#### 7. MinIO Bucket Name Error

```
mc: <ERROR> Unable to make bucket `local/ApplyBots`. Bucket name contains invalid characters
```

**Solution:**

S3/MinIO bucket names must be **lowercase**. Use `applybots` instead of `ApplyBots`:

```bash
# Correct
docker exec ApplyBots-minio /bin/sh -c "mc mb local/applybots --ignore-existing"

# Wrong (will fail)
docker exec ApplyBots-minio /bin/sh -c "mc mb local/ApplyBots --ignore-existing"
```

Update your `.env` file:
```env
S3_BUCKET=applybots  # lowercase only!
```

#### 8. PDF Resume Extraction Failed (Scanned PDF)

```
PDF appears to be scanned/image-based but OCR is unavailable.
```

**Cause:** The uploaded PDF is a scanned document (images instead of text) and Tesseract OCR is not installed.

**Solution:**

1. **For Docker users:** Rebuild the backend container (Tesseract is now included):
   ```bash
   make dev-rebuild
   # or
   docker compose -f docker/docker-compose.yml build backend worker
   docker compose -f docker/docker-compose.yml up -d
   ```

2. **For local development:** Install Tesseract OCR:
   ```bash
   # Windows (Chocolatey)
   choco install tesseract
   
   # macOS
   brew install tesseract
   
   # Linux
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   ```

3. **Alternative:** Upload a text-based PDF or DOCX file instead.

**Verify Tesseract is working:**
```bash
tesseract --version
# Should output version info like: tesseract 5.x.x
```

#### 9. PDF Extraction: "Unable to get page count. Is poppler installed?"

```
ocr_extraction_failed          error=Unable to get page count. Is poppler installed and in PATH?
vision_ocr_extraction_failed   error=Unable to get page count. Is poppler installed and in PATH?
```

**Cause:** Poppler is not installed. The `pdf2image` library requires Poppler to convert PDFs to images for OCR and AI Vision extraction.

**Solution:**

1. **Install Poppler:**
   ```bash
   # Windows (Chocolatey)
   choco install poppler
   
   # macOS
   brew install poppler
   
   # Linux
   sudo apt-get install poppler-utils
   ```
   
   **Windows Manual Installation:**
   - Download from: https://github.com/osser/poppler-windows/releases
   - Extract to: `C:\Program Files\poppler`
   - Add to PATH: `C:\Program Files\poppler\Library\bin`
     - Press `Win + R` → type `sysdm.cpl` → Enter
     - Click **Advanced** tab → **Environment Variables**
     - Under **System variables**, find **Path** → **Edit**
     - Click **New** → add `C:\Program Files\poppler\Library\bin`
     - Click **OK** on all dialogs

2. **Restart your terminal/IDE** after installation for PATH changes to take effect (important!).

3. **Verify installation:**
   ```bash
   pdfinfo -v
   # or
   pdftoppm -v
   ```

#### 10. PDF Extraction: "No /Root object! - Is this really a PDF?"

```
pypdf_extraction_failed        error='/Root'
pdfplumber_extraction_failed   error=No /Root object! - Is this really a PDF?
pdfminer_extraction_failed     error=No /Root object! - Is this really a PDF?
```

**Cause:** The PDF file is corrupted or malformed. All PDF parsing libraries require a valid PDF structure with a `/Root` object.

**Solutions:**

1. **Re-export the PDF** from the original source:
   - If created in Word: File → Save As → PDF
   - If created in Google Docs: File → Download → PDF Document
   - If created in Canva/other tools: Re-export as PDF

2. **Use a PDF repair tool:**
   - Adobe Acrobat: File → Save As Other → Optimized PDF
   - Online tools: [iLovePDF](https://www.ilovepdf.com/repair-pdf), [PDF2Go](https://www.pdf2go.com/repair-pdf)
   - Ghostscript: `gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress corrupted.pdf`

3. **Create a clean copy via browser:**
   - Open the PDF in Chrome or Edge
   - Press Ctrl+P (or Cmd+P on Mac)
   - Select "Save as PDF" as the destination
   - Save the new PDF and upload it

4. **Try PyMuPDF (AGPL license)** - More tolerant of malformed PDFs:
   ```bash
   pip install pymupdf
   ```
   > **Note:** PyMuPDF uses AGPL-3.0 license which requires open-sourcing derivative works. Only use if you're okay with AGPL or for testing purposes.

5. **Upload as DOCX instead** - If you have the original Word document, upload that instead of PDF.

**Why this happens:**
- PDF was created with non-standard or buggy tools
- File was corrupted during download or transfer
- PDF uses unusual encoding or non-compliant structure
- Some resume builders create non-standard PDFs

### Frontend Issues

#### 1. Module Not Found

```
Module not found: Can't resolve '@/...'
```

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

#### 2. API Connection Error

```
TypeError: Failed to fetch
```

**Solution:**
- Check backend is running at http://localhost:8080
- Check CORS settings in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

#### 3. Hydration Error

```
Hydration failed because the initial UI does not match
```

**Solution:**
- Ensure server and client render the same content
- Check for browser-only code (use `useEffect` or dynamic imports)

### Docker Issues

#### 1. Port Already in Use

```
Error: Bind for 0.0.0.0:5432 failed: port is already allocated
```

**Solution:**
```bash
# Find and stop the conflicting process
# Linux/macOS:
lsof -i :5432
kill -9 <PID>

# Windows PowerShell:
netstat -ano | findstr :5432
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml
```

#### 2. Container Won't Start

```bash
# Check logs
docker logs ApplyBots-backend

# Rebuild
make dev-rebuild
```

#### 3. MinIO Container Issues

```bash
# Check MinIO logs for startup issues
docker logs ApplyBots-minio

# Common fix: Remove and recreate with correct settings
docker rm -f ApplyBots-minio
docker run -d --name ApplyBots-minio \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -p 9000:9000 \
  -p 9001:9001 \
  minio/minio:latest server /data --console-address ":9001"

# Don't forget to recreate the bucket after container recreation
docker exec ApplyBots-minio /bin/sh -c "mc alias set local http://localhost:9000 minioadmin minioadmin && mc mb local/applybots --ignore-existing"
```

---

## Testing

### Run All Tests

```bash
# Backend tests
make test

# With coverage
make test-cov

# Frontend tests
make test-frontend

# E2E tests
make test-e2e
```

### Run Specific Tests

```bash
# Backend - specific file
cd backend
pytest tests/unit/test_matcher.py -v

# Backend - specific test
pytest tests/unit/test_matcher.py::TestMatchService::test_calculate_score_perfect_match -v

# Frontend - specific file
cd frontend
npm run test -- useJobs.test.ts
```

---

## Code Quality

```bash
# Lint backend
make lint

# Format backend
make format

# Type check
make typecheck
```

---

## API Endpoints Reference

All API endpoints are prefixed with `/api/v1`. Interactive documentation is available at http://localhost:8080/docs when `DEBUG=true`.

### Core Endpoints

| Endpoint Group | Path | Description |
|----------------|------|-------------|
| **Auth** | `/auth/*` | Signup, login, logout, token refresh, OAuth |
| **Profile** | `/profile/*` | User profile management |
| **Jobs** | `/jobs/*` | Job listings, search, match scores |
| **Applications** | `/applications/*` | Application tracking, stages (Kanban), notes |
| **Resumes** | `/resumes/*` | Resume upload, parsing, management |
| **Resume Builder** | `/resume-builder/*` | AI-powered resume creation |
| **Campaigns** | `/campaigns/*` | Automated application campaigns |
| **Agents** | `/agents/*` | AI agent interactions |
| **Billing** | `/billing/*` | Usage tracking, subscription management |

### Feature Endpoints

| Endpoint Group | Path | Description |
|----------------|------|-------------|
| **Career Tools** | `/tools/*` | Interview roleplay, negotiation, career advice |
| **Alerts** | `/alerts/*` | Job alerts, dream job notifications |
| **Gamification** | `/gamification/*` | Points, streaks, achievements |
| **Analytics** | `/analytics/*` | Application analytics, insights |
| **Wellness** | `/wellness/*` | Job search wellness tracking |
| **Company Intel** | `/company-intel/*` | Company research, news, insights |

### Health Check

```bash
curl http://localhost:8080/health
# Returns: {"status":"healthy","version":"0.1.0"}
```

---

## Getting Help

1. **Check the logs** - Most issues are visible in logs
2. **API Docs** - http://localhost:8080/docs has interactive testing
3. **Search issues** - Check existing GitHub issues
4. **Ask for help** - Create a new issue with logs and reproduction steps

---

## Features Overview

### Career Tools

ApplyBots includes AI-powered career tools accessible via `/api/v1/tools/*`:

#### Interview Roleplay (`/tools/interview/*`)
Practice mock interviews with AI-generated questions tailored to your target role:
- Start a session with target role, company, and interview type (behavioral, technical, situational, mixed)
- Receive personalized questions based on experience level
- Get real-time feedback on your answers with strengths, improvements, and example answers
- End session to get overall performance summary and recommendations

#### Offer Negotiation (`/tools/negotiation/*`)
Analyze job offers and get negotiation strategies:
- Compare offers against market data
- Identify strengths and concerns in an offer
- Get recommended counter-offer amounts with justification
- Receive ready-to-use negotiation scripts (email, phone)

#### Career Advisor (`/tools/career/*`)
Get personalized career guidance:
- Assess current career position and skills
- Identify transferable skills and market position
- Explore recommended career paths with transition steps
- Get learning roadmap with prioritized resources

### Job Aggregators

ApplyBots can ingest jobs from multiple sources (configure API keys to enable):

| Source | Environment Variables | Notes |
|--------|----------------------|-------|
| Adzuna | `ADZUNA_APP_ID`, `ADZUNA_API_KEY` | Global job board |
| Jooble | `JOOBLE_API_KEY` | Aggregated listings |
| The Muse | `THEMUSE_API_KEY` | Tech/startup focus |
| StackOverflow | (scraper) | Developer jobs |
| WellFound | (scraper) | Startup jobs |

### Feature Flags

Toggle features on/off via environment variables:

| Feature | Variable | Description |
|---------|----------|-------------|
| Company Intel | `FEATURE_COMPANY_INTEL` | Company research & news |
| Gamification | `FEATURE_GAMIFICATION` | Points, streaks, achievements |
| Wellness | `FEATURE_WELLNESS` | Job search wellness tracking |
| Advanced Analytics | `FEATURE_ADVANCED_ANALYTICS` | Detailed application analytics |

---

## Next Steps

After setup is complete:

1. **Create an account** at http://localhost:3000/signup (or use Google/GitHub OAuth)
2. **Upload a resume** in the Resumes section (requires MinIO to be running)
   - You can manage multiple resumes and set a primary one
3. **Complete your profile** in the Profile section
   - Add preferences like target roles, locations, and negative keywords
4. **Browse jobs** to see match scores based on your resume
5. **Try the AI chat** to interact with agents for job searching and applications
6. **Create applications** - AI generates cover letters and answers screening questions
7. **Use Career Tools** - Practice interviews, analyze offers, and plan your career path

### Quick Service Status Check

Before using the application, ensure all services are running:

```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Expected output should show:
# ApplyBots-postgres   Up ...   0.0.0.0:5432->5432/tcp
# ApplyBots-redis      Up ...   0.0.0.0:6379->6379/tcp
# ApplyBots-minio      Up ...   0.0.0.0:9000-9001->9000-9001/tcp
```

Happy coding! 🚀
