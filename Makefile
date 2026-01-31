# ApplyBots Makefile
# ====================

.PHONY: help dev dev-up dev-down dev-logs backend frontend worker migrate test lint format clean

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)ApplyBots Development Commands$(NC)"
	@echo "================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Development Environment
# =============================================================================

dev: dev-up ## Start full development environment
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8080"
	@echo "API Docs: http://localhost:8080/docs"
	@echo "MinIO Console: http://localhost:9001"

dev-up: ## Start Docker services
	docker compose -f docker/docker-compose.yml up -d

dev-down: ## Stop Docker services
	docker compose -f docker/docker-compose.yml down

dev-logs: ## View Docker logs
	docker compose -f docker/docker-compose.yml logs -f

dev-rebuild: ## Rebuild and restart services
	docker compose -f docker/docker-compose.yml down
	docker compose -f docker/docker-compose.yml build --no-cache
	docker compose -f docker/docker-compose.yml up -d

# =============================================================================
# Individual Services
# =============================================================================

backend: ## Run backend locally (without Docker)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

frontend: ## Run frontend locally (without Docker)
	cd frontend && npm run dev

worker: ## Run Celery worker locally (auto-detects Windows and uses solo pool)
	cd backend && celery -A app.workers.celery_app worker --loglevel=info

worker-beat: ## Run Celery beat scheduler
	cd backend && celery -A app.workers.celery_app beat --loglevel=info

worker-windows: ## Run Celery worker on Windows (explicit solo pool)
	cd backend && celery -A app.workers.celery_app worker --loglevel=info --pool=solo

# =============================================================================
# Database
# =============================================================================

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-new: ## Create new migration (usage: make migrate-new MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	cd backend && alembic downgrade -1

db-shell: ## Open database shell
	docker exec -it ApplyBots-postgres psql -U postgres -d ApplyBots

# =============================================================================
# Testing
# =============================================================================

test: ## Run all tests
	cd backend && pytest tests/ -v

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit/ -v

test-integration: ## Run integration tests only
	cd backend && pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	cd backend && pytest tests/ --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	cd frontend && npm run test

test-e2e: ## Run E2E tests
	cd frontend && npx playwright test

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linters
	@echo "$(BLUE)Running backend linters...$(NC)"
	cd backend && ruff check app/
	cd backend && mypy app/
	@echo "$(BLUE)Running frontend linters...$(NC)"
	cd frontend && npm run lint

format: ## Format code
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && ruff format app/
	cd backend && ruff check app/ --fix
	@echo "$(BLUE)Formatting complete!$(NC)"

typecheck: ## Run type checking
	cd backend && mypy app/
	cd frontend && npm run typecheck

# =============================================================================
# Dependencies
# =============================================================================

install: ## Install all dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)Dependencies installed!$(NC)"

install-backend: ## Install backend dependencies only
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies only
	cd frontend && npm install

# =============================================================================
# Production
# =============================================================================

build: ## Build production images
	docker compose -f docker/docker-compose.yml build

# =============================================================================
# Utilities
# =============================================================================

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov 2>/dev/null || true
	rm -rf frontend/.next 2>/dev/null || true
	rm -rf frontend/node_modules/.cache 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

seed-jobs: ## Seed database with sample jobs
	cd backend && python scripts/seed_jobs.py

shell: ## Open Python shell with app context
	cd backend && python -c "from app.config import get_settings; print('Settings loaded')"
