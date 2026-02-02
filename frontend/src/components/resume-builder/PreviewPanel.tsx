/**
 * Preview panel with live template rendering and zoom controls.
 * Supports theme settings for page size (A4/Letter).
 * Includes dual PDF export: ATS-friendly (real text) and Visual (exact match).
 */

"use client";

import { useRef, useState, useMemo, useEffect } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { getTemplateComponent, TEMPLATES } from "./templates";
import { TemplateSettingsButton } from "./TemplateSettings";
import { usePDFExport } from "@/hooks/usePDFExport";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Download,
  Loader2,
  FileText,
  AlertCircle,
  ChevronDown,
  FileCheck,
  ImageIcon,
  X,
} from "lucide-react";

// Page dimensions in inches
const PAGE_DIMENSIONS = {
  letter: { width: 8.5, height: 11 },
  a4: { width: 8.27, height: 11.69 },
};

export function PreviewPanel() {
  const content = useResumeBuilderStore((s) => s.content);
  const templateId = useResumeBuilderStore((s) => s.templateId);
  const activeSection = useResumeBuilderStore((s) => s.activeSection);
  const previewScale = useResumeBuilderStore((s) => s.previewScale);
  const setPreviewScale = useResumeBuilderStore((s) => s.setPreviewScale);
  const themeSettings = useResumeBuilderStore((s) => s.themeSettings);

  const containerRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const exportMenuRef = useRef<HTMLDivElement>(null);

  // PDF Export hook
  const {
    isGenerating,
    error: exportError,
    exportType,
    generateATSPDF,
    generateVisualPDF,
    clearError,
  } = usePDFExport({
    content,
    themeSettings,
    templateId,
  });

  // Close menu on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target as Node)) {
        setShowExportMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Get page dimensions based on settings
  const pageDimensions = useMemo(() => {
    const dims = PAGE_DIMENSIONS[themeSettings.pageSize];
    return {
      width: dims.width * 96, // Convert to pixels (96 DPI)
      height: dims.height * 96,
    };
  }, [themeSettings.pageSize]);

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
      const newScale = Math.min(containerWidth / pageDimensions.width, 1);
      setPreviewScale(newScale);
    }
  };

  // Export handlers
  const handleExportATS = async () => {
    setShowExportMenu(false);
    await generateATSPDF();
  };

  const handleExportVisual = async () => {
    setShowExportMenu(false);
    if (previewRef.current) {
      await generateVisualPDF(previewRef.current);
    }
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

        {/* Page size indicator + Settings */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
            <FileText className="h-3.5 w-3.5" />
            {themeSettings.pageSize.toUpperCase()}
          </div>
          <TemplateSettingsButton />
        </div>

        {/* Export button with dropdown */}
        <div className="flex items-center gap-2 relative" ref={exportMenuRef}>
          {exportError && (
            <div className="flex items-center gap-1.5 px-2 py-1 bg-red-100 dark:bg-red-900/30 rounded text-xs text-red-600 dark:text-red-400">
              <AlertCircle className="h-3.5 w-3.5" />
              <span className="max-w-[200px] truncate">{exportError}</span>
              <button onClick={clearError} className="ml-1 hover:opacity-70">
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
          
          <div className="relative">
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              disabled={isGenerating}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  {exportType === "ats" ? "Generating ATS PDF..." : "Generating Visual PDF..."}
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Export PDF
                  <ChevronDown className="h-4 w-4" />
                </>
              )}
            </button>

            {/* Export dropdown menu */}
            {showExportMenu && !isGenerating && (
              <div className="absolute right-0 top-full mt-2 w-72 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
                <div className="p-3 border-b border-gray-100 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Choose export format based on your needs
                  </p>
                </div>
                
                {/* ATS-Friendly Option */}
                <button
                  onClick={handleExportATS}
                  className="w-full p-3 text-left hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                      <FileCheck className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          ATS-Friendly
                        </span>
                        <span className="px-1.5 py-0.5 text-[10px] font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded">
                          RECOMMENDED
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        Real, selectable text. Optimized for Applicant Tracking Systems.
                        Best for job applications.
                      </p>
                    </div>
                  </div>
                </button>

                {/* Divider */}
                <div className="border-t border-gray-100 dark:border-gray-700" />

                {/* Visual Option */}
                <button
                  onClick={handleExportVisual}
                  className="w-full p-3 text-left hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                      <ImageIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          Visual Match
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        Exact visual copy of preview. Image-based, not ATS-parseable.
                        Best for sharing or printing.
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            )}
          </div>
        </div>
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
        <div className="flex justify-center items-start w-full">
          {/* Template shadow wrapper - accounts for scaled dimensions */}
          <div
            ref={previewRef}
            data-pdf-capture="true"
            className="shadow-2xl bg-white"
            style={{
              width: `${pageDimensions.width * previewScale}px`,
              minHeight: `${pageDimensions.height * previewScale}px`,
              position: "relative",
            }}
          >
            <TemplateComponent
              content={content}
              scale={previewScale}
              highlightSection={activeSection}
              themeSettings={themeSettings}
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
              {TEMPLATES.find((t) => t.id === templateId)?.name || "Bronzor"}
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
