# Reactive Resume Migration Plan

## Overview

**Project**: Migrate Frontend to Reactive Resume  
**Goal**: Replace the custom frontend resume builder with Reactive Resume while keeping the backend intact. Resumes will continue to be stored as JSON in the database. Create adapter layer for data conversion and integrate with existing ATS scoring service.

**Status**: Foundation Complete - Awaiting Reactive Resume Fork Integration

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │     Reactive Resume (Forked & Integrated)       │   │
│  │  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ Zustand Store│  │  UI Components│            │   │
│  │  └──────┬───────┘  └──────┬───────┘            │   │
│  └─────────┼──────────────────┼────────────────────┘   │
│            │                  │                         │
│  ┌─────────▼──────────────────▼─────────┐              │
│  │     Resume Adapter Utilities          │              │
│  │  (JSON Resume ↔ ResumeContent)       │              │
│  └─────────┬──────────────────┬────────┘              │
│            │                  │                         │
│  ┌─────────▼──────────────────▼─────────┐              │
│  │     Integration Hooks                │              │
│  │  (Sync, ATS Scoring)                 │              │
│  └─────────┬──────────────────┬────────┘              │
│            │                  │                         │
│  ┌─────────▼──────────────────▼─────────┐              │
│  │     ATS Score Panel                  │              │
│  └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI - Unchanged)              │
├─────────────────────────────────────────────────────────┤
│  /api/v1/resume-builder/drafts (CRUD)                  │
│  /api/v1/resume-builder/ats-score                       │
│  ATSScoringService                                       │
│  PostgreSQL (JSON Storage)                              │
└─────────────────────────────────────────────────────────┘
```

---

## Migration Phases

### Phase 1: Fork & Integrate Reactive Resume

**Status**: Foundation Ready - Manual Steps Pending

#### Task 1.1: Fork Reactive Resume Repository
- **ID**: `fork-reactive-resume`
- **Status**: Pending
- **Type**: Manual
- **Description**: Fork Reactive Resume GitHub repo and study codebase structure
- **Actions**:
  - Fork `https://github.com/amruthpillai/reactive-resume` to organization/account
  - Clone forked repository locally
  - Study codebase structure:
    - Frontend structure (TanStack Start/React 19)
    - API layer (ORPC)
    - State management (Zustand + TanStack Query)
    - Resume data model (JSON Resume format)
- **Deliverables**:
  - Forked repository
  - Codebase analysis notes
  - Architecture understanding document

#### Task 1.2: Remove Unnecessary Code from Fork
- **ID**: `cleanup-fork`
- **Status**: Pending
- **Type**: Manual
- **Dependencies**: `fork-reactive-resume`
- **Description**: Remove unnecessary code from fork (backend, database, auth, deployment configs) keeping only frontend UI components
- **Files/Directories to Remove**:
  - **Backend code**: `server/`, `backend/`, API server implementation, database migrations, ORPC server files
  - **Infrastructure**: `docker-compose.yml`, `Dockerfile`, `.github/workflows/`, deployment configs
  - **Database/ORM**: Database schema files, ORM models, migration scripts
  - **Authentication**: Auth implementation, user management UI, session management
  - **API Routes**: API route handlers, ORPC route definitions, API middleware
  - **Configuration**: Environment configs for their stack, database connection configs
- **Files/Directories to Keep**:
  - **Frontend UI Components**: Resume builder UI, templates, preview/editor, forms
  - **State Management**: Zustand stores, TanStack Query hooks
  - **Styling**: CSS/Tailwind styles, theme configuration
  - **Resume Data Models**: TypeScript types/interfaces, JSON Resume schema
  - **Utilities**: Resume formatting, PDF generation (client-side), validation
- **Process**:
  1. Create branch: `cleanup-for-integration`
  2. Systematically remove unnecessary directories
  3. Update imports that reference removed code
  4. Test that frontend components still compile (errors expected)
  5. Document removed files in `REMOVED_FILES.md`
- **Deliverables**:
  - Cleaned fork branch
  - `REMOVED_FILES.md` documentation
  - Updated import paths

