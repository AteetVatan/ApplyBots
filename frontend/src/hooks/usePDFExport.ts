/**
 * Hook for PDF export functionality.
 * Provides both ATS-friendly (real text) and Visual (exact match) PDF generation.
 */

"use client";

import React, { useState, useCallback, useRef } from "react";
import { pdf } from "@react-pdf/renderer";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import type { ResumeContent, ThemeSettings } from "@/stores/resume-builder-store";
import { getPDFTemplateComponent } from "@/components/resume-builder/pdf-templates";

interface UsePDFExportOptions {
  content: ResumeContent;
  themeSettings: ThemeSettings;
  templateId: string;
  filename?: string;
}

interface UsePDFExportReturn {
  isGenerating: boolean;
  error: string | null;
  exportType: "ats" | "visual" | null;
  /** Generate ATS-friendly PDF with real selectable text */
  generateATSPDF: () => Promise<void>;
  /** Generate visual PDF that matches preview exactly (image-based) */
  generateVisualPDF: (previewElement: HTMLElement) => Promise<void>;
  /** Clear any error state */
  clearError: () => void;
}

/**
 * Hook for exporting resumes as PDF.
 * Supports two export modes:
 * 1. ATS-friendly: Uses @react-pdf/renderer for real text (parseable by ATS)
 * 2. Visual: Uses html2canvas + jsPDF for exact visual match (image-based)
 */
