/**
 * Soft Skills section editor.
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { Plus, X, Sparkles, Users } from "lucide-react";

interface SkillTagInputProps {
  skills: string[];
  onChange: (skills: string[]) => void;
  placeholder: string;
}

function SkillTagInput({ skills, onChange, placeholder }: SkillTagInputProps) {
  const [input, setInput] = useState("");

  const handleAddSkill = () => {
    if (input.trim() && !skills.includes(input.trim())) {
      onChange([...skills, input.trim()]);
      setInput("");
    }
  };

  const handleRemoveSkill = (skill: string) => {
    onChange(skills.filter((s) => s !== skill));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddSkill();
    } else if (e.key === "Backspace" && !input && skills.length > 0) {
      onChange(skills.slice(0, -1));
    }
  };

  return (
    <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-2 bg-white dark:bg-gray-800 focus-within:ring-2 focus-within:ring-blue-500">
      <div className="flex flex-wrap gap-1.5 mb-2">
        {skills.map((skill) => (
          <span
            key={skill}
            className="inline-flex items-center gap-1 px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-sm rounded"
          >
            {skill}
            <button
              onClick={() => handleRemoveSkill(skill)}
              className="hover:bg-purple-200 dark:hover:bg-purple-800 rounded"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-gray-900 dark:text-white text-sm focus:outline-none"
        />
        <button
          onClick={handleAddSkill}
          disabled={!input.trim()}
          className="p-1 text-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

export function SoftSkillsSection() {
  const skills = useResumeBuilderStore((s) => s.content.skills);
  const updateSkills = useResumeBuilderStore((s) => s.updateSkills);
  const setAIDrawerOpen = useResumeBuilderStore((s) => s.setAIDrawerOpen);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Soft Skills
        </h3>
        <button
          onClick={() => setAIDrawerOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all"
        >
          <Sparkles className="h-4 w-4" />
          AI Suggest
        </button>
      </div>

      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          <Users className="h-4 w-4 text-purple-500" />
          Soft Skills
        </label>
        <SkillTagInput
          skills={skills.soft || []}
          onChange={(soft) => updateSkills({ ...skills, soft })}
          placeholder="Add soft skill (e.g., Leadership, Communication, Teamwork...)"
        />
      </div>

      {/* Tips */}
      <div className="bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg">
        <h4 className="text-sm font-medium text-amber-800 dark:text-amber-300 mb-2">
          Pro Tips
        </h4>
        <ul className="text-xs text-amber-700 dark:text-amber-400 space-y-1">
          <li>• Highlight skills that demonstrate your ability to work with others</li>
          <li>• Include skills mentioned in the job description</li>
          <li>• Be specific (e.g., "Conflict Resolution" instead of just "Communication")</li>
          <li>• Focus on skills relevant to the role you're applying for</li>
        </ul>
      </div>
    </div>
  );
}
