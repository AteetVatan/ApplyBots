/**
 * Preview panel with live template rendering and zoom controls.
 */

"use client";

import { useRef, useState, useMemo } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { getTemplateComponent, TEMPLATES } from "./templates";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Download,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

export function PreviewPanel() {
  const content = useResumeBuilderStore((s) => s.content);
  const templateId = useResumeBuilderStore((s) => s.templateId);
  const activeSection = useResumeBuilderStore((s) => s.activeSection);
  const atsScore = useResumeBuilderStore((s) => s.atsScore);
  const previewScale = useResumeBuilderStore((s) => s.previewScale);
  const setPreviewScale = useResumeBuilderStore((s) => s.setPreviewScale);

  const containerRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  // Get the template component
  const TemplateComponent = useMemo(
    () => getTemplateComponent(templateId),
    [templateId]
  );

  // Zoom controls
  const handleZoomIn = () => {
    setPreviewScale(Math.min(previewScale + 0.1, 1.5));
  };

  const handleZoomOut = () => {
    setPreviewScale(Math.max(previewScale - 0.1, 0.3));
  };

  const handleFitToWidth = () => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.clientWidth - 48; // 24px padding each side
      const resumeWidth = 8.5 * 96; // 8.5 inches * 96 DPI
      const newScale = Math.min(containerWidth / resumeWidth, 1);
      setPreviewScale(newScale);
    }
  };

  // Export PDF (simplified - in production would call API)
  const handleExport = async () => {
    setIsExporting(true);
    try {
      // This would call the API in production
      await new Promise((resolve) => setTimeout(resolve, 1500));
      // For demo, just show alert
      alert("PDF export would download here!");
    } finally {
      setIsExporting(false);
    }
  };

  // ATS score color
  const getATSScoreColor = (score: number | null) => {
    if (score === null) return "text-gray-500";
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  const getATSScoreBg = (score: number | null) => {
    if (score === null) return "bg-gray-100 dark:bg-gray-800";
    if (score >= 80) return "bg-green-50 dark:bg-green-900/20";
    if (score >= 60) return "bg-yellow-50 dark:bg-yellow-900/20";
    return "bg-red-50 dark:bg-red-900/20";
  };

  return (
    <div className="flex flex-col h-full bg-gray-100 dark:bg-gray-950">
      {/* Toolbar */}
      <div className="flex-shrink-0 flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        {/* Zoom controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            title="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[3rem] text-center">
            {Math.round(previewScale * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            title="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={handleFitToWidth}
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            title="Fit to width"
          >
            <Maximize2 className="h-4 w-4" />
          </button>
        </div>

        {/* ATS Score */}
        <div
          className={`flex items-center gap-2 px-3 py-1 rounded-full ${getATSScoreBg(atsScore)}`}
        >
          {atsScore !== null ? (
            <>
              {atsScore >= 80 ? (
                <CheckCircle2 className={`h-4 w-4 ${getATSScoreColor(atsScore)}`} />
              ) : (
                <AlertCircle className={`h-4 w-4 ${getATSScoreColor(atsScore)}`} />
              )}
              <span className={`text-sm font-medium ${getATSScoreColor(atsScore)}`}>
                ATS Score: {atsScore}%
              </span>
            </>
          ) : (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              ATS Score: --
            </span>
          )}
        </div>

        {/* Export button */}
        <button
          onClick={handleExport}
          disabled={isExporting}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          {isExporting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <Download className="h-4 w-4" />
              Export PDF
            </>
          )}
        </button>
      </div>

      {/* Preview area */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-6"
        style={{
          backgroundImage:
            "radial-gradient(circle, #cbd5e1 1px, transparent 1px)",
          backgroundSize: "16px 16px",
        }}
      >
        <div className="flex justify-center">
          {/* Template shadow wrapper */}
          <div className="shadow-2xl">
            <TemplateComponent
              content={content}
              scale={previewScale}
              highlightSection={activeSection}
            />
          </div>
        </div>
      </div>

      {/* Template selector hint */}
      <div className="flex-shrink-0 p-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <span>
            Template:{" "}
            <span className="font-medium text-gray-700 dark:text-gray-300">
              {TEMPLATES.find((t) => t.id === templateId)?.name || "Professional Modern"}
            </span>
          </span>
          <span className="text-gray-300 dark:text-gray-600">|</span>
          <span className="text-xs">
            Press <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">Ctrl + P</kbd> to print
          </span>
        </div>
      </div>
    </div>
  );
}
