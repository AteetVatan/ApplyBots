# Reactive Resume Customizations

This document tracks all customizations made to Reactive Resume code for integration with our backend.

## Customization Log

### API Client Modifications
**Files Modified**: `src/lib/api-client.ts` (or equivalent)
**Changes**:
- Replaced ORPC client with our FastAPI client
- Added adapter functions for data conversion
- Integrated with our authentication (JWT tokens)
- Mapped Reactive Resume operations to our endpoints:
  - Create resume → `POST /api/v1/resume-builder/drafts`
  - Update resume → `PATCH /api/v1/resume-builder/drafts/{id}`
  - Get resume → `GET /api/v1/resume-builder/drafts/{id}`
  - List resumes → `GET /api/v1/resume-builder/drafts`
  - Delete resume → `DELETE /api/v1/resume-builder/drafts/{id}`

### State Management Modifications
**Files Modified**: `src/stores/resume-store.ts` (or equivalent)
**Changes**:
- Modified to load drafts from our backend on mount
- Auto-save to our backend on changes (debounced)
- Use our draft ID system instead of Reactive Resume's ID system
- Maintain compatibility with Reactive Resume's UI components

### Data Conversion
**Integration Point**: `frontend/src/lib/resume-adapter.ts`
**Usage**:
- On fetch: Backend `ResumeContentSchema` → JSON Resume format → Reactive Resume state
- On save: Reactive Resume state → JSON Resume format → Backend `ResumeContentSchema`

## Upstream Update Strategy

When merging upstream updates:
1. Review changes in modified files
2. Prioritize our backend integration
3. Manually resolve conflicts
4. Test thoroughly after each merge
5. Update this document with new customizations