export function usePDFExport({
  content,
  themeSettings,
  templateId,
  filename,
}: UsePDFExportOptions): UsePDFExportReturn {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportType, setExportType] = useState<"ats" | "visual" | null>(null);
  
  // Abort controller for cancellation
  const abortRef = useRef<AbortController | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const getFilename = useCallback((suffix: string = "") => {
    const baseName = filename || `${content.fullName || "resume"}`;
    const safeName = baseName.replace(/[^a-zA-Z0-9-_]/g, "_");
    return `${safeName}${suffix}.pdf`;
  }, [content.fullName, filename]);

  /**
   * Download blob as file.
   */
  const downloadBlob = useCallback((blob: Blob, downloadFilename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = downloadFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, []);

  /**
   * Generate ATS-friendly PDF using @react-pdf/renderer.
   * The generated PDF has real, selectable, searchable text.
   */
  const generateATSPDF = useCallback(async () => {
    if (isGenerating) return;

    setIsGenerating(true);
    setExportType("ats");
    setError(null);
    abortRef.current = new AbortController();

    try {
      // Get the PDF template component for this template ID
      const PDFTemplate = getPDFTemplateComponent(templateId);

      // Create the PDF document element using React.createElement to avoid SSR issues
      const document = React.createElement(PDFTemplate, {
        content,
        themeSettings,
      });

      // Generate PDF blob
      const blob = await pdf(document).toBlob();

      // Check if cancelled
      if (abortRef.current?.signal.aborted) {
        return;
      }

      // Download the PDF
      downloadBlob(blob, getFilename("_ATS"));
    } catch (err) {
      if (abortRef.current?.signal.aborted) {
        return;
      }
      const message = err instanceof Error ? err.message : "Failed to generate ATS PDF";
      console.error("ATS PDF generation failed:", err);
      setError(message);
    } finally {
      setIsGenerating(false);
      setExportType(null);
      abortRef.current = null;
    }
  }, [content, themeSettings, templateId, isGenerating, downloadBlob, getFilename]);

  /**
   * Generate visual PDF using html2canvas + jsPDF.
   * Captures the HTML preview as an image for exact visual match.
   */
  const generateVisualPDF = useCallback(async (previewElement: HTMLElement) => {
    if (isGenerating) return;

    setIsGenerating(true);
    setExportType("visual");
    setError(null);
    abortRef.current = new AbortController();

    try {
      // Page dimensions in points (72 DPI for PDF)
      const pageWidth = themeSettings.pageSize === "a4" ? 595.28 : 612; // A4 or Letter
      const pageHeight = themeSettings.pageSize === "a4" ? 841.89 : 792;

      // Full page dimensions in PIXELS (96 DPI for screen)
      // Letter: 8.5in × 11in = 816px × 1056px
      // A4: 210mm × 297mm ≈ 794px × 1123px
      const fullPageWidthPx = themeSettings.pageSize === "a4" ? 794 : 816;
      const fullPageHeightPx = themeSettings.pageSize === "a4" ? 1123 : 1056;

      // Capture the preview element as canvas
      // CRITICAL: Must set explicit width - let height be auto to capture full content
      const canvas = await html2canvas(previewElement, {
        scale: 2, // Higher quality
        width: fullPageWidthPx,    // Force full-size canvas width
        // NOTE: Don't set height - let it capture full content for multi-page support
        useCORS: true,
        logging: false,
        backgroundColor: "#ffffff",
        // Reset element styles for proper rendering at full size
        onclone: (_clonedDoc, element) => {
          // 1. Reset wrapper to full page width, let height be auto
          element.style.width = `${fullPageWidthPx}px`;
          element.style.minHeight = `${fullPageHeightPx}px`;
          element.style.height = "auto"; // Allow full content height
          element.style.boxShadow = "none";

          // 2. Reset inner template's transform (templates use transform: scale(previewScale))
          const templateElement = element.firstElementChild as HTMLElement;
          if (templateElement) {
            templateElement.style.transform = "scale(1)";
          }
        },
      });

      // Check if cancelled
      if (abortRef.current?.signal.aborted) {
        return;
      }

      // Create PDF
      const pdfDoc = new jsPDF({
        orientation: "portrait",
        unit: "pt",
        format: themeSettings.pageSize === "a4" ? "a4" : "letter",
      });

      // Scale factor: canvas pixels to PDF points
      // html2canvas scale:2 means canvas is 2x the element size
      const scaleFactor = pageWidth / canvas.width;

      // Simple approach: slice canvas into exact page-height chunks
      const pageSliceHeightPx = Math.round(pageHeight / scaleFactor);
      const totalPages = Math.ceil(canvas.height / pageSliceHeightPx);

      for (let page = 0; page < totalPages; page++) {
        if (page > 0) {
          pdfDoc.addPage();
        }

        // Calculate source position and height for this page
        const sourceY = page * pageSliceHeightPx;
        const sourceHeight = Math.min(pageSliceHeightPx, canvas.height - sourceY);

        // Skip if no content
        if (sourceHeight <= 0) continue;

        // Create temporary canvas for this page slice
        const pageCanvas = document.createElement("canvas");
        pageCanvas.width = canvas.width;
        pageCanvas.height = sourceHeight;
        const ctx = pageCanvas.getContext("2d");
        
        if (ctx) {
          // Draw the slice from source canvas
          ctx.drawImage(
            canvas,
            0, sourceY, canvas.width, sourceHeight,
            0, 0, canvas.width, sourceHeight
          );
          
          // Convert to image and add to PDF
          const pageImgData = pageCanvas.toDataURL("image/png", 1.0);
          const destHeight = sourceHeight * scaleFactor;
          pdfDoc.addImage(pageImgData, "PNG", 0, 0, pageWidth, destHeight);
        }
      }

      // Check if cancelled
      if (abortRef.current?.signal.aborted) {
        return;
      }

      // Download
      const blob = pdfDoc.output("blob");
      downloadBlob(blob, getFilename("_Visual"));
    } catch (err) {
      if (abortRef.current?.signal.aborted) {
        return;
      }
      const message = err instanceof Error ? err.message : "Failed to generate Visual PDF";
      console.error("Visual PDF generation failed:", err);
      setError(message);
    } finally {
      setIsGenerating(false);
      setExportType(null);
      abortRef.current = null;
    }
  }, [themeSettings.pageSize, isGenerating, downloadBlob, getFilename]);

  return {
    isGenerating,
    error,
    exportType,
    generateATSPDF,
    generateVisualPDF,
    clearError,
  };
}
