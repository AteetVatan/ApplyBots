/**
 * Work experience section editor with drag-drop reordering.
 */

"use client";

import { useState, lazy, Suspense } from "react";
import { useResumeBuilderStore, type WorkExperience } from "@/stores/resume-builder-store";
import {
  Plus,
  Trash2,
  GripVertical,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Building2,
  Loader2,
} from "lucide-react";

// Lazy load RichTextEditor to avoid SSR issues with Tiptap
const RichTextEditor = lazy(() =>
  import("../RichTextEditor").then((mod) => ({ default: mod.RichTextEditor }))
);

interface ExperienceCardProps {
  experience: WorkExperience;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

function ExperienceCard({ experience, index, isExpanded, onToggle }: ExperienceCardProps) {
  const updateWorkExperience = useResumeBuilderStore((s) => s.updateWorkExperience);
  const removeWorkExperience = useResumeBuilderStore((s) => s.removeWorkExperience);
  const [newAchievement, setNewAchievement] = useState("");

  const handleAddAchievement = () => {
    // Strip HTML tags for empty check, but store as HTML
    const plainText = newAchievement.replace(/<[^>]*>/g, "").trim();
    if (plainText) {
      updateWorkExperience(experience.id, {
        achievements: [...experience.achievements, newAchievement.trim()],
      });
      setNewAchievement("");
    }
  };

  const handleRemoveAchievement = (achIndex: number) => {
    updateWorkExperience(experience.id, {
      achievements: experience.achievements.filter((_, i) => i !== achIndex),
    });
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 overflow-hidden">
      {/* Header - Always visible */}
      <div
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750"
        onClick={onToggle}
      >
        <button className="cursor-grab text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
          <GripVertical className="h-5 w-5" />
        </button>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-900 dark:text-white truncate">
            {experience.title || "New Position"}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
            {experience.company || "Company Name"} •{" "}
            {experience.startDate || "Start"} - {experience.isCurrent ? "Present" : experience.endDate || "End"}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            removeWorkExperience(experience.id);
          }}
          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
        >
          <Trash2 className="h-4 w-4" />
        </button>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
          {/* Job Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Job Title *
            </label>
            <input
              type="text"
              value={experience.title}
              onChange={(e) => updateWorkExperience(experience.id, { title: e.target.value })}
              placeholder="Software Engineer"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Company */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Company *
            </label>
            <input
              type="text"
              value={experience.company}
              onChange={(e) => updateWorkExperience(experience.id, { company: e.target.value })}
              placeholder="Acme Inc."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Location
            </label>
            <input
              type="text"
              value={experience.location || ""}
              onChange={(e) => updateWorkExperience(experience.id, { location: e.target.value || null })}
              placeholder="San Francisco, CA (or Remote)"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Date range */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Date
              </label>
              <input
                type="text"
                value={experience.startDate || ""}
                onChange={(e) => updateWorkExperience(experience.id, { startDate: e.target.value || null })}
                placeholder="Jan 2020"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                End Date
              </label>
              <input
                type="text"
                value={experience.isCurrent ? "" : experience.endDate || ""}
                onChange={(e) => updateWorkExperience(experience.id, { endDate: e.target.value || null })}
                placeholder="Dec 2023"
                disabled={experience.isCurrent}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
            </div>
          </div>

          {/* Current position checkbox */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id={`current-${experience.id}`}
              checked={experience.isCurrent}
              onChange={(e) => updateWorkExperience(experience.id, { isCurrent: e.target.checked })}
              className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <label
              htmlFor={`current-${experience.id}`}
              className="text-sm text-gray-700 dark:text-gray-300"
            >
              I currently work here
            </label>
          </div>

          {/* Achievements / Bullet points */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Key Achievements
              </label>
              <button className="flex items-center gap-1 text-xs text-purple-600 dark:text-purple-400 hover:text-purple-700">
                <Sparkles className="h-3 w-3" />
                AI Enhance
              </button>
            </div>
            
            {/* Existing achievements */}
            <div className="space-y-2 mb-2">
              {experience.achievements.map((ach, achIndex) => (
                <div key={achIndex} className="flex items-start gap-2">
                  <span className="text-gray-400 mt-2">•</span>
                  <div className="flex-1 min-w-0">
                    <Suspense
                      fallback={
                        <div className="h-20 flex items-center justify-center border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-800">
                          <Loader2 className="h-4 w-4 text-gray-400 animate-spin" />
                        </div>
                      }
                    >
                      <RichTextEditor
                        content={ach || ""}
                        onChange={(html) => {
                          const newAchievements = [...experience.achievements];
                          newAchievements[achIndex] = html;
                          updateWorkExperience(experience.id, { achievements: newAchievements });
                        }}
                        placeholder="Enter achievement..."
                        minHeight="80px"
                        className="text-sm"
                      />
                    </Suspense>
                  </div>
                  <button
                    onClick={() => handleRemoveAchievement(achIndex)}
                    className="p-1 text-gray-400 hover:text-red-500 flex-shrink-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Add new achievement */}
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <span className="text-gray-400 mt-2">•</span>
                <div className="flex-1 min-w-0">
                  <Suspense
                    fallback={
                      <div className="h-20 flex items-center justify-center border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-800">
                        <Loader2 className="h-4 w-4 text-gray-400 animate-spin" />
                      </div>
                    }
                  >
                    <RichTextEditor
                      content={newAchievement}
                      onChange={(html) => setNewAchievement(html)}
                      placeholder="Add an achievement (e.g., Increased sales by 20%...)"
                      minHeight="80px"
                      className="text-sm"
                    />
                  </Suspense>
                </div>
                <button
                  onClick={handleAddAchievement}
                  className="p-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 flex-shrink-0"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Tip: Start with action verbs and include numbers when possible
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export function ExperienceSection() {
  const workExperience = useResumeBuilderStore((s) => s.content.workExperience);
  const addWorkExperience = useResumeBuilderStore((s) => s.addWorkExperience);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleAddExperience = () => {
    addWorkExperience({
      company: "",
      title: "",
      startDate: null,
      endDate: null,
      description: null,
      achievements: [],
      location: null,
      isCurrent: false,
    });
    setExpandedIndex(workExperience.length);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Work Experience
        </h3>
        <button
          onClick={handleAddExperience}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Experience
        </button>
      </div>

      {workExperience.length === 0 ? (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
          <Building2 className="h-10 w-10 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            No work experience added yet
          </p>
          <button
            onClick={handleAddExperience}
            className="text-blue-500 hover:text-blue-600 text-sm font-medium"
          >
            Add your first position
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {workExperience.map((exp, index) => (
            <ExperienceCard
              key={exp.id}
              experience={exp}
              index={index}
              isExpanded={expandedIndex === index}
              onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
