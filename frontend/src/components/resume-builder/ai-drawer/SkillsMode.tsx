/**
 * AI Assistant Skills suggestions mode.
 */

"use client";

import { Lightbulb, Loader2, CheckCircle2 } from "lucide-react";

interface SuggestedSkills {
  technical: string[];
  soft: string[];
  tools: string[];
}

interface SkillsModeProps {
  isLoading: boolean;
  suggestedSkills: SuggestedSkills;
  onGenerate: () => void;
  onApply: () => void;
}

function SkillBadge({ skill, color }: { skill: string; color: "blue" | "purple" | "emerald" }) {
  const colorClasses = {
    blue: "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300",
    purple: "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300",
    emerald: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300",
  };

  return (
    <span className={`px-2 py-1 ${colorClasses[color]} text-xs rounded`}>
      {skill}
    </span>
  );
}

export function SkillsMode({
  isLoading,
  suggestedSkills,
  onGenerate,
  onApply,
}: SkillsModeProps) {
  const hasSkills =
    suggestedSkills.technical.length > 0 ||
    suggestedSkills.soft.length > 0 ||
    suggestedSkills.tools.length > 0;

  return (
    <div className="space-y-4">
      <div className="p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
        <h3 className="font-medium text-emerald-800 dark:text-emerald-300 mb-1">
          AI Skill Suggestions
        </h3>
        <p className="text-sm text-emerald-600 dark:text-emerald-400">
          Get recommendations for skills to add based on your experience.
        </p>
      </div>

      <button
        onClick={onGenerate}
        disabled={isLoading}
        className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg hover:from-emerald-600 hover:to-teal-600 disabled:opacity-50"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Lightbulb className="h-4 w-4" />
            Suggest Skills
          </>
        )}
      </button>

      {hasSkills && (
        <div className="space-y-3">
          {suggestedSkills.technical.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                Technical Skills
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {suggestedSkills.technical.map((skill) => (
                  <SkillBadge key={skill} skill={skill} color="blue" />
                ))}
              </div>
            </div>
          )}
          {suggestedSkills.soft.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                Soft Skills
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {suggestedSkills.soft.map((skill) => (
                  <SkillBadge key={skill} skill={skill} color="purple" />
                ))}
              </div>
            </div>
          )}
          {suggestedSkills.tools.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                Tools
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {suggestedSkills.tools.map((skill) => (
                  <SkillBadge key={skill} skill={skill} color="emerald" />
                ))}
              </div>
            </div>
          )}
          <button
            onClick={onApply}
            className="w-full flex items-center justify-center gap-2 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            <CheckCircle2 className="h-4 w-4" />
            Add All Skills
          </button>
        </div>
      )}
    </div>
  );
}
