/**
 * Professional summary section editor with AI assistance and rich text editing.
 */

"use client";

import { useState, lazy, Suspense } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { Sparkles, Loader2, Type, AlignLeft } from "lucide-react";

// Lazy load RichTextEditor to avoid SSR issues with Tiptap
const RichTextEditor = lazy(() =>
  import("../RichTextEditor").then((mod) => ({ default: mod.RichTextEditor }))
);

export function SummarySection() {
  const content = useResumeBuilderStore((s) => s.content);
  const updateSummary = useResumeBuilderStore((s) => s.updateSummary);
  const setAIDrawerOpen = useResumeBuilderStore((s) => s.setAIDrawerOpen);
  const [isGenerating, setIsGenerating] = useState(false);
  const [useRichText, setUseRichText] = useState(true);

  const handleAIGenerate = async () => {
    setIsGenerating(true);
    try {
      // This would call the API in production
      // For now, just open the AI drawer
      setAIDrawerOpen(true);
    } finally {
      setIsGenerating(false);
    }
  };

  // Strip HTML tags for character count
  const plainTextLength = (content.professionalSummary || "")
    .replace(/<[^>]*>/g, "")
    .length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Professional Summary
        </h3>
        <div className="flex items-center gap-2">
          {/* Rich text toggle */}
          <button
            onClick={() => setUseRichText(!useRichText)}
            className={`flex items-center gap-1.5 px-2 py-1 text-xs rounded-lg border transition-colors ${
              useRichText
                ? "border-blue-300 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                : "border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}
            title={useRichText ? "Switch to plain text" : "Switch to rich text"}
          >
            {useRichText ? (
              <>
                <Type className="h-3.5 w-3.5" />
                Rich
              </>
            ) : (
              <>
                <AlignLeft className="h-3.5 w-3.5" />
                Plain
              </>
            )}
          </button>
          
          <button
            onClick={handleAIGenerate}
            disabled={isGenerating}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 transition-all"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            AI Generate
          </button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Write a compelling 3-5 sentence summary of your professional background
        </label>
        
        {useRichText ? (
          <Suspense
            fallback={
              <div className="h-40 flex items-center justify-center border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-800">
                <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
              </div>
            }
          >
            <RichTextEditor
              content={content.professionalSummary || ""}
              onChange={(html) => updateSummary(html || null)}
              placeholder="Experienced software engineer with 5+ years of expertise..."
              minHeight="120px"
            />
          </Suspense>
        ) : (
          <textarea
            value={content.professionalSummary || ""}
            onChange={(e) => updateSummary(e.target.value || null)}
            placeholder="Experienced software engineer with 5+ years of expertise in building scalable web applications. Proficient in React, Node.js, and cloud technologies. Passionate about clean code and delivering exceptional user experiences..."
            rows={5}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
        )}
        
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            Tip: Highlight your key achievements and years of experience
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {plainTextLength} / 500 characters
          </span>
        </div>
      </div>

      {/* Writing tips */}
      <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
        <h4 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
          Writing Tips
        </h4>
        <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
          <li>• Start with your years of experience and primary expertise</li>
          <li>• Mention 2-3 key achievements or capabilities</li>
          <li>• Include relevant technical skills naturally</li>
          <li>• Tailor it to the type of role you're seeking</li>
        </ul>
      </div>
    </div>
  );
}