#### Task 1.3: Integrate Cleaned Code
- **ID**: `integrate-cleaned-code`
- **Status**: Pending
- **Type**: Development
- **Dependencies**: `cleanup-fork`
- **Description**: Copy cleaned Reactive Resume source code into `frontend/src/reactive-resume/` and install dependencies
- **Steps**:
  1. Copy Reactive Resume's `src/` directory to `frontend/src/reactive-resume/`
  2. Install Reactive Resume dependencies in `frontend/package.json`:
     - TanStack Start
     - TanStack Query
     - Zustand
     - Radix UI components
     - Other dependencies from Reactive Resume's `package.json`
  3. Update import paths to work within Next.js structure
  4. Configure Reactive Resume to work with Next.js App Router
- **Deliverables**:
  - Reactive Resume code in `frontend/src/reactive-resume/`
  - Updated `package.json` with dependencies
  - Working import paths

#### Task 1.4: Create Resume Adapter Utilities
- **ID**: `create-adapter`
- **Status**: ✅ Completed
- **Type**: Development
- **Description**: Create resume-adapter.ts with JSON Resume ↔ ResumeContentSchema conversion functions
- **File**: `frontend/src/lib/resume-adapter.ts`
- **Functions**:
  - `jsonResumeToResumeContent(jsonResume: JSONResume): ResumeContent` - Convert from Reactive Resume format
  - `resumeContentToJsonResume(content: ResumeContent): JSONResume` - Convert to Reactive Resume format
  - `apiSchemaToResumeContent(schema: ResumeContentSchema): ResumeContent` - Convert backend API to frontend
  - `resumeContentToApiSchema(content: ResumeContent): ResumeContentSchema` - Convert frontend to backend API
- **Field Mappings**:
  - `basics.name` → `full_name`
  - `basics.profiles` → `linkedin_url`, `github_url`, `portfolio_url`
  - `work[].name` → `work_experience[].company`
  - `work[].position` → `work_experience[].title`
  - `skills[]` → `skills.technical[]` (categorize if possible)
  - Map all other fields accordingly
- **Deliverables**:
  - ✅ `frontend/src/lib/resume-adapter.ts` (Complete)

---

### Phase 2: Customize Data Synchronization

**Status**: Foundation Ready - Awaiting Reactive Resume Code

#### Task 2.1: Customize Reactive Resume's API Layer
- **ID**: `customize-api-layer`
- **Status**: Pending
- **Type**: Development
- **Dependencies**: `integrate-cleaned-code`, `create-adapter`
- **Description**: Customize Reactive Resume's API client to use our FastAPI backend endpoints with adapter conversion
- **Files to Modify**: Reactive Resume's API client files (typically in `src/lib/api/` or similar)
- **Changes**:
  - Replace Reactive Resume's ORPC API calls with our FastAPI endpoints
  - Map Reactive Resume's resume operations to our draft CRUD endpoints:
    - Create resume → `POST /api/v1/resume-builder/drafts`
    - Update resume → `PATCH /api/v1/resume-builder/drafts/{id}`
    - Get resume → `GET /api/v1/resume-builder/drafts/{id}`
    - List resumes → `GET /api/v1/resume-builder/drafts`
    - Delete resume → `DELETE /api/v1/resume-builder/drafts/{id}`
  - Use adapter functions to convert between formats on API calls
  - Integrate with our authentication (JWT tokens)
  - Use our existing API utilities from `frontend/src/lib/api.ts`
- **Deliverables**:
  - Customized API client
  - Integration with our backend
  - Authentication integration

#### Task 2.2: Customize Reactive Resume's State Management
- **ID**: `customize-state-management`
- **Status**: Pending
- **Type**: Development
- **Dependencies**: `customize-api-layer`
- **Description**: Modify Reactive Resume's Zustand stores to load/save from our backend with adapter conversion
- **Files**: Reactive Resume's Zustand stores (typically in `src/stores/`)
- **Changes**:
  - Modify Reactive Resume's resume store to:
    - Load drafts from our backend on mount
    - Auto-save to our backend on changes (debounced)
    - Use our draft ID system instead of Reactive Resume's ID system
    - Maintain compatibility with Reactive Resume's UI components
- **Deliverables**:
  - Modified Zustand stores
  - Backend integration
  - Auto-save functionality

