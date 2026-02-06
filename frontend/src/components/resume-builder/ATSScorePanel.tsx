/**
 * ATS Score Panel - Always visible sidebar showing ATS compatibility score.
 *
 * Features:
 * - Circular gauge showing overall score (0-100)
 * - Breakdown sections for each criterion
 * - Color-coded indicators (green/yellow/red)
 * - Matched/missing keywords display
 * - Improvement suggestions list
 */

"use client";

import { Loader2, Target } from "lucide-react";
import { ATSScoreContent, type ScoreBreakdown } from "./ATSScoreContent";

interface ATSScorePanelProps {
  totalScore: number | null;
  breakdown: ScoreBreakdown | null;
  matchedKeywords: string[];
  missingKeywords: string[];
  suggestions: string[];
  isCalculating: boolean;
  onRecalculate?: () => void;
  isMinimized?: boolean;
  onExpand?: () => void;
}


export function ATSScorePanel({
  totalScore,
  breakdown,
  matchedKeywords,
  missingKeywords,
  suggestions,
  isCalculating,
  onRecalculate,
  isMinimized = false,
  onExpand,
}: ATSScorePanelProps) {

  // Minimized view - icon-only strip (after all hooks)
  if (isMinimized) {
    return (
      <div className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 overflow-hidden">
        <div
          className="flex-1 flex flex-col items-center justify-center gap-2 p-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          onClick={onExpand}
          title="Click to expand ATS panel"
        >
          <div className="p-2 bg-blue-500 rounded-lg">
            <Target className="h-5 w-5 text-white" />
          </div>
          {totalScore !== null && (
            <div className="flex flex-col items-center">
              <span
                className={`text-lg font-bold ${
                  totalScore >= 80
                    ? "text-green-500"
                    : totalScore >= 60
                    ? "text-yellow-500"
                    : "text-red-500"
                }`}
              >
                {totalScore}
              </span>
              <span className="text-[10px] text-gray-500 dark:text-gray-400">/100</span>
            </div>
          )}
          {isCalculating && (
            <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
          )}
        </div>
      </div>
    );
  }

  // Full expanded view
  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 overflow-hidden w-full min-w-0 max-w-full box-border">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-500 rounded-lg">
              <Target className="h-4 w-4 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 dark:text-white text-sm">
                ATS Score
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Applicant Tracking System
              </p>
            </div>
          </div>
          {isCalculating && (
            <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
          )}
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden w-full max-w-full">
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
    </div>
  );
}
