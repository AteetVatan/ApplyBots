/**
 * ATS Score Dropdown - Collapsible dropdown overlay for ATS score display.
 * 
 * Features:
 * - Collapsed state: Compact button showing percentage (top-right)
 * - Expanded state: Full panel overlay with backdrop
 * - Follows existing modal patterns (TemplateSelector, ExportImport)
 * - Uses framer-motion for smooth animations
 * - Responsive: Full screen on mobile, overlay on desktop
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Target, X, Loader2 } from "lucide-react";
import { ATSScoreContent, type ScoreBreakdown } from "./ATSScoreContent";

export interface ATSScoreDropdownProps {
  totalScore: number | null;
  breakdown: ScoreBreakdown | null;
  matchedKeywords: string[];
  missingKeywords: string[];
  suggestions: string[];
  isCalculating: boolean;
  onRecalculate?: () => void;
}

export function ATSScoreDropdown({
  totalScore,
  breakdown,
  matchedKeywords,
  missingKeywords,
  suggestions,
  isCalculating,
  onRecalculate,
}: ATSScoreDropdownProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // Handle Escape key to close
  useEffect(() => {
    if (!isExpanded) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsExpanded(false);
        // Return focus to button
        buttonRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isExpanded]);

  // Focus management: Focus first focusable element when opened
  useEffect(() => {
    if (isExpanded && panelRef.current) {
      // Find first focusable element (close button)
      const firstFocusable = panelRef.current.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusable?.focus();
    }
  }, [isExpanded]);

  const getScoreColor = (score: number | null) => {
    if (score === null) return "text-neutral-400 dark:text-neutral-500";
    if (score >= 80) return "text-success-600 dark:text-success-500";
    if (score >= 60) return "text-warning-600 dark:text-warning-500";
    return "text-error-600 dark:text-error-500";
  };

  return (
    <>
      {/* Collapsed State: Fixed button */}
      <button
        ref={buttonRef}
        onClick={() => setIsExpanded(true)}
        disabled={isCalculating}
        className="fixed top-[0.625rem] right-4 z-50 flex items-center gap-2 px-4 py-2 rounded-lg shadow-lg bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/50 hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="ATS Score"
        aria-expanded={isExpanded}
      >
        {isCalculating ? (
          <Loader2 className="h-4 w-4 text-primary-500 animate-spin" />
        ) : (
          <Target className={`h-4 w-4 ${getScoreColor(totalScore)}`} />
        )}
        <span className={`text-sm font-medium ${getScoreColor(totalScore)}`}>
          ATS: {totalScore !== null ? `${totalScore}%` : "--"}
        </span>
      </button>

      {/* Expanded State: Backdrop and Panel */}
      <AnimatePresence>
        {isExpanded && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-50 bg-black/50 dark:bg-black/70"
              onClick={() => {
                setIsExpanded(false);
                buttonRef.current?.focus();
              }}
              aria-hidden="true"
            />

            {/* Panel */}
            <motion.div
              ref={panelRef}
              initial={{ opacity: 0, scale: 0.95, y: -8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -8 }}
              transition={{ duration: 0.2 }}
              className={`
                fixed z-50
                inset-0 md:inset-auto md:top-4 md:right-4
                max-w-none max-h-none md:max-w-md md:max-h-[80vh]
                rounded-none md:rounded-xl
                bg-white dark:bg-neutral-900
                shadow-2xl
                flex flex-col
                overflow-hidden
              `}
              role="dialog"
              aria-modal="true"
              aria-labelledby="ats-score-title"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex-shrink-0 p-4 border-b border-neutral-200 dark:border-neutral-700 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-neutral-800 dark:to-neutral-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-primary-500 rounded-lg">
                      <Target className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <h2
                        id="ats-score-title"
                        className="font-semibold text-neutral-900 dark:text-white text-sm"
                      >
                        ATS Score
                      </h2>
                      <p className="text-xs text-neutral-500 dark:text-neutral-400">
                        Applicant Tracking System
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isCalculating && (
                      <Loader2 className="h-4 w-4 text-primary-500 animate-spin" />
                    )}
                    <button
                      onClick={() => {
                        setIsExpanded(false);
                        buttonRef.current?.focus();
                      }}
                      className="p-2 text-neutral-500 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
                      aria-label="Close ATS Score panel"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Content Area */}
              <div className="flex-1 overflow-y-auto overflow-x-hidden w-full max-w-full p-4 md:p-6">
                <ATSScoreContent
                  totalScore={totalScore}
                  breakdown={breakdown}
                  matchedKeywords={matchedKeywords}
                  missingKeywords={missingKeywords}
                  suggestions={suggestions}
                  isCalculating={isCalculating}
                  onRecalculate={onRecalculate}
                />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