---

### Phase 3: Update Builder Page & ATS Integration

**Status**: Foundation Ready - Awaiting Reactive Resume Code

#### Task 3.1: Update Builder Page
- **ID**: `update-builder-page`
- **Status**: Pending
- **Type**: Development
- **Dependencies**: `customize-state-management`
- **Description**: Replace builder page with integrated Reactive Resume component and ATS panel
- **File**: `frontend/src/app/(dashboard)/dashboard/resumes/builder/page.tsx`
- **Changes**:
  - Replace the three-panel layout with:
    - Reactive Resume builder (integrated component, not iframe)
    - ATS Score Panel (side panel, keep existing)
  - Remove EditorPanel and PreviewPanel (handled by Reactive Resume)
  - Import Reactive Resume builder component directly
  - Pass draft ID from URL to Reactive Resume
  - Integrate ATS scoring panel alongside Reactive Resume
  - Remove `useResumeBuilderStore` dependency (Reactive Resume manages its own state)
  - Maintain draft ID in URL (`?draftId=xxx`)
- **Deliverables**:
  - Updated builder page
  - Integrated Reactive Resume component
  - ATS panel integration

#### Task 3.2: Integrate ATS Scoring
- **ID**: `integrate-ats-scoring`
- **Status**: ✅ Completed (Hook Ready)
- **Type**: Development
- **Dependencies**: `create-adapter`, `update-builder-page`
- **Description**: Create useReactiveResumeATSScore hook to fetch data from Reactive Resume and call ATS service
- **File**: `frontend/src/hooks/useReactiveResumeATSScore.ts`
- **Functionality**:
  - Accesses Reactive Resume's Zustand store to get current resume data
  - Converts JSON Resume → `ResumeContentSchema` using adapter
  - Calls existing `useATSScore` hook with converted data
  - Displays results in existing `ATSScorePanel` component
- **Integration**:
  - Access Reactive Resume's resume store (e.g., `useResumeStore()` from Reactive Resume)
  - Reuse `frontend/src/hooks/useATSScore.ts`
  - Reuse `frontend/src/components/resume-builder/ATSScorePanel.tsx`
  - Backend endpoint `/api/v1/resume-builder/ats-score` remains unchanged
- **Deliverables**:
  - ✅ `useReactiveResumeATSScore.ts` hook (Complete)
  - Updated ATS Score Panel (if needed)

---

### Phase 4: Testing & Validation

**Status**: Pending

#### Task 4.1: Test Migration
- **ID**: `test-migration`
- **Status**: Pending
- **Type**: Testing
- **Dependencies**: `update-builder-page`, `integrate-ats-scoring`
- **Description**: Test draft loading, auto-save, ATS scoring, and data conversion with existing drafts
- **Test Cases**:
  1. **Data Conversion Tests**: Test adapter functions with various resume formats
  2. **Draft Loading**: Load existing drafts from database
  3. **Draft Creation**: Create new drafts
  4. **Auto-save**: Verify auto-save triggers correctly and data persists
  5. **ATS Integration**: Verify ATS scoring works with Reactive Resume data
  6. **Edge Cases**: Empty resumes, missing fields, special characters
  7. **Real-time Updates**: Verify ATS panel updates in real-time
- **Deliverables**:
  - Test results
  - Bug reports (if any)
  - Fixes for identified issues

---

### Phase 5: Cleanup & Component Removal

**Status**: Pending

#### Task 5.1: Extract Adapter Logic
- **ID**: `extract-adapter-logic`
- **Status**: ✅ Completed (Already in adapter)
- **Type**: Development
- **Description**: Extract adapter logic from ExportImport.tsx (already done in adapter)
- **Note**: Adapter logic already extracted to `resume-adapter.ts`

