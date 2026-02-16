---
description: How to run ConflictLens development environment
---
// turbo-all

## Prerequisites
- Node.js 20+
- Python 3.11+
- pnpm 9+
- Docker (for PostgreSQL)

## Steps

1. Install pnpm dependencies from monorepo root
```bash
cd s:\SYNC\programming\MASX-GCT && pnpm install
```

2. Create Python venv and install backend dependencies
```bash
cd s:\SYNC\programming\MASX-GCT\apps\backend && python -m venv .venv && .venv\Scripts\activate && pip install -e ".[dev]"
```

3. Start PostgreSQL via Docker
```bash
cd s:\SYNC\programming\MASX-GCT && docker-compose up -d postgres
```

4. Run database migrations
```bash
cd s:\SYNC\programming\MASX-GCT\apps\backend && .venv\Scripts\activate && python -m alembic upgrade head
```

5. Seed demo data
```bash
cd s:\SYNC\programming\MASX-GCT\apps\backend && .venv\Scripts\activate && python scripts/seed_demo_data.py
```

6. Start backend (runs on port 8000)
```bash
cd s:\SYNC\programming\MASX-GCT\apps\backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000
```

7. Start web frontend in a NEW terminal (runs on port 3000)
```bash
cd s:\SYNC\programming\MASX-GCT\apps\web && pnpm dev
```

## Verify
- Backend API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health check: http://localhost:8000/health
