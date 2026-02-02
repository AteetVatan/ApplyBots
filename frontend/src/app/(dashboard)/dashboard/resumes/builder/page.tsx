/**
 * Resume Builder page - Three-panel layout with editor, preview, and ATS score.
 *
 * Standards: react_nextjs.mdc
 * - Client component for interactivity
 * - Resizable panels
 * - Always-visible ATS score panel
 * - Server-side draft persistence via TanStack Query
 */

"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useResumeBuilderStore, type ResumeContent, type TechnicalSkillGroup } from "@/stores/resume-builder-store";
import {
  EditorPanel,
  PreviewPanel,
  AIAssistantDrawer,
  ATSScorePanel,
  TemplateButton,
  ExportImportButton,
  ShareButton,
} from "@/components/resume-builder";
import { useATSScore } from "@/hooks/useATSScore";
import { useDraft, useCreateDraft, useUpdateDraft } from "@/hooks/useResumeDrafts";
import type { ResumeContentAPI, DraftCreateRequest, DraftUpdateRequest } from "@/lib/api";
import {
  Save,
  Undo2,
  Redo2,
  Sparkles,
  ChevronLeft,
  Cloud,
  CloudOff,
  Loader2,
  PanelRightClose,
  PanelRightOpen,
  Target,
  AlertCircle,
} from "lucide-react";

// =============================================================================
// Data Conversion Utilities (Frontend camelCase <-> Backend snake_case)
// =============================================================================

/**
 * Convert frontend ResumeContent to backend API format
 */
function toAPIFormat(content: ResumeContent): ResumeContentAPI {
  return {
    full_name: content.fullName,
    email: content.email,
    phone: content.phone,
    location: content.location,
    linkedin_url: content.linkedinUrl,
    portfolio_url: content.portfolioUrl,
    github_url: content.githubUrl,
    profile_picture_url: content.profilePictureUrl,
    custom_links: content.customLinks.map((link) => ({
      id: link.id,
      label: link.label,
      url: link.url,
    })),
    professional_summary: content.professionalSummary,
    work_experience: content.workExperience.map((exp) => ({
      company: exp.company,
      title: exp.title,
      start_date: exp.startDate,
      end_date: exp.endDate,
      description: exp.description,
      achievements: exp.achievements,
      location: exp.location,
      is_current: exp.isCurrent,
    })),
    education: content.education.map((edu) => ({
      institution: edu.institution,
      degree: edu.degree,
      field_of_study: edu.fieldOfStudy,
      graduation_date: edu.graduationDate,
      gpa: edu.gpa,
      location: edu.location,
      achievements: edu.achievements,
    })),
    skills: {
      // Flatten technical skill groups to flat array for backend
      technical: content.skills.technical.flatMap((group: TechnicalSkillGroup) => group.items),
      soft: content.skills.soft,
      tools: content.skills.tools,
    },
    projects: content.projects.map((proj) => ({
      name: proj.name,
      description: proj.description,
      url: proj.url,
      technologies: proj.technologies,
      start_date: proj.startDate,
      end_date: proj.endDate,
      highlights: proj.highlights,
    })),
    certifications: content.certifications.map((cert) => ({
      name: cert.name,
      issuer: cert.issuer,
      date: cert.date,
      expiry_date: cert.expiryDate,
      credential_id: cert.credentialId,
      url: cert.url,
    })),
    awards: content.awards.map((award) => ({
      title: award.title,
      issuer: award.issuer,
      date: award.date,
      description: award.description,
    })),
    languages: content.languages.map((lang) => ({
      language: lang.language,
      proficiency: lang.proficiency,
    })),
    custom_sections: content.customSections.map((section) => ({
      id: section.id,
      title: section.title,
      items: section.items,
    })),
    template_id: content.templateId,
    section_order: content.sectionOrder,
    ats_score: content.atsScore,
  };
}

/**
 * Convert backend API format to frontend ResumeContent
 */