#### Task 5.2: Cleanup Old Components
- **ID**: `cleanup-old-components`
- **Status**: Pending
- **Type**: Development
- **Dependencies**: `test-migration`
- **Description**: Extract adapter logic from ExportImport.tsx, then remove all UI components (EditorPanel, PreviewPanel, templates, sections, resume-builder-store) while keeping ATS panel and hooks
- **Files to Keep (Reusable Components)**:
  - ✅ `frontend/src/components/resume-builder/ATSScorePanel.tsx` - **KEEP** (reused for ATS scoring display)
  - `frontend/src/components/resume-builder/ai-drawer/` - **EVALUATE** (may be useful for AI features)
  - ✅ `frontend/src/hooks/useATSScore.ts` - **KEEP** (reused for ATS scoring logic)
  - ✅ `frontend/src/hooks/useResumeDrafts.ts` - **KEEP** (used for draft CRUD operations)
  - ✅ `frontend/src/lib/resume-adapter.ts` - **KEEP** (adapter utilities)
- **Files to Remove (UI Components Replaced by Reactive Resume)**:
  - `frontend/src/components/resume-builder/EditorPanel.tsx` - Replaced by Reactive Resume editor
  - `frontend/src/components/resume-builder/PreviewPanel.tsx` - Replaced by Reactive Resume preview
  - `frontend/src/components/resume-builder/templates/` - All template components (13 templates)
  - `frontend/src/components/resume-builder/pdf-templates/` - PDF generation handled by Reactive Resume
  - `frontend/src/components/resume-builder/sections/` - All section components
  - `frontend/src/components/resume-builder/TemplateSelector.tsx` - Replaced by Reactive Resume
  - `frontend/src/components/resume-builder/TemplateSettings.tsx` - Replaced by Reactive Resume
  - `frontend/src/components/resume-builder/RichTextEditor.tsx` - Replaced by Reactive Resume
  - `frontend/src/components/resume-builder/ExportImport.tsx` - Remove after extracting adapter logic
  - `frontend/src/stores/resume-builder-store.ts` - **REMOVE** (Reactive Resume manages its own state)
  - `frontend/src/hooks/usePDFExport.ts` - **REMOVE** (PDF export handled by Reactive Resume)
- **Cleanup Steps**:
  1. Verify adapter logic is extracted (already done)
  2. Update imports in files that use removed components
  3. Remove unused imports and dependencies
  4. Test that ATS panel still works with Reactive Resume data
  5. Remove listed files after verification
  6. Update `frontend/src/components/resume-builder/index.ts` to export only kept components
- **Deliverables**:
  - Removed old components
  - Updated imports
  - Clean codebase

---

## Task Dependency Graph

```
fork-reactive-resume
    ↓
cleanup-fork
    ↓
integrate-cleaned-code ──┐
    ↓                    │
create-adapter ──────────┼──→ customize-api-layer
    ↓                    │         ↓
    └────────────────────┼──→ customize-state-management
                         │         ↓
                         │    update-builder-page
                         │         ↓
                         └──→ integrate-ats-scoring
                                  ↓
                              test-migration
                                  ↓
                              cleanup-old-components
```

---

## Current Status Summary

### ✅ Completed
- **Phase 1.4**: Resume Adapter Utilities (`resume-adapter.ts`)
- **Phase 3.2**: ATS Scoring Hook (`useReactiveResumeATSScore.ts`)
- **Phase 5.1**: Adapter Logic Extraction

### ⏳ Pending (Manual Steps)
- **Phase 1.1**: Fork Reactive Resume Repository
- **Phase 1.2**: Remove Unnecessary Code from Fork
- **Phase 1.3**: Integrate Cleaned Code

### ⏳ Pending (Development - Awaiting Reactive Resume Code)
- **Phase 2.1**: Customize Reactive Resume's API Layer
- **Phase 2.2**: Customize Reactive Resume's State Management
- **Phase 3.1**: Update Builder Page
- **Phase 4.1**: Test Migration
- **Phase 5.2**: Cleanup Old Components

---

## Data Flow Diagrams

### Loading a Draft
```
User → Builder Page → useReactiveResumeSync → Backend API
  → ResumeContentSchema → Adapter → JSON Resume → Reactive Resume → Display
```

### Auto-saving Changes
```
User Edits → Reactive Resume State → useReactiveResumeSync (debounced)
  → Adapter (JSON Resume → ResumeContentSchema) → Backend API → Save
```

### ATS Scoring
```
User Request → ATS Panel → useReactiveResumeATSScore → Reactive Resume Store
  → JSON Resume → Adapter → ResumeContentSchema → ATS Service → Display Results
```

