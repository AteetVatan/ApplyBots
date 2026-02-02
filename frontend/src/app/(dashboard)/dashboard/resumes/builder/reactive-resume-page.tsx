/**
 * Resume Builder page with Reactive Resume integration.
 * 
 * This is the new version that will replace the current builder page
 * once Reactive Resume is forked and integrated.
 * 
 * Standards: react_nextjs.mdc
 * - Client component for interactivity
 * - Integrates Reactive Resume with our backend
 * - Maintains ATS scoring panel
 */

"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ReactiveResumeBuilder, getReactiveResumeData } from "@/components/reactive-resume/ReactiveResumeBuilder";
import { ATSScorePanel } from "@/components/resume-builder/ATSScorePanel";
import { useReactiveResumeATSScore } from "@/hooks/useReactiveResumeATSScore";
import { PanelRightClose, PanelRightOpen } from "lucide-react";

export default function ReactiveResumeBuilderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const draftIdFromUrl = searchParams.get("draftId");

  // ATS Panel state
  const [isATSPanelVisible, setATSPanelVisible] = useState(true);
  const [atsPanelWidth, setAtsPanelWidth] = useState(280);
  const [isATSPanelResizing, setIsATSPanelResizing] = useState(false);
  const [jobDescription, setJobDescription] = useState("");

  // ATS Scoring with Reactive Resume data
  const {
    result: atsResult,
    isCalculating: isATSCalculating,
    error: atsError,
    calculate: calculateATS,
    setJobDescription: setATSJobDescription,
  } = useReactiveResumeATSScore({
    getResumeData: getReactiveResumeData,
    jobDescription,
    debounceMs: 800,
    autoCalculate: true,
  });

  // Update job description in ATS hook when it changes
  useEffect(() => {
    setATSJobDescription(jobDescription);
  }, [jobDescription, setATSJobDescription]);

  // Handle ATS panel resize
  const handleATSPanelMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsATSPanelResizing(true);
  }, []);

  useEffect(() => {
    if (!isATSPanelResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = window.innerWidth - e.clientX;
      const minWidth = 50;
      const maxWidth = 700;
      setAtsPanelWidth(Math.max(minWidth, Math.min(maxWidth, newWidth)));
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

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Content: Reactive Resume Builder */}
      <div
        className="flex-1 overflow-hidden"
        style={{
          marginRight: isATSPanelVisible ? `${atsPanelWidth}px` : "0",
        }}
      >
        <ReactiveResumeBuilder
          draftId={draftIdFromUrl}
          onDraftIdChange={(newDraftId) => {
            // Update URL with new draft ID
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set("draftId", newDraftId);
            router.replace(newUrl.toString());
          }}
        />
      </div>

      {/* ATS Score Panel */}
      {isATSPanelVisible && (
        <>
          {/* Resize Handle */}
          <div
            className="w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize transition-colors"
            onMouseDown={handleATSPanelMouseDown}
            style={{ minWidth: "4px" }}
          />

          {/* ATS Panel */}
          <div
            className="bg-white border-l shadow-lg overflow-hidden flex flex-col"
            style={{ width: `${atsPanelWidth}px` }}
          >
            <ATSScorePanel
              totalScore={atsResult?.totalScore || null}
              breakdown={atsResult?.breakdown || null}
              matchedKeywords={atsResult?.matchedKeywords || []}
              missingKeywords={atsResult?.missingKeywords || []}
              suggestions={atsResult?.suggestions || []}
              isCalculating={isATSCalculating}
              onRecalculate={calculateATS}
            />
          </div>
        </>
      )}

      {/* Toggle ATS Panel Button */}
      <button
        onClick={() => setATSPanelVisible(!isATSPanelVisible)}
        className="fixed right-0 top-1/2 -translate-y-1/2 z-10 bg-blue-600 text-white p-2 rounded-l-lg shadow-lg hover:bg-blue-700 transition-colors"
        style={{
          right: isATSPanelVisible ? `${atsPanelWidth}px` : "0",
        }}
        aria-label={isATSPanelVisible ? "Hide ATS Panel" : "Show ATS Panel"}
      >
        {isATSPanelVisible ? (
          <PanelRightClose className="w-5 h-5" />
        ) : (
          <PanelRightOpen className="w-5 h-5" />
        )}
      </button>
    </div>
  );
}
