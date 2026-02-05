# ORPC Necessity Analysis

## Executive Summary

**Recommendation: ORPC can be removed** - It adds unnecessary complexity with minimal benefits for this use case. The reactive-resume app is embedded in an iframe, doesn't need SEO, and already has direct API client usage patterns.

## Current Architecture

```
Component → ORPC Client (TanStack Query) → /api/rpc route → ORPC Router → ORPC Service → API Client → FastAPI Backend
```

**Key Finding:** ORPC services are thin wrappers that just call `getAPIClient()`, which directly hits the FastAPI backend.

## Detailed Findings

### 1. SSR Usage (Server-Side Rendering)

**Finding: Minimal SSR usage**

- **Only 1 route uses SSR:** `$username/$slug.tsx` uses `ensureQueryData` in loader
- **Purpose:** Public resume sharing page (SEO/performance)
- **Reality:** Reactive-resume is embedded in iframe - SEO is irrelevant
- **Alternative:** Could use direct API call in loader if SSR is truly needed

**Files:**
- `reactive-resume/src/routes/$username/$slug.tsx` - Only SSR usage

### 2. Type Safety

**Finding: Type safety is available but not critical**

- ORPC provides type inference from Zod schemas via `RouterInput` and `RouterOutput`
- API client already has TypeScript interfaces (`Resume`, `ResumeData`, etc.)
- Type safety could be maintained with direct API client + TypeScript types

**Current:**
```typescript
// ORPC provides
orpc.resume.getById.queryOptions({ input: { id: string } })
// Type-safe from Zod schema
```

**Alternative:**
```typescript
// Direct API client
useQuery({
  queryKey: ["resume", id],
  queryFn: () => apiClient.getById(id) // Returns Promise<Resume>
})
// Type-safe from API client return type
```

### 3. Request Batching

**Finding: Batching is enabled but value is unclear**

- `BatchLinkPlugin` is enabled in ORPC client
- `BatchHandlerPlugin` is enabled in ORPC server
- **No evidence** that batching provides measurable performance benefits
- Most queries are independent and don't benefit from batching

**Files:**
- `reactive-resume/src/integrations/orpc/client.ts:55` - BatchLinkPlugin enabled
- `reactive-resume/src/routes/api/rpc.$.ts:13` - BatchHandlerPlugin enabled

### 4. Error Handling

**Finding: ORPC error handling is minimal**

- ORPC services convert generic errors to `ORPCError` types
- API client already throws proper errors
- Error handling could be done at component level with direct API calls

**Current Pattern:**
```typescript
// ORPC service
catch (error) {
  if (error instanceof Error && error.message.includes("404")) {
    throw new ORPCError("NOT_FOUND");
  }
  throw error;
}
```

**Alternative:**
```typescript
// Direct API client
try {
  await apiClient.getById(id);
} catch (error) {
  if (error.message.includes("404")) {
    // Handle 404
  }
}
```

### 5. Direct API Client Usage

**Finding: Direct API client is already used in key places**

**Files using `getAPIClient()` directly:**
1. `reactive-resume/src/routes/builder/$resumeId/route.tsx` - Main builder route
2. `reactive-resume/src/components/resume/store/resume.ts` - Resume store (auto-save)
3. `reactive-resume/src/integrations/orpc/services/resume.ts` - All ORPC services (8 calls)

**Pattern:** The builder route (most critical) already bypasses ORPC and uses direct API client with TanStack Query.

### 6. TanStack Query Integration

**Finding: TanStack Query works perfectly with direct API client**

**Current ORPC pattern:**
```typescript
const { data } = useQuery(orpc.resume.getById.queryOptions({ input: { id } }));
```

**Direct API client pattern (already used in builder):**
```typescript
const { data } = useQuery({
  queryKey: ["resume", id],
  queryFn: () => apiClient.getById(id)
});
```

**Verdict:** Direct API client works seamlessly with TanStack Query. No ORPC needed.

### 7. API Client Auth/Error Handling