function fromAPIFormat(api: ResumeContentAPI): ResumeContent {
  return {
    fullName: api.full_name,
    email: api.email,
    phone: api.phone ?? null,
    location: api.location ?? null,
    linkedinUrl: api.linkedin_url ?? null,
    portfolioUrl: api.portfolio_url ?? null,
    githubUrl: api.github_url ?? null,
    profilePictureUrl: api.profile_picture_url ?? null,
    customLinks: (api.custom_links || []).map((link) => ({
      id: link.id,
      label: link.label,
      url: link.url,
    })),
    professionalSummary: api.professional_summary ?? null,
    workExperience: (api.work_experience || []).map((exp) => ({
      id: crypto.randomUUID(),
      company: exp.company,
      title: exp.title,
      startDate: exp.start_date ?? null,
      endDate: exp.end_date ?? null,
      description: exp.description ?? null,
      achievements: exp.achievements || [],
      location: exp.location ?? null,
      isCurrent: exp.is_current || false,
    })),
    education: (api.education || []).map((edu) => ({
      id: crypto.randomUUID(),
      institution: edu.institution,
      degree: edu.degree,
      fieldOfStudy: edu.field_of_study ?? null,
      graduationDate: edu.graduation_date ?? null,
      gpa: edu.gpa ?? null,
      location: edu.location ?? null,
      achievements: edu.achievements || [],
    })),
    skills: {
      // Convert flat array back to grouped format
      technical: api.skills?.technical?.length
        ? [{ id: crypto.randomUUID(), header: "Technical Skills", items: api.skills.technical }]
        : [],
      soft: api.skills?.soft || [],
      tools: api.skills?.tools || [],
      custom: [],
      customSkillsHeader: "Custom Skills",
    },
    projects: (api.projects || []).map((proj) => ({
      id: crypto.randomUUID(),
      name: proj.name,
      description: proj.description,
      url: proj.url ?? null,
      technologies: proj.technologies || [],
      startDate: proj.start_date ?? null,
      endDate: proj.end_date ?? null,
      highlights: proj.highlights || [],
    })),
    certifications: (api.certifications || []).map((cert) => ({
      id: crypto.randomUUID(),
      name: cert.name,
      issuer: cert.issuer,
      date: cert.date ?? null,
      expiryDate: cert.expiry_date ?? null,
      credentialId: cert.credential_id ?? null,
      url: cert.url ?? null,
    })),
    awards: (api.awards || []).map((award) => ({
      id: crypto.randomUUID(),
      title: award.title,
      issuer: award.issuer,
      date: award.date ?? null,
      description: award.description ?? null,
    })),
    languages: (api.languages || []).map((lang) => ({
      id: crypto.randomUUID(),
      language: lang.language,
      proficiency: lang.proficiency,
    })),
    customSections: (api.custom_sections || []).map((section) => ({
      id: section.id,
      title: section.title,
      items: section.items || [],
    })),
    templateId: api.template_id || "bronzor",
    sectionOrder: api.section_order || [],
    atsScore: api.ats_score ?? null,
  };
}

