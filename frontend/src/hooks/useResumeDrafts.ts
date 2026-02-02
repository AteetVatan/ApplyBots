"use client";

/**
 * TanStack Query hooks for Resume Builder draft management.
 *
 * Standards: react_nextjs.mdc
 * - TanStack Query for server state
 * - Type-safe API calls
 * - Optimistic updates where applicable
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  api,
  type DraftListResponse,
  type ResumeDraft,
  type DraftCreateRequest,
  type DraftUpdateRequest,
} from "@/lib/api";

// Query keys for cache management
export const draftKeys = {
  all: ["resume-drafts"] as const,
  lists: () => [...draftKeys.all, "list"] as const,
  list: (params: { limit?: number; offset?: number }) =>
    [...draftKeys.lists(), params] as const,
  details: () => [...draftKeys.all, "detail"] as const,
  detail: (id: string) => [...draftKeys.details(), id] as const,
};

/**
 * Fetch all user's resume drafts
 */
export function useDrafts(params: { limit?: number; offset?: number } = {}) {
  return useQuery<DraftListResponse>({
    queryKey: draftKeys.list(params),
    queryFn: () => api.getDrafts(params),
  });
}

/**
 * Fetch a single draft by ID
 */
export function useDraft(id: string | null) {
  return useQuery<ResumeDraft>({
    queryKey: draftKeys.detail(id ?? ""),
    queryFn: () => api.getDraft(id!),
    enabled: !!id,
  });
}

/**
 * Create a new draft
 */
export function useCreateDraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DraftCreateRequest) => api.createDraft(data),
    onSuccess: (newDraft) => {
      // Invalidate list queries to refetch
      queryClient.invalidateQueries({ queryKey: draftKeys.lists() });
      // Pre-populate the cache for this draft
      queryClient.setQueryData(draftKeys.detail(newDraft.id), newDraft);
    },
  });
}

/**
 * Update an existing draft (autosave)
 */
export function useUpdateDraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DraftUpdateRequest }) =>
      api.updateDraft(id, data),
    onSuccess: (updatedDraft) => {
      // Update the cache for this specific draft
      queryClient.setQueryData(draftKeys.detail(updatedDraft.id), updatedDraft);
      // Invalidate list queries to reflect updated data
      queryClient.invalidateQueries({ queryKey: draftKeys.lists() });
    },
  });
}

/**
 * Delete a draft
 */
export function useDeleteDraft() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.deleteDraft(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: draftKeys.detail(deletedId) });
      // Invalidate list queries
      queryClient.invalidateQueries({ queryKey: draftKeys.lists() });
    },
  });
}
