/**
 * Hook for ATS scoring with Reactive Resume data.
 * 
 * This hook fetches resume data from Reactive Resume's store,
 * converts it to our format, and calls the ATS scoring service.
 * 
 * Standards: react_nextjs.mdc
 * - Reuses existing ATS scoring logic
 * - Type-safe conversions
 * - Real-time updates
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useATSScore, type ATSScoreResult } from "@/hooks/useATSScore";
import {
  jsonResumeToResumeContent,
  type JSONResume,
} from "@/lib/resume-adapter";
import type { ResumeContent } from "@/stores/resume-builder-store";

interface UseReactiveResumeATSScoreOptions {
  /**
   * Function to get current resume data from Reactive Resume store
   * This will be provided by the Reactive Resume integration
   */
  getResumeData: () => JSONResume | null;
  /**
   * Optional job description for targeted scoring
   */
  jobDescription?: string;
  /**
   * Debounce time in milliseconds
   */
  debounceMs?: number;
  /**
   * Auto-calculate score when resume changes
   */
  autoCalculate?: boolean;
}

interface UseReactiveResumeATSScoreReturn {
  result: ATSScoreResult | null;
  isCalculating: boolean;
  error: string | null;
  calculate: () => Promise<void>;
  setJobDescription: (jd: string) => void;
}

/**
 * Hook to calculate ATS score from Reactive Resume data.
 * 
 * This hook:
 * 1. Gets current resume data from Reactive Resume store
 * 2. Converts JSON Resume format to our ResumeContent format
 * 3. Calls our ATS scoring service
 * 4. Returns results in the same format as useATSScore
 */
export function useReactiveResumeATSScore({
  getResumeData,
  jobDescription: initialJobDescription,
  debounceMs = 800,
  autoCalculate = true,
}: UseReactiveResumeATSScoreOptions): UseReactiveResumeATSScoreReturn {
  const [jobDescription, setJobDescription] = useState(initialJobDescription || "");
  const [resumeContent, setResumeContent] = useState<ResumeContent | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  // Use the existing ATS score hook with our converted resume content
  const {
    result,
    isCalculating: isCalculatingBase,
    error: errorBase,
    calculate: calculateBase,
  } = useATSScore(resumeContent || ({} as ResumeContent), {
    debounceMs,
    autoCalculate: false, // We'll handle auto-calculate here
    jobDescription,
  });

  /**
   * Convert Reactive Resume data to our format and update state
   */
  const updateResumeContent = useCallback(() => {
    try {
      const jsonResume = getResumeData();
      if (!jsonResume) {
        setResumeContent(null);
        return;
      }

      const converted = jsonResumeToResumeContent(jsonResume);
      if (converted && Object.keys(converted).length > 0) {
        setResumeContent(converted as ResumeContent);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to convert resume data";
      setError(message);
      console.error("Error converting Reactive Resume data:", err);
    }
  }, [getResumeData]);

  /**
   * Calculate ATS score
   */
  const calculate = useCallback(async () => {
    setIsCalculating(true);
    setError(null);

    try {
      // Update resume content from Reactive Resume
      updateResumeContent();

      // Wait a bit for state to update
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Use the base calculate function
      await calculateBase();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to calculate ATS score";
      setError(message);
      console.error("Error calculating ATS score:", err);
    } finally {
      setIsCalculating(false);
    }
  }, [updateResumeContent, calculateBase]);

  // Auto-calculate when resume changes (debounced)
  useEffect(() => {
    if (!autoCalculate || !resumeContent) return;

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      calculate();
    }, debounceMs);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [resumeContent, autoCalculate, debounceMs, calculate]);

  // Update resume content when Reactive Resume data changes
  useEffect(() => {
    // Poll for changes (in a real implementation, this would be reactive)
    const interval = setInterval(() => {
      updateResumeContent();
    }, 1000); // Check every second

    return () => clearInterval(interval);
  }, [updateResumeContent]);

  // Combine errors
  useEffect(() => {
    if (errorBase) {
      setError(errorBase);
    }
  }, [errorBase]);

  return {
    result,
    isCalculating: isCalculating || isCalculatingBase,
    error: error || errorBase,
    calculate,
    setJobDescription,
  };
}
