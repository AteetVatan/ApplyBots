/**
 * Resume Builder page - Two-panel layout with form editor and live preview.
 *
 * Standards: react_nextjs.mdc
 * - Client component for interactivity
 * - Resizable panels
 */

"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import {
  EditorPanel,
  PreviewPanel,
  AIAssistantDrawer,
  TemplateButton,
} from "@/components/resume-builder";
import {
  Save,
  Undo2,
  Redo2,
  Sparkles,
  ChevronLeft,
  Cloud,
  CloudOff,
  Loader2,
} from "lucide-react";

export default function ResumeBuilderPage() {
  const router = useRouter();
  const {
    draftName,
    setDraftName,
    isDirty,
    isSaving,
    lastSaved,
    setSaving,
    markSaved,
    undo,
    redo,
    canUndo,
    canRedo,
    setAIDrawerOpen,
    reset,
  } = useResumeBuilderStore();

  // Resizable panel state
  const [leftPanelWidth, setLeftPanelWidth] = useState(45);
  const [isResizing, setIsResizing] = useState(false);

  // Autosave effect
  useEffect(() => {
    if (!isDirty) return;

    const timer = setTimeout(async () => {
      // Mock save - in production, call API
      setSaving(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      markSaved();
      setSaving(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, [isDirty, setSaving, markSaved]);

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

  // Resize handler
  const handleMouseDown = useCallback(() => {
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = (e.clientX / window.innerWidth) * 100;
      setLeftPanelWidth(Math.min(Math.max(newWidth, 30), 70));
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
  }, [isResizing]);

  // Format last saved time
  const formatLastSaved = () => {
    if (!lastSaved) return null;
    const now = new Date();
    const diff = now.getTime() - lastSaved.getTime();
    if (diff < 60000) return "Saved just now";
    if (diff < 3600000) return `Saved ${Math.floor(diff / 60000)}m ago`;
    return `Saved ${lastSaved.toLocaleTimeString()}`;
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Top toolbar */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        {/* Left: Back + Name */}
        <div className="flex items-center gap-3">
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
            className="text-lg font-semibold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 text-gray-900 dark:text-white"
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

        {/* Center: Undo/Redo + Template */}
        <div className="flex items-center gap-2">
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
        </div>

        {/* Right: AI + Save */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAIDrawerOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all"
          >
            <Sparkles className="h-4 w-4" />
            AI Assistant
          </button>

          <button
            onClick={() => {
              // Manual save
              setSaving(true);
              setTimeout(() => {
                markSaved();
                setSaving(false);
              }, 500);
            }}
            disabled={!isDirty || isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="h-4 w-4" />
            Save
          </button>
        </div>
      </header>

      {/* Main content - Two panels */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor Panel */}
        <div
          className="flex-shrink-0 overflow-hidden"
          style={{ width: `${leftPanelWidth}%` }}
        >
          <EditorPanel />
        </div>

        {/* Resizable divider */}
        <div
          className={`w-1 bg-gray-200 dark:bg-gray-700 cursor-col-resize hover:bg-blue-500 transition-colors ${
            isResizing ? "bg-blue-500" : ""
          }`}
          onMouseDown={handleMouseDown}
        />

        {/* Preview Panel */}
        <div className="flex-1 overflow-hidden">
          <PreviewPanel />
        </div>
      </div>

      {/* AI Assistant Drawer */}
      <AIAssistantDrawer />
    </div>
  );
}
