# Removed Files from Reactive Resume Fork

This document tracks files and directories removed from the Reactive Resume fork to keep only the frontend UI components we need.

## Removed Directories

### Backend/Server Code
- `server/` - Backend server implementation (we use FastAPI)
- `backend/` - Alternative backend directory if present
- `src/server/` - Server-side code
- Any API server implementation files

### Database/ORM
- `prisma/` - Prisma ORM files (we use SQLAlchemy)
- `src/db/` - Database code
- `migrations/` - Database migrations (we have our own)
- Any ORM model files

### Authentication
- `src/auth/` - Authentication implementation (we have our own)
- User management UI components (we have our own)
- Session management code

### API Routes
- `src/api/` - API route handlers (we'll replace with our backend)
- ORPC route definitions (we'll customize these)
- API middleware

### Infrastructure/Deployment
- `docker-compose.yml` - Docker compose config (we have our own)
- `Dockerfile` - Dockerfile if separate from frontend (we have our own)
- `.github/workflows/` - CI/CD workflows (we have our own)
- Deployment configuration files

### Configuration
- Environment configs for their stack
- Database connection configs

## Kept Directories

### Frontend UI Components
- `src/components/` - Resume builder UI components
- `src/templates/` - Resume templates
- Preview/editor components
- Form components

### State Management
- `src/stores/` - Zustand stores (we'll customize these)
- `src/hooks/` - TanStack Query hooks (we'll customize these)

### Styling/Theming
- CSS/Tailwind styles
- Theme configuration
- Component styles

### Resume Data Models
- TypeScript types/interfaces for resume data
- JSON Resume schema definitions

### Utilities
- Resume formatting utilities
- PDF generation utilities (if client-side)
- Validation utilities

## Notes

- All backend functionality will be replaced with calls to our FastAPI backend
- State management will be customized to work with our backend API
- Data conversion will use `frontend/src/lib/resume-adapter.ts`
