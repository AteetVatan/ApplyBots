/**
 * Education section editor.
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore, type Education } from "@/stores/resume-builder-store";
import { Plus, Trash2, ChevronDown, ChevronUp, GraduationCap } from "lucide-react";

interface EducationCardProps {
  education: Education;
  isExpanded: boolean;
  onToggle: () => void;
}

function EducationCard({ education, isExpanded, onToggle }: EducationCardProps) {
  const updateEducation = useResumeBuilderStore((s) => s.updateEducation);
  const removeEducation = useResumeBuilderStore((s) => s.removeEducation);

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750"
        onClick={onToggle}
      >
        <GraduationCap className="h-5 w-5 text-gray-400" />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-900 dark:text-white truncate">
            {education.degree || "Degree"}
            {education.fieldOfStudy && ` in ${education.fieldOfStudy}`}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
            {education.institution || "Institution"} • {education.graduationDate || "Year"}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            removeEducation(education.id);
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
          {/* Degree */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Degree *
            </label>
            <input
              type="text"
              value={education.degree}
              onChange={(e) => updateEducation(education.id, { degree: e.target.value })}
              placeholder="Bachelor of Science"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Field of Study */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Field of Study
            </label>
            <input
              type="text"
              value={education.fieldOfStudy || ""}
              onChange={(e) => updateEducation(education.id, { fieldOfStudy: e.target.value || null })}
              placeholder="Computer Science"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Institution */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Institution *
            </label>
            <input
              type="text"
              value={education.institution}
              onChange={(e) => updateEducation(education.id, { institution: e.target.value })}
              placeholder="Stanford University"
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
              value={education.location || ""}
              onChange={(e) => updateEducation(education.id, { location: e.target.value || null })}
              placeholder="Stanford, CA"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Graduation Date and GPA */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Graduation Date
              </label>
              <input
                type="text"
                value={education.graduationDate || ""}
                onChange={(e) => updateEducation(education.id, { graduationDate: e.target.value || null })}
                placeholder="May 2020"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                GPA (optional)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="4"
                value={education.gpa || ""}
                onChange={(e) => updateEducation(education.id, { gpa: e.target.value ? parseFloat(e.target.value) : null })}
                placeholder="3.8"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function EducationSection() {
  const education = useResumeBuilderStore((s) => s.content.education);
  const addEducation = useResumeBuilderStore((s) => s.addEducation);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleAddEducation = () => {
    addEducation({
      institution: "",
      degree: "",
      fieldOfStudy: null,
      graduationDate: null,
      gpa: null,
      location: null,
      achievements: [],
    });
    setExpandedIndex(education.length);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Education
        </h3>
        <button
          onClick={handleAddEducation}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Education
        </button>
      </div>

      {education.length === 0 ? (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
          <GraduationCap className="h-10 w-10 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            No education added yet
          </p>
          <button
            onClick={handleAddEducation}
            className="text-blue-500 hover:text-blue-600 text-sm font-medium"
          >
            Add your education
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {education.map((edu, index) => (
            <EducationCard
              key={edu.id}
              education={edu}
              isExpanded={expandedIndex === index}
              onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
