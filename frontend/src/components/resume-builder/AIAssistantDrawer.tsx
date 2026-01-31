/**
 * AI Assistant drawer for resume optimization and suggestions.
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { X, Sparkles, Target, FileText, Wand2 } from "lucide-react";
import { SummaryMode, SkillsMode, ATSMode } from "./ai-drawer";

type AIMode = "summary" | "skills" | "ats";

const MODE_TABS = [
  { key: "summary" as AIMode, label: "Summary", icon: FileText },
  { key: "skills" as AIMode, label: "Skills", icon: Wand2 },
  { key: "ats" as AIMode, label: "ATS Score", icon: Target },
] as const;

export function AIAssistantDrawer() {
  const isOpen = useResumeBuilderStore((s) => s.isAIDrawerOpen);
  const setOpen = useResumeBuilderStore((s) => s.setAIDrawerOpen);
  const content = useResumeBuilderStore((s) => s.content);
  const updateSummary = useResumeBuilderStore((s) => s.updateSummary);
  const updateSkills = useResumeBuilderStore((s) => s.updateSkills);
  const setATSScore = useResumeBuilderStore((s) => s.setATSScore);

  const [activeMode, setActiveMode] = useState<AIMode>("summary");
  const [isLoading, setIsLoading] = useState(false);
  const [jobDescription, setJobDescription] = useState("");

  // Results state
  const [generatedSummary, setGeneratedSummary] = useState("");
  const [suggestedSkills, setSuggestedSkills] = useState({
    technical: [] as string[],
    soft: [] as string[],
    tools: [] as string[],
  });
  const [atsResult, setATSResult] = useState<{
    score: number;
    suggestions: string[];
    matchedKeywords: string[];
  } | null>(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));

      switch (activeMode) {
        case "summary": {
          const mockSummary = `Results-driven ${content.workExperience[0]?.title || "professional"} with ${content.workExperience.length}+ years of experience in delivering high-impact solutions. Proven track record of ${content.skills.technical.slice(0, 3).join(", ") || "technical excellence"} with a focus on driving business outcomes.`;
          setGeneratedSummary(mockSummary);
          break;
        }
        case "skills":
          setSuggestedSkills({
            technical: ["TypeScript", "GraphQL", "Kubernetes", "CI/CD"],
            soft: ["Strategic Thinking", "Stakeholder Management", "Mentoring"],
            tools: ["Terraform", "DataDog", "Sentry", "Linear"],
          });
          break;
        case "ats": {
          const score = Math.floor(Math.random() * 30) + 70;
          setATSResult({
            score,
            suggestions: [
              "Add more quantified achievements (numbers, percentages)",
              "Include keywords: 'agile', 'cross-functional', 'scalable'",
              "Expand professional summary to 3-5 sentences",
              "Add more technical skills relevant to job description",
            ],
            matchedKeywords: ["leadership", "development", "collaboration"],
          });
          setATSScore(score);
          break;
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplySummary = () => {
    if (generatedSummary) {
      updateSummary(generatedSummary);
      setGeneratedSummary("");
    }
  };

  const handleApplySkills = () => {
    if (suggestedSkills.technical.length > 0) {
      updateSkills({
        technical: [...new Set([...content.skills.technical, ...suggestedSkills.technical])],
        soft: [...new Set([...content.skills.soft, ...suggestedSkills.soft])],
        tools: [...new Set([...content.skills.tools, ...suggestedSkills.tools])],
      });
      setSuggestedSkills({ technical: [], soft: [], tools: [] });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />

      <div className="relative w-full max-w-md bg-white dark:bg-gray-900 shadow-xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 dark:text-white">AI Assistant</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">Enhance your resume with AI</p>
            </div>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Mode selector */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {MODE_TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveMode(key)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
                activeMode === key
                  ? "text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400 bg-purple-50 dark:bg-purple-900/20"
                  : "text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeMode === "summary" && (
            <SummaryMode
              isLoading={isLoading}
              generatedSummary={generatedSummary}
              onGenerate={handleGenerate}
              onApply={handleApplySummary}
            />
          )}
          {activeMode === "skills" && (
            <SkillsMode
              isLoading={isLoading}
              suggestedSkills={suggestedSkills}
              onGenerate={handleGenerate}
              onApply={handleApplySkills}
            />
          )}
          {activeMode === "ats" && (
            <ATSMode
              isLoading={isLoading}
              jobDescription={jobDescription}
              atsResult={atsResult}
              onJobDescriptionChange={setJobDescription}
              onGenerate={handleGenerate}
            />
          )}
        </div>
      </div>
    </div>
  );
}
