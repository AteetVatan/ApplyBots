# ApplyBots - Setup, Installation & Debugging Guide

This guide provides detailed instructions for setting up, installing, and debugging both the backend (Python/FastAPI) and frontend (Next.js) components of ApplyBots.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Environment Configuration](#environment-configuration)
6. [Running the Application](#running-the-application)
7. [Debugging](#debugging)
8. [Common Issues & Solutions](#common-issues--solutions)

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

# Create initial migration (only needed once, if migrations/versions is empty)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations to create database tables
alembic upgrade head
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
curl http://localhost:9000/minio/health/live
# Should return: healthy

# Redis health check
docker exec ApplyBots-redis redis-cli ping
# Should return: PONG

# PostgreSQL health check
docker exec ApplyBots-postgres pg_isready -U postgres
# Should return: accepting connections
```

### Service Ports Summary

| Service | Port | Console/UI |
|---------|------|------------|
| Backend API | 8080 | http://localhost:8080/docs |
| Frontend | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | - |
| Redis | 6379 | - |
| MinIO API | 9000 | - |
| MinIO Console | 9001 | http://localhost:9001 |
| ChromaDB | 8000 | - |

---

## Frontend Setup

### Option A: Docker (Recommended)

Frontend starts automatically with `make dev`.

### Option B: Local Development

#### 1. Install Node.js Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
```

#### 3. Start Development Server

```bash
npm run dev

# Or use make command from project root
cd ..
make frontend
```

### Verify Frontend is Running

Open http://localhost:3000 in your browser.

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

# =============================================================================
# Database
# =============================================================================
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ApplyBots

# =============================================================================
# Redis
# =============================================================================
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# Authentication
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
# ChromaDB
# =============================================================================
CHROMA_HOST=localhost
CHROMA_PORT=8000
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
| Celery Beat | `make worker-beat` | - |
| MinIO | `docker start ApplyBots-minio` | 9000, 9001 |
| PostgreSQL | `docker start ApplyBots-postgres` | 5432 |
| Redis | `docker start ApplyBots-redis` | 6379 |

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

## Getting Help

1. **Check the logs** - Most issues are visible in logs
2. **API Docs** - http://localhost:8080/docs has interactive testing
3. **Search issues** - Check existing GitHub issues
4. **Ask for help** - Create a new issue with logs and reproduction steps

---

## Next Steps

After setup is complete:

1. **Create an account** at http://localhost:3000/signup
2. **Upload a resume** in the Profile section (requires MinIO to be running)
3. **Browse jobs** to see match scores
4. **Try the AI chat** to interact with agents

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
