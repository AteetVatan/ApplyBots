/**
 * Hook for syncing Reactive Resume data with our backend.
 * 
 * This hook bridges Reactive Resume's state management with our backend API.
 * It handles loading drafts from our backend and auto-saving changes.
 * 
 * Standards: react_nextjs.mdc
 * - TanStack Query for server state
 * - Debounced auto-save
 * - Type-safe conversions
 */

"use client";

import { useEffect, useCallback, useRef, useState } from "react";
import { useDraft, useUpdateDraft, useCreateDraft } from "@/hooks/useResumeDrafts";
import {
  resumeContentToJsonResume,
  jsonResumeToResumeContent,
  apiSchemaToResumeContent,
  resumeContentToApiSchema,
} from "@/lib/resume-adapter";
import type { ResumeContent } from "@/stores/resume-builder-store";
import type { ResumeContentSchemaAPI } from "@/lib/api";

interface UseReactiveResumeSyncOptions {
  draftId: string | null;
  onResumeLoaded?: (jsonResume: unknown) => void;
  onResumeChanged?: (jsonResume: unknown) => void;
}

interface UseReactiveResumeSyncReturn {
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  loadResume: () => Promise<void>;
  saveResume: (jsonResume: unknown) => Promise<void>;
  getCurrentResume: () => ResumeContent | null;
}

/**
 * Hook to sync Reactive Resume with our backend.
 * 
 * This hook:
 * 1. Loads draft from backend and converts to JSON Resume format for Reactive Resume
 * 2. Listens for changes in Reactive Resume and auto-saves to backend
 * 3. Handles data conversion between formats
 */
export function useReactiveResumeSync({
  draftId,
  onResumeLoaded,
  onResumeChanged,
}: UseReactiveResumeSyncOptions): UseReactiveResumeSyncReturn {
  const { data: draft, isLoading } = useDraft(draftId);
  const updateDraftMutation = useUpdateDraft();
  const createDraftMutation = useCreateDraft();
  
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const currentResumeRef = useRef<ResumeContent | null>(null);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Load resume from backend and convert to JSON Resume format
   */
  const loadResume = useCallback(async () => {
    if (!draft) return;

    try {
      // Convert backend format to frontend format
      const resumeContent = apiSchemaToResumeContent(draft.content);
      currentResumeRef.current = resumeContent;

      // Convert to JSON Resume format for Reactive Resume
      const jsonResume = resumeContentToJsonResume(resumeContent, draft.name);

      // Notify Reactive Resume to load this data
      onResumeLoaded?.(jsonResume);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load resume";
      setError(message);
      console.error("Error loading resume:", err);
    }
  }, [draft, onResumeLoaded]);

  /**
   * Save resume to backend (converts from JSON Resume format)
   */
  const saveResume = useCallback(
    async (jsonResume: unknown) => {
      if (!draftId) {
        // Create new draft if no ID
        try {
          const resumeContent = jsonResumeToResumeContent(jsonResume as Record<string, unknown>);
          const apiSchema = resumeContentToApiSchema(resumeContent as ResumeContent);
          
          const newDraft = await createDraftMutation.mutateAsync({
            name: "Untitled Resume",
            content: apiSchema,
            template_id: resumeContent.templateId || "bronzor",
          });

          // Update current resume ref
          currentResumeRef.current = resumeContent as ResumeContent;
          
          // Notify parent component of new draft ID
          onResumeChanged?.(jsonResume);
        } catch (err) {
          const message = err instanceof Error ? err.message : "Failed to create draft";
          setError(message);
          console.error("Error creating draft:", err);
        }
        return;
      }

      // Debounce saves
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }

      setIsSaving(true);
      setError(null);

      saveTimeoutRef.current = setTimeout(async () => {
        try {
          // Convert JSON Resume to our format
          const resumeContent = jsonResumeToResumeContent(jsonResume as Record<string, unknown>);
          currentResumeRef.current = resumeContent as ResumeContent;

          // Convert to API schema
          const apiSchema = resumeContentToApiSchema(resumeContent as ResumeContent);

          // Update draft
          await updateDraftMutation.mutateAsync({
            id: draftId,
            data: {
              content: apiSchema,
            },
          });

          onResumeChanged?.(jsonResume);
        } catch (err) {
          const message = err instanceof Error ? err.message : "Failed to save draft";
          setError(message);
          console.error("Error saving draft:", err);
        } finally {
          setIsSaving(false);
        }
      }, 2000); // 2 second debounce
    },
    [draftId, updateDraftMutation, createDraftMutation, onResumeChanged]
  );

  /**
   * Get current resume in our format
   */
  const getCurrentResume = useCallback((): ResumeContent | null => {
    return currentResumeRef.current;
  }, []);

  // Load resume when draft is available
  useEffect(() => {
    if (draft && !isLoading) {
      loadResume();
    }
  }, [draft, isLoading, loadResume]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  return {
    isLoading,
    isSaving,
    error,
    loadResume,
    saveResume,
    getCurrentResume,
  };
}
