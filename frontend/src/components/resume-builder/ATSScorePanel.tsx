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

import { useState, useEffect, useRef } from "react";
import {
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Loader2,
  TrendingUp,
  FileText,
  Target,
  Hash,
  User,
  Sparkles,
} from "lucide-react";

interface ScoreBreakdown {
  keywordMatch: { score: number; max: number };
  formatting: { score: number; max: number };
  sectionCompleteness: { score: number; max: number };
  quantifiedAchievements: { score: number; max: number };
  length: { score: number; max: number };
  contactInfo: { score: number; max: number };
}

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

// Circular progress component
function CircularGauge({
  score,
  size = 140,
  strokeWidth = 12,
}: {
  score: number | null;
  size?: number;
  strokeWidth?: number;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const displayScore = score ?? 0;
  const offset = circumference - (displayScore / 100) * circumference;

  const getScoreColor = (s: number) => {
    if (s >= 80) return { stroke: "#22c55e", text: "text-green-500", bg: "bg-green-500" };
    if (s >= 60) return { stroke: "#eab308", text: "text-yellow-500", bg: "bg-yellow-500" };
    return { stroke: "#ef4444", text: "text-red-500", bg: "bg-red-500" };
  };

  const colors = getScoreColor(displayScore);

  const centerX = size / 2;
  const centerY = size / 2;

  return (
    <div className="relative flex items-center justify-center flex-shrink-0" style={{ width: `${size}px`, maxWidth: "100%", aspectRatio: "1", flexShrink: 0 }}>
      <svg className="transform -rotate-90 w-full h-full" viewBox={`0 0 ${size} ${size}`} preserveAspectRatio="xMidYMid meet" style={{ width: "100%", height: "100%" }}>
        {/* Background circle */}
        <circle
          cx={centerX}
          cy={centerY}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-gray-200 dark:text-gray-700"
        />
        {/* Progress circle */}
        <circle
          cx={centerX}
          cy={centerY}
          r={radius}
          stroke={score !== null ? colors.stroke : "#9ca3af"}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={score !== null ? offset : circumference}
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        {score !== null ? (
          <>
            <span className={`text-3xl font-bold ${colors.text} leading-none`}>{score}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400 leading-none">/ 100</span>
          </>
        ) : (
          <>
            <span className="text-2xl font-bold text-gray-400 leading-none">--</span>
            <span className="text-xs text-gray-400 leading-none">Not calculated</span>
          </>
        )}
      </div>
    </div>
  );
}

// Individual score bar component
function ScoreBar({
  label,
  icon: Icon,
  score,
  maxScore,
}: {
  label: string;
  icon: React.ElementType;
  score: number;
  maxScore: number;
}) {
  const percentage = (score / maxScore) * 100;
  const getColor = (pct: number) => {
    if (pct >= 80) return "bg-green-500";
    if (pct >= 50) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="space-y-1 min-w-0 w-full max-w-full box-border overflow-hidden">
      <div className="flex items-center justify-between text-xs min-w-0 max-w-full overflow-hidden">
        <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 min-w-0 flex-1 max-w-full overflow-hidden">
          <Icon className="h-3.5 w-3.5 flex-shrink-0" />
          <span className="truncate min-w-0 overflow-hidden">{label}</span>
        </div>
        <span className="font-medium text-gray-900 dark:text-white flex-shrink-0 ml-2 whitespace-nowrap">
          {score}/{maxScore}
        </span>
      </div>
      <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden w-full max-w-full box-border">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getColor(percentage)}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
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
  const [expandedSections, setExpandedSections] = useState({
    breakdown: true,
    keywords: false,
    suggestions: true,
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const getScoreLabel = (score: number | null) => {
    if (score === null) return "Not Calculated";
    if (score >= 90) return "Excellent";
    if (score >= 80) return "Very Good";
    if (score >= 70) return "Good";
    if (score >= 60) return "Fair";
    return "Needs Work";
  };

  const getScoreIcon = (score: number | null) => {
    if (score === null) return AlertCircle;
    if (score >= 80) return CheckCircle2;
    if (score >= 60) return AlertCircle;
    return XCircle;
  };

  const ScoreIcon = getScoreIcon(totalScore);

  // All hooks must be called before any early returns
  const panelRef = useRef<HTMLDivElement>(null);
  const gaugeContainerRef = useRef<HTMLDivElement>(null);
  const breakdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // #region agent log
    const timer = setTimeout(() => {
      if (panelRef.current && gaugeContainerRef.current && breakdownRef.current) {
        const panelWidth = panelRef.current.offsetWidth;
        const gaugeContainerWidth = gaugeContainerRef.current.offsetWidth;
        const breakdownWidth = breakdownRef.current.offsetWidth;
        const gaugeContainerScrollWidth = gaugeContainerRef.current.scrollWidth;
        const breakdownScrollWidth = breakdownRef.current.scrollWidth;
        const gaugeElement = gaugeContainerRef.current.querySelector('svg')?.parentElement as HTMLElement | null;
        const gaugeWidth = gaugeElement ? gaugeElement.offsetWidth : 0;
        const gaugeContainerLeft = gaugeContainerRef.current.offsetLeft;
        const gaugeLeft = gaugeElement ? gaugeElement.offsetLeft : 0;
        const gaugeLeftRelative = gaugeElement ? gaugeLeft - gaugeContainerLeft : 0;
        const expectedCenterLeft = (gaugeContainerWidth - gaugeWidth) / 2;
        const gaugeComputedStyle = gaugeElement ? window.getComputedStyle(gaugeElement) : null;
        const containerComputedStyle = window.getComputedStyle(gaugeContainerRef.current);
        const scoreBars = breakdownRef.current.querySelectorAll('[class*="space-y-1"]');
        const barWidths = Array.from(scoreBars).map(bar => {
          const el = bar as HTMLElement;
          return { width: el.offsetWidth, scrollWidth: el.scrollWidth, left: el.offsetLeft };
        });
        const maxBarWidth = Math.max(...barWidths.map(b => b.width), 0);
        const maxBarScrollWidth = Math.max(...barWidths.map(b => b.scrollWidth), 0);
        const breakdownContent = breakdownRef.current.querySelector('[class*="px-3 pb-3"]');
        const breakdownContentWidth = breakdownContent ? (breakdownContent as HTMLElement).offsetWidth : 0;
        const breakdownContentScrollWidth = breakdownContent ? (breakdownContent as HTMLElement).scrollWidth : 0;
        const breakdownContentPadding = breakdownContent ? {
          left: parseFloat(window.getComputedStyle(breakdownContent as HTMLElement).paddingLeft),
          right: parseFloat(window.getComputedStyle(breakdownContent as HTMLElement).paddingRight)
        } : { left: 0, right: 0 };
        const breakdownContentInnerWidth = breakdownContentWidth - breakdownContentPadding.left - breakdownContentPadding.right;
        const gaugeContainerPadding = {
          left: parseFloat(containerComputedStyle.paddingLeft),
          right: parseFloat(containerComputedStyle.paddingRight)
        };
        const gaugeContainerInnerWidth = gaugeContainerWidth - gaugeContainerPadding.left - gaugeContainerPadding.right;
        const gaugeExpectedCenterInContainer = (gaugeContainerInnerWidth - gaugeWidth) / 2 + gaugeContainerPadding.left;
        fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ATSScorePanel.tsx:237',message:'Panel width measurements',data:{panelWidth,gaugeContainerWidth,breakdownWidth,gaugeContainerScrollWidth,breakdownScrollWidth,gaugeWidth,gaugeLeft,gaugeLeftRelative,gaugeContainerLeft,expectedCenterLeft,gaugeOffsetFromCenter:Math.abs(gaugeLeftRelative-expectedCenterLeft),gaugeExpectedCenterInContainer,gaugeContainerInnerWidth,gaugeContainerPadding,breakdownContentInnerWidth,breakdownContentPadding,gaugeDisplay:gaugeComputedStyle?.display,gaugeMarginLeft:gaugeComputedStyle?.marginLeft,gaugeMarginRight:gaugeComputedStyle?.marginRight,containerDisplay:containerComputedStyle.display,containerJustifyContent:containerComputedStyle.justifyContent,containerAlignItems:containerComputedStyle.alignItems,containerPadding:containerComputedStyle.padding,maxBarWidth,maxBarScrollWidth,breakdownContentWidth,breakdownContentScrollWidth,gaugeOverflow:gaugeContainerScrollWidth>gaugeContainerWidth,breakdownOverflow:breakdownScrollWidth>breakdownWidth,barOverflow:maxBarScrollWidth>maxBarWidth,contentOverflow:breakdownContentScrollWidth>breakdownContentWidth,barFitsInContent:maxBarWidth<=breakdownContentInnerWidth},timestamp:Date.now(),sessionId:'debug-session',runId:'run4',hypothesisId:'A,B,C,E'})}).catch(()=>{});
      }
    }, 100);
    return () => clearTimeout(timer);
    // #endregion
  });

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
    <div ref={panelRef} className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 overflow-hidden w-full min-w-0 max-w-full box-border">
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
        {/* Circular Gauge */}
        <div ref={gaugeContainerRef} className="p-4 flex flex-col items-center justify-center w-full max-w-full border-b border-gray-100 dark:border-gray-800 box-border overflow-hidden">
          <CircularGauge score={totalScore} />
          <div className="mt-3 flex items-center justify-center gap-1.5">
            <ScoreIcon
              className={`h-4 w-4 ${
                totalScore === null
                  ? "text-gray-400"
                  : totalScore >= 80
                  ? "text-green-500"
                  : totalScore >= 60
                  ? "text-yellow-500"
                  : "text-red-500"
              }`}
            />
            <span
              className={`text-sm font-medium ${
                totalScore === null
                  ? "text-gray-400"
                  : totalScore >= 80
                  ? "text-green-600 dark:text-green-400"
                  : totalScore >= 60
                  ? "text-yellow-600 dark:text-yellow-400"
                  : "text-red-600 dark:text-red-400"
              }`}
            >
              {getScoreLabel(totalScore)}
            </span>
          </div>
          {onRecalculate && (
            <button
              onClick={onRecalculate}
              disabled={isCalculating}
              className="mt-3 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors disabled:opacity-50 mx-auto"
            >
              <TrendingUp className="h-3.5 w-3.5" />
              Recalculate Score
            </button>
          )}
        </div>

        {/* Score Breakdown */}
        <div ref={breakdownRef} className="border-b border-gray-100 dark:border-gray-800 w-full min-w-0 max-w-full overflow-hidden box-border">
          <button
            onClick={() => toggleSection("breakdown")}
            className="w-full flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors min-w-0 max-w-full box-border"
          >
            <span className="text-sm font-medium text-gray-900 dark:text-white truncate min-w-0">
              Score Breakdown
            </span>
            {expandedSections.breakdown ? (
              <ChevronUp className="h-4 w-4 text-gray-500 flex-shrink-0 ml-2" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-500 flex-shrink-0 ml-2" />
            )}
          </button>
          {expandedSections.breakdown && breakdown && (
            <div className="px-3 pb-3 space-y-3 w-full min-w-0 max-w-full box-border overflow-x-hidden">
              <ScoreBar
                label="Keyword Match"
                icon={Target}
                score={breakdown.keywordMatch.score}
                maxScore={breakdown.keywordMatch.max}
              />
              <ScoreBar
                label="Formatting"
                icon={FileText}
                score={breakdown.formatting.score}
                maxScore={breakdown.formatting.max}
              />
              <ScoreBar
                label="Sections"
                icon={Hash}
                score={breakdown.sectionCompleteness.score}
                maxScore={breakdown.sectionCompleteness.max}
              />
              <ScoreBar
                label="Achievements"
                icon={TrendingUp}
                score={breakdown.quantifiedAchievements.score}
                maxScore={breakdown.quantifiedAchievements.max}
              />
              <ScoreBar
                label="Length"
                icon={FileText}
                score={breakdown.length.score}
                maxScore={breakdown.length.max}
              />
              <ScoreBar
                label="Contact Info"
                icon={User}
                score={breakdown.contactInfo.score}
                maxScore={breakdown.contactInfo.max}
              />
            </div>
          )}
          {expandedSections.breakdown && !breakdown && (
            <div className="px-3 pb-3">
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center py-2">
                Calculate your score to see the breakdown
              </p>
            </div>
          )}
        </div>

        {/* Keywords */}
        <div className="border-b border-gray-100 dark:border-gray-800 w-full min-w-0 max-w-full overflow-hidden box-border">
          <button
            onClick={() => toggleSection("keywords")}
            className="w-full flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors min-w-0 max-w-full box-border"
          >
            <span className="text-sm font-medium text-gray-900 dark:text-white truncate min-w-0">
              Keywords
            </span>
            {expandedSections.keywords ? (
              <ChevronUp className="h-4 w-4 text-gray-500 flex-shrink-0 ml-2" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-500 flex-shrink-0 ml-2" />
            )}
          </button>
          {expandedSections.keywords && (
            <div className="px-3 pb-3 space-y-3 w-full min-w-0 max-w-full box-border">
              {matchedKeywords.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-green-600 dark:text-green-400 mb-1.5">
                    ✓ Matched ({matchedKeywords.length})
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {matchedKeywords.map((kw) => (
                      <span
                        key={kw}
                        className="px-1.5 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-[10px] rounded"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {missingKeywords.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-red-600 dark:text-red-400 mb-1.5">
                    ✗ Missing ({missingKeywords.length})
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {missingKeywords.slice(0, 10).map((kw) => (
                      <span
                        key={kw}
                        className="px-1.5 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-[10px] rounded"
                      >
                        {kw}
                      </span>
                    ))}
                    {missingKeywords.length > 10 && (
                      <span className="px-1.5 py-0.5 text-gray-500 text-[10px]">
                        +{missingKeywords.length - 10} more
                      </span>
                    )}
                  </div>
                </div>
              )}
              {matchedKeywords.length === 0 && missingKeywords.length === 0 && (
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center py-2">
                  Add a job description for keyword analysis
                </p>
              )}
            </div>
          )}
        </div>

        {/* Suggestions */}
        <div className="w-full min-w-0 max-w-full overflow-hidden box-border">
          <button
            onClick={() => toggleSection("suggestions")}
            className="w-full flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors min-w-0 max-w-full box-border"
          >
            <div className="flex items-center gap-1.5 min-w-0 flex-1 max-w-full">
              <Sparkles className="h-3.5 w-3.5 text-purple-500 flex-shrink-0" />
              <span className="text-sm font-medium text-gray-900 dark:text-white truncate min-w-0">
                Suggestions
              </span>
            </div>
            {expandedSections.suggestions ? (
              <ChevronUp className="h-4 w-4 text-gray-500 flex-shrink-0 ml-2" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-500 flex-shrink-0 ml-2" />
            )}
          </button>
          {expandedSections.suggestions && (
            <div className="px-3 pb-3 w-full min-w-0 max-w-full box-border">
              {suggestions.length > 0 ? (
                <ul className="space-y-2">
                  {suggestions.map((suggestion, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400 min-w-0"
                    >
                      <span className="text-purple-500 mt-0.5 flex-shrink-0">→</span>
                      <span className="break-words min-w-0">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center py-2">
                  {totalScore !== null && totalScore >= 80
                    ? "Great job! Your resume is ATS-optimized."
                    : "Calculate your score to get personalized suggestions"}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