export default function ResumeBuilderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const draftIdFromUrl = searchParams.get("draftId");

  const {
    content,
    draftId,
    draftName,
    setDraftId,
    setDraftName,
    isDirty,
    isSaving,
    lastSaved,
    setSaving,
    markSaved,
    loadDraft,
    templateId,
    undo,
    redo,
    canUndo,
    canRedo,
    setAIDrawerOpen,
    isATSPanelVisible,
    setATSPanelVisible,
    detailedAtsScore,
    setDetailedATSScore,
    atsScore,
  } = useResumeBuilderStore();

  // Track if we've loaded the draft from URL
  const hasLoadedFromUrl = useRef(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Fetch draft from server if draftId is in URL
  const { data: serverDraft, isLoading: isLoadingDraft, error: loadError } = useDraft(draftIdFromUrl);

  // Mutations for creating and updating drafts
  const createDraftMutation = useCreateDraft();
  const updateDraftMutation = useUpdateDraft();

  // Load draft from server when data arrives
  useEffect(() => {
    if (serverDraft && !hasLoadedFromUrl.current) {
      hasLoadedFromUrl.current = true;
      const convertedContent = fromAPIFormat(serverDraft.content);
      loadDraft({
        id: serverDraft.id,
        name: serverDraft.name,
        content: convertedContent,
        templateId: serverDraft.template_id,
        atsScore: serverDraft.ats_score,
      });
    }
  }, [serverDraft, loadDraft]);

  // Sync draftId from URL if store doesn't have it
  useEffect(() => {
    if (draftIdFromUrl && !draftId && !isLoadingDraft) {
      setDraftId(draftIdFromUrl);
    }
  }, [draftIdFromUrl, draftId, isLoadingDraft, setDraftId]);

  // Real-time ATS score calculation
  const { result: atsResult, isCalculating, calculate } = useATSScore(content, {
    debounceMs: 800,
    autoCalculate: true,
    jobDescription: detailedAtsScore.jobDescription,
  });

  // Update store when ATS result changes
  useEffect(() => {
    if (atsResult) {
      setDetailedATSScore({
        total: atsResult.totalScore,
        breakdown: atsResult.breakdown,
        matchedKeywords: atsResult.matchedKeywords,
        missingKeywords: atsResult.missingKeywords,
        suggestions: atsResult.suggestions,
        isCalculating: false,
      });
    }
  }, [atsResult, setDetailedATSScore]);

  // Resizable panel state
  const [leftPanelWidth, setLeftPanelWidth] = useState(40);
  const [isResizing, setIsResizing] = useState(false);

  // ATS panel resizable state
  const MIN_ATS_WIDTH = 50; // Icon-only minimized state
  const DEFAULT_ATS_WIDTH = 280;
  const MAX_ATS_WIDTH = 700; // Maximum width when maximized
  const [atsPanelWidth, setAtsPanelWidth] = useState(DEFAULT_ATS_WIDTH);
  const [isATSPanelResizing, setIsATSPanelResizing] = useState(false);

  // Calculate maximum ATS panel width (constrained to MAX_ATS_WIDTH)
  const calculateMaxATSPanelWidth = useCallback(() => {
    const leftPanelPx = (window.innerWidth * leftPanelWidth) / 100;
    const dividerWidth = 2; // 2px for dividers
    // Calculate available width but cap at MAX_ATS_WIDTH
    const availableWidth = window.innerWidth - leftPanelPx - dividerWidth;
    return Math.min(availableWidth, MAX_ATS_WIDTH);
  }, [leftPanelWidth]);

  /**
   * Save draft to server - creates new or updates existing
   */
  const saveDraft = useCallback(async () => {
    setSaving(true);
    setSaveError(null);

    try {
      const apiContent = toAPIFormat(content);

      if (draftId) {
        // Update existing draft
        const updateData: DraftUpdateRequest = {
          name: draftName,
          content: apiContent,
          template_id: templateId,
        };
        await updateDraftMutation.mutateAsync({ id: draftId, data: updateData });
      } else {
        // Create new draft
        const createData: DraftCreateRequest = {
          name: draftName || "Untitled Resume",
          content: apiContent,
          template_id: templateId,
        };
        const newDraft = await createDraftMutation.mutateAsync(createData);
        
        // Update store with new draft ID
        setDraftId(newDraft.id);
        
        // Update URL with new draft ID (without full page reload)
        const newUrl = new URL(window.location.href);
        newUrl.searchParams.set("draftId", newDraft.id);
        window.history.replaceState({}, "", newUrl.toString());
      }

      markSaved();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to save draft";
      setSaveError(message);
      console.error("Failed to save draft:", error);
    } finally {
      setSaving(false);
    }
  }, [content, draftId, draftName, templateId, createDraftMutation, updateDraftMutation, setDraftId, markSaved, setSaving]);

  // Autosave effect - calls real API
  useEffect(() => {
    if (!isDirty) return;
    // Don't autosave while loading initial draft
    if (isLoadingDraft) return;

    const timer = setTimeout(() => {
      saveDraft();
    }, 2000);

    return () => clearTimeout(timer);
  }, [isDirty, isLoadingDraft, saveDraft]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case "z":
            e.preventDefault();
            if (e.shiftKey) {
              redo();
            } else {
              undo();
            }
            break;
          case "y":
            e.preventDefault();
            redo();
            break;
          case "s":
            e.preventDefault();
            // Trigger save
            break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [undo, redo]);

  // Left panel resize handler
  const handleLeftPanelMouseDown = useCallback(() => {
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      // Calculate available width excluding ATS panel and dividers
      const atsWidth = isATSPanelVisible ? atsPanelWidth : 0;
      const containerWidth = window.innerWidth - atsWidth - 2; // 2px for dividers
      const newWidth = (e.clientX / containerWidth) * 100;
      setLeftPanelWidth(Math.min(Math.max(newWidth, 25), 60));
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing, isATSPanelVisible, atsPanelWidth]);

  // ATS panel resize handler
  const handleATSPanelMouseDown = useCallback(() => {
    setIsATSPanelResizing(true);
  }, []);

  useEffect(() => {
    if (!isATSPanelResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      // Calculate maximum width: full CV/preview panel width
      const maxWidth = calculateMaxATSPanelWidth();
      
      // Calculate new width from right edge
      const newWidth = window.innerWidth - e.clientX;
      
      // Constrain between min and max (leave at least 100px for preview)
      const previewMinWidth = 100;
      const constrainedMaxWidth = Math.max(maxWidth - previewMinWidth, MIN_ATS_WIDTH);
      const constrainedWidth = Math.min(
        Math.max(newWidth, MIN_ATS_WIDTH),
        constrainedMaxWidth
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
  }, [isATSPanelResizing, calculateMaxATSPanelWidth]);

  // Format last saved time
  const formatLastSaved = () => {
    if (!lastSaved) return null;
    const now = new Date();
    const diff = now.getTime() - lastSaved.getTime();
    if (diff < 60000) return "Saved just now";
    if (diff < 3600000) return `Saved ${Math.floor(diff / 60000)}m ago`;
    return `Saved ${lastSaved.toLocaleTimeString()}`;
  };

  // ATS score color
  const getATSScoreColor = (score: number | null) => {
    if (score === null) return "text-gray-400";
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Top toolbar */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Left: Back + Name */}
        <div className="flex items-center gap-3 flex-shrink-0 min-w-0">
          <button
            onClick={() => router.push("/dashboard/resumes")}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            title="Back to resumes"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>

          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />

          <input
            type="text"
            value={draftName}
            onChange={(e) => setDraftName(e.target.value)}
            className="text-lg font-semibold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 text-gray-900 dark:text-white min-w-0 max-w-[200px] truncate"
            placeholder="Untitled Resume"
          />

          {/* Save status */}
          <div className="flex items-center gap-1.5 text-sm">
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
                <span className="text-gray-500 dark:text-gray-400">Saving...</span>
              </>
            ) : isDirty ? (
              <>
                <CloudOff className="h-4 w-4 text-amber-500" />
                <span className="text-amber-600 dark:text-amber-400">Unsaved</span>
              </>
            ) : lastSaved ? (
              <>
                <Cloud className="h-4 w-4 text-green-500" />
                <span className="text-gray-500 dark:text-gray-400">{formatLastSaved()}</span>
              </>
            ) : null}
          </div>
        </div>

        {/* Center: Undo/Redo + Template + ATS indicator */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={undo}
            disabled={!canUndo()}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed"
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="h-4 w-4" />
          </button>
          <button
            onClick={redo}
            disabled={!canRedo()}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed"
            title="Redo (Ctrl+Y)"
          >
            <Redo2 className="h-4 w-4" />
          </button>

          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-1" />

          <TemplateButton />

          <ExportImportButton />

          <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-1" />

          {/* ATS Score indicator (compact) */}
          <button
            onClick={() => {
              if (!isATSPanelVisible) {
                // Show and maximize to MAX_ATS_WIDTH
                setATSPanelVisible(true);
                setAtsPanelWidth(MAX_ATS_WIDTH);
              } else if (atsPanelWidth <= MIN_ATS_WIDTH) {
                // If minimized, expand to maximum width
                setAtsPanelWidth(MAX_ATS_WIDTH);
              } else {
                // If expanded, minimize
                setAtsPanelWidth(MIN_ATS_WIDTH);
              }
            }}
            onDoubleClick={(e) => {
              // Double-click to hide completely
              if (isATSPanelVisible) {
                e.preventDefault();
                setATSPanelVisible(false);
                setAtsPanelWidth(DEFAULT_ATS_WIDTH); // Reset for next time
              }
            }}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-colors ${isATSPanelVisible
                ? "border-blue-300 bg-blue-50 dark:bg-blue-900/20"
                : "border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}
            title={
              !isATSPanelVisible
                ? "Show ATS panel (double-click to toggle)"
                : atsPanelWidth <= MIN_ATS_WIDTH
                ? "Expand ATS panel (double-click to hide)"
                : "Minimize ATS panel (double-click to hide)"
            }
          >
            <Target className={`h-4 w-4 ${getATSScoreColor(detailedAtsScore.total)}`} />
            <span className={`text-sm font-medium ${getATSScoreColor(detailedAtsScore.total)}`}>
              {isCalculating ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                `${detailedAtsScore.total || "--"}%`
              )}
            </span>
            {isATSPanelVisible ? (
              <PanelRightClose className="h-4 w-4 text-gray-400" />
            ) : (
              <PanelRightOpen className="h-4 w-4 text-gray-400" />
            )}
          </button>
        </div>

        {/* Right: Share + AI + Save */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <ShareButton />

          <button
            onClick={() => setAIDrawerOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all"
          >
            <Sparkles className="h-4 w-4" />
            AI Assistant
          </button>

          <button
            onClick={saveDraft}
            disabled={(!isDirty && !!draftId) || isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {isSaving ? "Saving..." : "Save"}
          </button>
        </div>
      </header>

      {/* Save Error Banner */}
      {saveError && (
        <div className="flex-shrink-0 flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-700 dark:text-red-300">{saveError}</span>
          <button
            onClick={() => setSaveError(null)}
            className="ml-auto text-sm text-red-600 dark:text-red-400 hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Loading state when fetching draft from server */}
      {isLoadingDraft && draftIdFromUrl && (
        <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-950">
          <div className="text-center">
            <Loader2 className="h-8 w-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-gray-600 dark:text-gray-400">Loading your resume...</p>
          </div>
        </div>
      )}

      {/* Load error state */}
      {loadError && draftIdFromUrl && (
        <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-950">
          <div className="text-center max-w-md">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Failed to load resume
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {loadError instanceof Error ? loadError.message : "An error occurred while loading your resume."}
            </p>
            <button
              onClick={() => router.push("/dashboard/resumes")}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Back to Resumes
            </button>
          </div>
        </div>
      )}

      {/* Main content - Three panels */}
      {(!isLoadingDraft || !draftIdFromUrl) && !loadError && (
      <div className="flex-1 flex overflow-hidden">
        {/* Editor Panel */}
        <div
          className="flex-shrink-0 overflow-hidden"
          style={{ width: `${leftPanelWidth}%` }}
        >
          <EditorPanel />
        </div>

        {/* Resizable divider between editor and preview */}
        <div
          className={`w-1 bg-gray-200 dark:bg-gray-700 cursor-col-resize hover:bg-blue-500 transition-colors ${isResizing ? "bg-blue-500" : ""
            }`}
          onMouseDown={handleLeftPanelMouseDown}
        />

        {/* Preview Panel */}
        <div className="flex-1 overflow-hidden min-w-0">
          <PreviewPanel />
        </div>

        {/* ATS Score Panel (resizable) */}
        {isATSPanelVisible && (
          <>
            {/* Resizable divider between preview and ATS panel */}
            <div
              className={`w-1 bg-gray-200 dark:bg-gray-700 cursor-col-resize hover:bg-blue-500 transition-colors ${isATSPanelResizing ? "bg-blue-500" : ""
                }`}
              onMouseDown={handleATSPanelMouseDown}
            />
            <div
              className="flex-shrink-0 overflow-hidden transition-all duration-300 h-full flex flex-col"
              style={{ width: `${atsPanelWidth}px`, maxWidth: `${atsPanelWidth}px`, maxHeight: "100%" }}
              ref={(el) => {
                // #region agent log
                if (el) {
                  setTimeout(() => {
                    const actualWidth = el.offsetWidth;
                    const scrollWidth = el.scrollWidth;
                    const computedStyle = window.getComputedStyle(el);
                    fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:418',message:'ATS panel parent container measurements',data:{atsPanelWidth,actualWidth,scrollWidth,isOverflowing:scrollWidth>actualWidth,boxSizing:computedStyle.boxSizing,paddingLeft:computedStyle.paddingLeft,paddingRight:computedStyle.paddingRight},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,D'})}).catch(()=>{});
                  }, 100);
                }
                // #endregion
              }}
            >
              <ATSScorePanel
                totalScore={detailedAtsScore.total || null}
                breakdown={detailedAtsScore.total ? detailedAtsScore.breakdown : null}
                matchedKeywords={detailedAtsScore.matchedKeywords}
                missingKeywords={detailedAtsScore.missingKeywords}
                suggestions={detailedAtsScore.suggestions}
                isCalculating={isCalculating}
                onRecalculate={calculate}
                isMinimized={atsPanelWidth <= MIN_ATS_WIDTH}
                onExpand={() => {
                  setAtsPanelWidth(MAX_ATS_WIDTH);
                }}
              />
            </div>
          </>
        )}
      </div>
      )}

      {/* AI Assistant Drawer */}
      <AIAssistantDrawer />
    </div>
  );
}
