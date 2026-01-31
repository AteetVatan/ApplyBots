/**
 * AI Assistant ATS analysis mode.
 */

"use client";

import { TrendingUp, Loader2, ChevronRight } from "lucide-react";

interface ATSResult {
  score: number;
  suggestions: string[];
  matchedKeywords: string[];
}

interface ATSModeProps {
  isLoading: boolean;
  jobDescription: string;
  atsResult: ATSResult | null;
  onJobDescriptionChange: (value: string) => void;
  onGenerate: () => void;
}

export function ATSMode({
  isLoading,
  jobDescription,
  atsResult,
  onJobDescriptionChange,
  onGenerate,
}: ATSModeProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="space-y-4">
      <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
        <h3 className="font-medium text-amber-800 dark:text-amber-300 mb-1">
          ATS Compatibility Check
        </h3>
        <p className="text-sm text-amber-600 dark:text-amber-400">
          Analyze how well your resume will perform with Applicant Tracking Systems.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Job Description (optional)
        </label>
        <textarea
          value={jobDescription}
          onChange={(e) => onJobDescriptionChange(e.target.value)}
          placeholder="Paste the job description for better keyword matching..."
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
      </div>

      <button
        onClick={onGenerate}
        disabled={isLoading}
        className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg hover:from-amber-600 hover:to-orange-600 disabled:opacity-50"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <TrendingUp className="h-4 w-4" />
            Analyze ATS Score
          </>
        )}
      </button>

      {atsResult && (
        <div className="space-y-3">
          <div className="text-center py-4">
            <div className={`text-5xl font-bold ${getScoreColor(atsResult.score)}`}>
              {atsResult.score}%
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              ATS Compatibility Score
            </p>
          </div>

          {atsResult.matchedKeywords.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                Matched Keywords
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {atsResult.matchedKeywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-xs rounded"
                  >
                    ✓ {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              Improvement Suggestions
            </h4>
            <ul className="space-y-2">
              {atsResult.suggestions.map((suggestion, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
                >
                  <ChevronRight className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