---

## Testing Strategy

### Unit Tests
- [ ] Adapter conversion functions (both directions)
- [ ] Edge cases (empty resumes, missing fields)
- [ ] Special characters handling

### Integration Tests
- [ ] Draft loading from backend
- [ ] Auto-save functionality
- [ ] ATS scoring integration
- [ ] Data persistence

### E2E Tests
- [ ] Create new draft
- [ ] Edit existing draft
- [ ] Delete draft
- [ ] ATS scoring workflow
- [ ] Real-time updates

---

## Rollback Plan

If issues arise:

1. **Keep old builder code** in a feature branch
2. **Use feature flag** to switch between old/new builder
3. **Backend remains unchanged**, so rollback is frontend-only
4. **All adapter utilities are isolated** and can be reused

---

## Fork Maintenance Strategy

### Upstream Updates
1. **Keep Fork in Sync**: Periodically merge upstream changes from `amruthpillai/reactive-resume:main`
2. **Customization Tracking**: Document all customizations in `CUSTOMIZATIONS.md`
3. **Conflict Resolution**: Prioritize our backend integration, manually resolve conflicts
4. **Version Pinning**: Consider pinning to a specific Reactive Resume version for stability

### Customization Files
- `frontend/src/reactive-resume/README.md` - Fork process
- `frontend/src/reactive-resume/REMOVED_FILES.md` - Removed files log
- `frontend/src/reactive-resume/CUSTOMIZATIONS.md` - Customizations log
- `frontend/src/reactive-resume/INTEGRATION_STATUS.md` - Current status

---

## Environment Configuration

### Environment Variables
Add to `.env`:
- `NEXT_PUBLIC_REACTIVE_RESUME_URL` - URL to Reactive Resume instance (if self-hosted)
- Or use public instance: `https://rxresu.me`

### Routing
- Keep route: `/dashboard/resumes/builder?draftId=xxx`
- Reactive Resume handles its own routing internally
- Backend routes unchanged

---

## Notes

- ✅ Backend API endpoints remain unchanged
- ✅ Database schema unchanged (JSON storage)
- ✅ Existing drafts in database remain compatible (just need conversion on load)
- ✅ ATS scoring service unchanged
- ✅ Job application integration unchanged (uses draft ID from backend)
- ✅ Reactive Resume code is integrated directly, not as a dependency
- ✅ We maintain a fork to customize API integration
- ⚠️ **Important**: After forking, we remove all backend/infrastructure code from Reactive Resume, keeping only frontend UI components. This reduces codebase size and avoids conflicts with our existing stack.

---

## Next Immediate Steps

1. **Fork Reactive Resume** (Manual step)
   - Go to https://github.com/amruthpillai/reactive-resume
   - Fork to your organization/account
   - Clone locally

2. **Clean up fork** (Manual step)
   - Create branch: `cleanup-for-integration`
   - Remove unnecessary code
   - Document in `REMOVED_FILES.md`

3. **Integrate cleaned code**
   - Copy to `frontend/src/reactive-resume/`
   - Install dependencies
   - Update import paths

4. **Customize API layer**
   - Modify API client to use our backend
   - Use adapter functions
   - Integrate authentication

5. **Customize state management**
   - Modify Zustand stores
   - Connect to our backend
   - Implement auto-save

6. **Update builder page**
   - Replace placeholder with actual components
   - Test integration

7. **Test thoroughly**
   - All test cases
   - Edge cases
   - Real-world scenarios

8. **Cleanup**
   - Remove old components
   - Update documentation

---

## Success Criteria

- [ ] Existing drafts load correctly from database
- [ ] New drafts can be created
- [ ] Resume editing works in Reactive Resume
- [ ] Auto-save persists changes to backend
- [ ] ATS scoring works with Reactive Resume data
- [ ] Data conversion is accurate (both directions)
- [ ] All old builder components removed
- [ ] No breaking changes to backend
- [ ] Documentation updated

---

**Last Updated**: Based on current integration status  
**Plan Version**: 1.0  
**Status**: Foundation Complete - Awaiting Reactive Resume Fork Integration
