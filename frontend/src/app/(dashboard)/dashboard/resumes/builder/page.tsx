/**
 * Resume Builder page - Iframe layout with Reactive Resume and ATS score panel.
 *
 * Standards: react_nextjs.mdc
 * - Client component for interactivity
 * - Resizable panels
 * - Always-visible ATS score panel
 * - Reactive Resume in iframe
 */

"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ATSScorePanel } from "@/components/resume-builder";
import { useATSScore } from "@/hooks/useATSScore";
import { useReactiveResumeIframe } from "@/hooks/useReactiveResumeIframe";
import type { ResumeContent } from "@/lib/resume-adapter";
import { resumeContentToApiSchema } from "@/lib/resume-adapter";
import {
  ChevronLeft,
  Loader2,
  AlertCircle,
} from "lucide-react";

const REACTIVE_RESUME_URL = process.env.NEXT_PUBLIC_REACTIVE_RESUME_URL || "http://localhost:3001";

export default function ResumeBuilderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const draftIdFromUrl = searchParams.get("draftId");
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const [resumeContent, setResumeContent] = useState<ResumeContent | null>(null);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [atsBreakdown, setAtsBreakdown] = useState<any>(null);
  const [matchedKeywords, setMatchedKeywords] = useState<string[]>([]);
  const [missingKeywords, setMissingKeywords] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isCalculatingATS, setIsCalculatingATS] = useState(false);

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
    onDraftLoaded: (draftId) => {
      // Update URL if needed
      if (draftId !== draftIdFromUrl) {
        const newUrl = new URL(window.location.href);
        newUrl.searchParams.set("draftId", draftId);
        window.history.replaceState({}, "", newUrl.toString());
      }
    },
    onError: (error) => {
      console.error("Iframe error:", error);
    },
  });

  // ATS scoring hook
  const { result: atsResult, isCalculating, calculate } = useATSScore(
    resumeContent || ({} as ResumeContent),
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
    if (resumeContent && Object.keys(resumeContent).length > 0) {
      setIsCalculatingATS(true);
      calculate().finally(() => {
        setIsCalculatingATS(false);
      });
    }
  }, [resumeContent, calculate]);

  // Load resume data when iframe is ready
  useEffect(() => {
    if (isIframeReady && draftIdFromUrl) {
      getResumeData()
        .then((data) => {
          if (data) {
            setResumeContent(data);
          }
        })
        .catch((error) => {
          console.error("Error loading resume data:", error);
        });
    }
  }, [isIframeReady, draftIdFromUrl, getResumeData]);

  // ATS panel resizable state
  const MIN_ATS_WIDTH = 50;
  const DEFAULT_ATS_WIDTH = 280;
  const MAX_ATS_WIDTH = 700;
  const [atsPanelWidth, setAtsPanelWidth] = useState(DEFAULT_ATS_WIDTH);
  const [isATSPanelResizing, setIsATSPanelResizing] = useState(false);

  // ATS panel resize handler
  const handleATSPanelMouseDown = useCallback(() => {
    setIsATSPanelResizing(true);
  }, []);

  useEffect(() => {
    if (!isATSPanelResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = window.innerWidth - e.clientX;
      const constrainedWidth = Math.min(
        Math.max(newWidth, MIN_ATS_WIDTH),
        MAX_ATS_WIDTH
      );
      setAtsPanelWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsATSPanelResizing(false);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isATSPanelResizing]);

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
          {draftIdFromUrl && (
            <span className="text-sm text-muted-foreground">
              Draft ID: {draftIdFromUrl}
            </span>
          )}
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
      <div className="flex flex-1 overflow-hidden">
        {/* Reactive Resume Iframe */}
        <div
          className="flex-1 overflow-hidden"
          style={{
            width: `calc(100% - ${atsPanelWidth}px - 2px)`,
          }}
        >
          <iframe
            ref={iframeRef}
            src={iframeUrl}
            className="h-full w-full border-0"
            title="Reactive Resume Builder"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
            allow="clipboard-read; clipboard-write"
          />
        </div>

        {/* Resizable Divider */}
        <div
          className="w-0.5 bg-border cursor-col-resize hover:bg-primary/50 transition-colors"
          onMouseDown={handleATSPanelMouseDown}
        />

        {/* ATS Score Panel */}
        <div
          className="border-l bg-background overflow-y-auto"
          style={{ width: `${atsPanelWidth}px` }}
        >
          <ATSScorePanel
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
                }
              } catch (error) {
                console.error("Error recalculating ATS score:", error);
              }
            }}
          />
        </div>
      </div>
    </div>
  );
}
