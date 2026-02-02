# Reactive Resume Integration

This directory will contain the forked and cleaned Reactive Resume codebase.

## Fork Process

1. **Fork the Repository**
   - Go to https://github.com/amruthpillai/reactive-resume
   - Fork to your organization/account
   - Clone the forked repository locally

2. **Study the Codebase**
   - Review the structure (TanStack Start/React 19)
   - Understand the API layer (ORPC)
   - Review state management (Zustand + TanStack Query)
   - Review resume data model (JSON Resume format)

3. **Clean Up the Fork**
   - Create branch: `cleanup-for-integration`
   - Remove backend code (`server/`, `backend/`, API routes)
   - Remove database code (migrations, ORM models)
   - Remove authentication code (we have our own)
   - Remove deployment configs (Docker, CI/CD)
   - Keep only frontend UI components, stores, and utilities

4. **Document Removed Files**
   - Create `REMOVED_FILES.md` listing what was removed and why

5. **Copy to This Directory**
   - Copy cleaned `src/` directory to `frontend/src/reactive-resume/`
   - Install dependencies in `frontend/package.json`

## Integration Points

Once integrated, we'll customize:

- **API Client**: Replace ORPC calls with our FastAPI endpoints
- **State Management**: Modify Zustand stores to use our backend
- **Data Conversion**: Use `frontend/src/lib/resume-adapter.ts` for format conversion

## Customization Files

See `CUSTOMIZATIONS.md` (to be created) for documentation of all modifications made to Reactive Resume code.
