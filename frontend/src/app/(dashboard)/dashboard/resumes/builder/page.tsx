/**
 * Resume Builder page - Iframe layout with Reactive Resume and ATS score dropdown overlay.
 *
 * Standards: react_nextjs.mdc
 * - Client component for interactivity
 * - ATS score dropdown overlay (collapsed button, expandable panel)
 * - Reactive Resume in iframe (full width)
 */

"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ATSScoreDropdown } from "@/components/resume-builder/ATSScoreDropdown";
import { useATSScore } from "@/hooks/useATSScore";
import { useReactiveResumeIframe } from "@/hooks/useReactiveResumeIframe";
import { useAuth } from "@/providers/AuthProvider";
import type { ResumeContent as ResumeContentAdapter } from "@/lib/resume-adapter";
import type { ResumeContent } from "@/stores/resume-builder-store";
import { resumeContentToApiSchema } from "@/lib/resume-adapter";
import {
  ChevronLeft,
  Loader2,
  AlertCircle,
  Download,
  FileText,
} from "lucide-react";

const REACTIVE_RESUME_URL = process.env.NEXT_PUBLIC_REACTIVE_RESUME_URL || "http://localhost:3002";

const TOKEN_KEY = "ApplyBots_access_token";

export default function ResumeBuilderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { logout } = useAuth();
  const draftIdFromUrl = searchParams.get("draftId");
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const [resumeContent, setResumeContent] = useState<ResumeContentAdapter | null>(null);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [atsBreakdown, setAtsBreakdown] = useState<any>(null);
  const [matchedKeywords, setMatchedKeywords] = useState<string[]>([]);
  const [missingKeywords, setMissingKeywords] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isCalculatingATS, setIsCalculatingATS] = useState(false);
  const [isDraftLoaded, setIsDraftLoaded] = useState(false);
  const [isExportingPDF, setIsExportingPDF] = useState(false);

  // Use Reactive Resume iframe hook
  const {
    isReady: isIframeReady,
    isLoading: isIframeLoading,
    error: iframeError,
    getResumeData,
    loadDraft,
  } = useReactiveResumeIframe({
    iframeRef,
    draftId: draftIdFromUrl,
    onResumeUpdated: async () => {
      // When resume is updated, fetch new data and recalculate ATS score
      try {
        const data = await getResumeData();
        if (data) {
          setResumeContent(data);
        }
      } catch (error) {
        console.error("Error getting resume data after update:", error);
      }
    },
    onDraftLoaded: async (draftId) => {
      // Mark draft as loaded
      setIsDraftLoaded(true);
      
      // Update URL if needed
      if (draftId !== draftIdFromUrl) {
        const newUrl = new URL(window.location.href);
        newUrl.searchParams.set("draftId", draftId);
        window.history.replaceState({}, "", newUrl.toString());
      }
      
      // Now that draft is loaded, fetch the resume data
      try {
        const data = await getResumeData();
        if (data) {
          setResumeContent(data);
        }
      } catch (error) {
        console.error("Error loading resume data after draft loaded:", error);
      }
    },
    onError: (error) => {
      console.error("Iframe error:", error);
    },
    onAuthRequired: () => {
      router.push("/login");
    },
    onLogout: async () => {
      await logout();
    },
  });

  // Convert adapter ResumeContent to store ResumeContent type
  // IMPORTANT: useMemo is required here to prevent infinite render loops
  // Without memoization, a new object reference is created on every render,
  // which causes the useEffect depending on this to trigger repeatedly
  const normalizedResumeContent: ResumeContent | null = useMemo(() => {
    if (!resumeContent) return null;
    return {
      ...resumeContent,
      skills: {
        ...resumeContent.skills,
        custom: resumeContent.skills.custom || [],
        customSkillsHeader: resumeContent.skills.customSkillsHeader || "Custom Skills",
      },
      projects: resumeContent.projects.map((p) => ({
        ...p,
        description: p.description || "",
      })),
      awards: resumeContent.awards.map((a) => ({
        ...a,
        issuer: a.issuer || "",
      })),
      certifications: resumeContent.certifications.map((c) => ({
        ...c,
        issuer: c.issuer || "",
        expiryDate: c.expiryDate ?? null,
      })),
      customSections: resumeContent.customSections.map((cs) => ({
        ...cs,
        items: cs.items.map((item) =>
          typeof item === "string" ? item : item.title || ""
        ),
      })),
      languages: resumeContent.languages.map((l) => ({
        ...l,
        proficiency: (l.proficiency === "native" ||
          l.proficiency === "fluent" ||
          l.proficiency === "conversational" ||
          l.proficiency === "basic"
          ? l.proficiency
          : "conversational") as "native" | "fluent" | "conversational" | "basic",
      })),
      sectionOrder: resumeContent.sectionOrder || [],
      atsScore: resumeContent.atsScore ?? null,
    };
  }, [resumeContent]);

  // Empty resume content for when no content is loaded - memoized to prevent reference changes
  const emptyResumeContent = useMemo(() => ({} as ResumeContent), []);

  // ATS scoring hook
  const { result: atsResult, isCalculating, calculate } = useATSScore(
    normalizedResumeContent || emptyResumeContent,
    {
      debounceMs: 800,
      autoCalculate: false, // We'll trigger manually
    }
  );

  // Update ATS score when result changes
  useEffect(() => {
    if (atsResult) {
      setAtsScore(atsResult.totalScore);
      setAtsBreakdown(atsResult.breakdown);
      setMatchedKeywords(atsResult.matchedKeywords);
      setMissingKeywords(atsResult.missingKeywords);
      setSuggestions(atsResult.suggestions);
    }
  }, [atsResult]);

  // Calculate ATS score when resume content changes
  useEffect(() => {
    if (normalizedResumeContent && Object.keys(normalizedResumeContent).length > 0) {
      setIsCalculatingATS(true);
      calculate().finally(() => {
        setIsCalculatingATS(false);
      });
    }
  }, [normalizedResumeContent, calculate]);

  // NOTE: Resume data is now fetched in onDraftLoaded callback after the draft is loaded.
  // This ensures we don't try to get resume data before the draft has been loaded into the iframe.

  // Export JSON handler
  const handleExportJSON = async () => {
    if (!draftIdFromUrl) return;

    try {
      const data = await getResumeData();
      if (!data) return;

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `resume-${draftIdFromUrl}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export JSON:", error);
    }
  };

  // Export PDF handler
  const handleExportPDF = async () => {
    if (!draftIdFromUrl) return;

    // Get token from localStorage
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      alert("Please log in to export PDF");
      return;
    }

    setIsExportingPDF(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}/api/v1/resume-builder/drafts/${draftIdFromUrl}/export-pdf`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to generate PDF" }));
        throw new Error(error.detail || "Failed to generate PDF");
      }

      const { url } = await response.json();

      // Try to open/download the PDF
      const newWindow = window.open(url, "_blank");

      if (!newWindow || newWindow.closed || typeof newWindow.closed === "undefined") {
        // Popup was blocked - show message with manual link
        alert(
          "Download may have been blocked by your browser.\n\n" +
          "Please allow popups for this site, or use the link that will be copied to your clipboard."
        );
        await navigator.clipboard.writeText(url);
      }
    } catch (error) {
      console.error("Failed to export PDF:", error);
      alert(error instanceof Error ? error.message : "Failed to generate PDF. Please try again.");
    } finally {
      setIsExportingPDF(false);
    }
  };

  // Calculate iframe URL
  const iframeUrl = draftIdFromUrl
    ? `${REACTIVE_RESUME_URL}/builder/${draftIdFromUrl}`
    : `${REACTIVE_RESUME_URL}/builder/new`;

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <div className="flex h-14 items-center justify-between border-b px-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/dashboard/resumes")}
            className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
            Back to Resumes
          </button>

          {/* Divider */}
          <div className="h-6 w-px bg-border" />

          {/* Export JSON Button */}
          <button
            onClick={handleExportJSON}
            disabled={!isIframeReady || !draftIdFromUrl}
            className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Export as JSON"
          >
            <Download className="h-4 w-4" />
            JSON
          </button>

          {/* Export PDF Button */}
          <button
            onClick={handleExportPDF}
            disabled={!isIframeReady || !draftIdFromUrl || isExportingPDF}
            className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Export as PDF"
          >
            {isExportingPDF ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            {isExportingPDF ? "Generating..." : "PDF"}
          </button>
        </div>
        <div className="flex items-center gap-2">
          {isIframeLoading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading...
            </div>
          )}
          {iframeError && (
            <div className="flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" />
              {iframeError}
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Reactive Resume Iframe */}
        <div className="flex-1 overflow-hidden w-full">
          <iframe
            ref={iframeRef}
            src={iframeUrl}
            className="h-full w-full border-0"
            title="Reactive Resume Builder"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
            allow="clipboard-read; clipboard-write"
          />
        </div>

        {/* ATS Score Dropdown Overlay */}
        <ATSScoreDropdown
          totalScore={atsScore}
          breakdown={atsBreakdown}
          matchedKeywords={matchedKeywords}
          missingKeywords={missingKeywords}
          suggestions={suggestions}
          isCalculating={isCalculatingATS || isCalculating}
          onRecalculate={async () => {
            try {
              const data = await getResumeData();
              if (data) {
                setResumeContent(data);
                // Trigger recalculation via the effect that watches normalizedResumeContent
              }
            } catch (error) {
              console.error("Error recalculating ATS score:", error);
            }
          }}
        />
      </div>
    </div>
  );
}
