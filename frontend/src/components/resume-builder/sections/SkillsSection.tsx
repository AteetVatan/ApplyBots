/**
 * Skills section editor with AI suggestions.
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { Plus, X, Sparkles, Code, Trash2 } from "lucide-react";
import type { TechnicalSkillGroup } from "@/stores/resume-builder-store";

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
            className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm rounded"
          >
            {skill}
            <button
              onClick={() => handleRemoveSkill(skill)}
              className="hover:bg-blue-200 dark:hover:bg-blue-800 rounded"
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
          className="p-1 text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

interface TechnicalSkillGroupEditorProps {
  group: TechnicalSkillGroup;
  onChange: (group: TechnicalSkillGroup) => void;
  onRemove: () => void;
}

function TechnicalSkillGroupEditor({ group, onChange, onRemove }: TechnicalSkillGroupEditorProps) {
  const handleHeaderChange = (header: string) => {
    onChange({ ...group, header });
  };

  const handleItemsChange = (items: string[]) => {
    onChange({ ...group, items });
  };

  return (
    <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-gray-50 dark:bg-gray-800/50">
      <div className="flex items-center justify-between mb-2">
        <input
          type="text"
          value={group.header}
          onChange={(e) => handleHeaderChange(e.target.value)}
          placeholder="Category name (e.g., Programming Languages, Frameworks...)"
          className="flex-1 font-semibold text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 focus:outline-none focus:border-blue-500 text-sm"
        />
        <button
          onClick={onRemove}
          className="ml-2 p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
          title="Remove category"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
      <SkillTagInput
        skills={group.items}
        onChange={handleItemsChange}
        placeholder="Add skill to this category..."
      />
    </div>
  );
}

export function SkillsSection() {
  const skills = useResumeBuilderStore((s) => s.content.skills);
  const updateSkills = useResumeBuilderStore((s) => s.updateSkills);
  const setAIDrawerOpen = useResumeBuilderStore((s) => s.setAIDrawerOpen);

  const handleAddTechnicalGroup = () => {
    const newGroup: TechnicalSkillGroup = {
      id: crypto.randomUUID(),
      header: "New Category",
      items: [],
    };
    updateSkills({ ...skills, technical: [...skills.technical, newGroup] });
  };

  const handleUpdateTechnicalGroup = (id: string, updatedGroup: TechnicalSkillGroup) => {
    updateSkills({
      ...skills,
      technical: skills.technical.map((g) => (g.id === id ? updatedGroup : g)),
    });
  };

  const handleRemoveTechnicalGroup = (id: string) => {
    updateSkills({
      ...skills,
      technical: skills.technical.filter((g) => g.id !== id),
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Technical Skills
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
        <div className="flex items-center justify-between mb-2">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            <Code className="h-4 w-4 text-blue-500" />
            Categories
          </label>
          <button
            onClick={handleAddTechnicalGroup}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            <Plus className="h-3 w-3" />
            Add Category
          </button>
        </div>
        <div className="space-y-3">
          {skills.technical.length === 0 && (
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
              No technical skill categories yet. Click "Add Category" to get started.
            </div>
          )}
          {skills.technical.map((group) => (
            <TechnicalSkillGroupEditor
              key={group.id}
              group={group}
              onChange={(updated) => handleUpdateTechnicalGroup(group.id, updated)}
              onRemove={() => handleRemoveTechnicalGroup(group.id)}
            />
          ))}
          {skills.technical.length > 0 && (
            <button
              onClick={handleAddTechnicalGroup}
              className="w-full flex items-center justify-center gap-1 px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors border border-dashed border-blue-300 dark:border-blue-700"
            >
              <Plus className="h-4 w-4" />
              Add Category
            </button>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg">
        <h4 className="text-sm font-medium text-amber-800 dark:text-amber-300 mb-2">
          Pro Tips
        </h4>
        <ul className="text-xs text-amber-700 dark:text-amber-400 space-y-1">
          <li>• Match skills to keywords in the job description</li>
          <li>• List your most relevant skills first</li>
          <li>• Use industry-standard terminology</li>
          <li>• Group technical skills by category (e.g., Languages, Frameworks, Databases)</li>
        </ul>
      </div>
    </div>
  );
}
