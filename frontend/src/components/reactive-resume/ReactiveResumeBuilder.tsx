/**
 * Reactive Resume Builder Wrapper Component
 * 
 * This component wraps the Reactive Resume builder and integrates it with our backend.
 * Once Reactive Resume is forked and integrated, this component will use the actual
 * Reactive Resume builder components.
 * 
 * Standards: react_nextjs.mdc
 * - Client component for interactivity
 * - Integrates with our backend API
 * - Handles data synchronization
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { useReactiveResumeSync } from "@/hooks/useReactiveResumeSync";
import type { JSONResume } from "@/lib/resume-adapter";

interface ReactiveResumeBuilderProps {
  draftId: string | null;
  onDraftIdChange?: (draftId: string) => void;
}

/**
 * Reactive Resume Builder Component
 * 
 * This component will be updated once Reactive Resume is integrated.
 * For now, it provides the integration structure.
 */
export function ReactiveResumeBuilder({
  draftId,
  onDraftIdChange,
}: ReactiveResumeBuilderProps) {
  const [resumeData, setResumeData] = useState<JSONResume | null>(null);
  const resumeContainerRef = useRef<HTMLDivElement>(null);

  const { isLoading, isSaving, error, loadResume, saveResume } = useReactiveResumeSync({
    draftId,
    onResumeLoaded: (jsonResume) => {
      setResumeData(jsonResume as JSONResume);
      // TODO: Load into Reactive Resume component once integrated
    },
    onResumeChanged: (jsonResume) => {
      setResumeData(jsonResume as JSONResume);
      // TODO: Update Reactive Resume component once integrated
    },
  });

  // Load resume when draftId changes
  useEffect(() => {
    if (draftId) {
      loadResume();
    }
  }, [draftId, loadResume]);

  // TODO: Once Reactive Resume is integrated, replace this placeholder
  // with the actual Reactive Resume builder component
  // The component should:
  // 1. Accept resume data as props
  // 2. Call onResumeChange when user edits
  // 3. Display the resume editor and preview

  return (
    <div className="flex flex-col h-full">
      {/* Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
        <div className="flex items-center gap-2">
          {isLoading && (
            <span className="text-sm text-gray-600">Loading resume...</span>
          )}
          {isSaving && (
            <span className="text-sm text-gray-600">Saving...</span>
          )}
          {error && (
            <span className="text-sm text-red-600">Error: {error}</span>
          )}
          {!isLoading && !isSaving && !error && (
            <span className="text-sm text-green-600">Saved</span>
          )}
        </div>
      </div>

      {/* Reactive Resume Builder Placeholder */}
      <div ref={resumeContainerRef} className="flex-1 overflow-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading Reactive Resume...</p>
            </div>
          </div>
        ) : (
          <div className="p-8">
            <div className="max-w-4xl mx-auto">
              <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                  Reactive Resume Builder
                </h2>
                <p className="text-gray-600 mb-6">
                  Once Reactive Resume is forked and integrated, the builder will appear here.
                </p>
                <div className="text-left bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Integration Status:</strong>
                  </p>
                  <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                    <li>Resume adapter utilities: ✓ Created</li>
                    <li>Sync hooks: ✓ Created</li>
                    <li>ATS scoring hooks: ✓ Created</li>
                    <li>Reactive Resume code: ⏳ Pending fork integration</li>
                  </ul>
                </div>
                {resumeData && (
                  <div className="mt-6 text-left">
                    <p className="text-sm font-semibold text-gray-700 mb-2">
                      Resume Data (JSON Resume format):
                    </p>
                    <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-64">
                      {JSON.stringify(resumeData, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Function to get current resume data from Reactive Resume
 * This will be implemented once Reactive Resume is integrated
 */
export function getReactiveResumeData(): JSONResume | null {
  // TODO: Access Reactive Resume's Zustand store to get current resume
  // Example: return useResumeStore.getState().resume;
  return null;
}