**Finding: API client already handles auth and errors properly**

**Auth:**
- API client automatically adds JWT token from localStorage
- Token is retrieved via `getAuthToken()` callback
- Works identically whether called through ORPC or directly

**Error Handling:**
- API client throws proper errors with status codes
- Error messages are extracted from API responses
- Components can handle errors directly

**File:** `reactive-resume/src/lib/api-client.ts:127-165`

### 8. Usage Statistics

**ORPC Usage:**
- **24 matches** across 15 files in routes
- **28 queryOptions/mutationOptions** calls across 17 files
- Most common: `orpc.resume.*` operations

**Direct API Client Usage:**
- **12 matches** across 3 files
- **Key files:** builder route, resume store, ORPC services themselves

**Pattern:** ORPC is used more, but the most critical path (builder) already uses direct API client.

## Complexity Analysis

### Files in ORPC Layer

1. **Routers:** 6 files (`router/resume.ts`, `router/ai.ts`, `router/storage.ts`, etc.)
2. **Services:** 6 files (`services/resume.ts`, `services/ai.ts`, etc.)
3. **Client:** 1 file (`client.ts`)
4. **Context:** 1 file (`context.ts`)
5. **API Route:** 1 file (`routes/api/rpc.$.ts`)

**Total:** ~15 files, ~2000+ lines of code

### Dependencies

- `@orpc/client`
- `@orpc/server`
- `@orpc/tanstack-query`
- Additional complexity in build/runtime

## Simplification Options

### Option A: Keep ORPC (Current)
**Pros:**
- SSR support (minimal usage)
- Type safety from schemas
- Request batching (unclear benefit)

**Cons:**
- Extra abstraction layer
- 15+ files, 2000+ lines of code
- Indirection (6 layers deep)
- Inconsistent patterns (builder uses direct API)

### Option B: Remove ORPC, Use API Client + TanStack Query ⭐ RECOMMENDED
**Pros:**
- Simpler architecture (direct calls)
- Consistent patterns (builder already does this)
- Less code to maintain
- Faster development (no ORPC layer to understand)
- Same functionality

**Cons:**
- Lose automatic type inference (but can use API client types)
- Need manual SSR handling (only 1 route needs it)

**Implementation:**
1. Replace `orpc.resume.*.queryOptions()` with direct `useQuery({ queryKey, queryFn: () => apiClient.* })`
2. Replace `orpc.*.mutationOptions()` with direct `useMutation({ mutationFn: () => apiClient.* })`
3. For SSR route (`$username/$slug.tsx`), use direct API call in loader
4. Remove ORPC router, services, client files
5. Remove `/api/rpc` route

**Estimated effort:** 2-3 days to refactor all routes

### Option C: Hybrid Approach
**Pros:**
- Keep ORPC for SSR routes
- Use direct API for dashboard/builder

**Cons:**
- Inconsistent patterns
- Still maintain ORPC layer
- Confusion about when to use which

## Recommendation

**Remove ORPC entirely (Option B)**

**Reasons:**
1. **Embedded in iframe** - SEO/SSR not critical
2. **Builder already uses direct API** - Proves it works
3. **Minimal SSR usage** - Only 1 route, can handle manually
4. **Complexity reduction** - Remove 15+ files, 2000+ lines
5. **Consistency** - Single pattern throughout codebase
6. **Performance** - One less layer, direct calls are faster
7. **Maintainability** - Easier to understand and debug

**Migration Path:**
1. Start with non-critical routes (dashboard, settings)
2. Migrate builder routes (already partially done)
3. Handle SSR route last (only one that needs special handling)
4. Remove ORPC layer once all routes migrated

## Conclusion

ORPC was likely added for SSR and type safety, but:
- SSR is not needed (iframe embedding)
- Type safety can be achieved with API client types
- Direct API client + TanStack Query works perfectly
- Builder already proves the pattern works

**The extra abstraction layer provides minimal value and adds significant complexity.**
