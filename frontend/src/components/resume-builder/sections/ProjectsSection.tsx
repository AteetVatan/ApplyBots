/**
 * Projects section editor.
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore, type Project } from "@/stores/resume-builder-store";
import { Plus, Trash2, ChevronDown, ChevronUp, FolderGit2, X, Link } from "lucide-react";

interface ProjectCardProps {
  project: Project;
  isExpanded: boolean;
  onToggle: () => void;
}

function ProjectCard({ project, isExpanded, onToggle }: ProjectCardProps) {
  const updateProject = useResumeBuilderStore((s) => s.updateProject);
  const removeProject = useResumeBuilderStore((s) => s.removeProject);
  const [techInput, setTechInput] = useState("");

  const handleAddTechnology = () => {
    if (techInput.trim() && !project.technologies.includes(techInput.trim())) {
      updateProject(project.id, {
        technologies: [...project.technologies, techInput.trim()],
      });
      setTechInput("");
    }
  };

  const handleRemoveTechnology = (tech: string) => {
    updateProject(project.id, {
      technologies: project.technologies.filter((t) => t !== tech),
    });
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750"
        onClick={onToggle}
      >
        <FolderGit2 className="h-5 w-5 text-gray-400" />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-900 dark:text-white truncate">
            {project.name || "New Project"}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
            {project.technologies.slice(0, 3).join(", ") || "No technologies added"}
            {project.technologies.length > 3 && ` +${project.technologies.length - 3} more`}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            removeProject(project.id);
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
          {/* Project Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Project Name *
            </label>
            <input
              type="text"
              value={project.name}
              onChange={(e) => updateProject(project.id, { name: e.target.value })}
              placeholder="E-commerce Platform"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description *
            </label>
            <textarea
              value={project.description}
              onChange={(e) => updateProject(project.id, { description: e.target.value })}
              placeholder="Built a full-stack e-commerce platform with shopping cart, payment integration, and admin dashboard..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Project URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Project URL
            </label>
            <div className="relative">
              <Link className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="url"
                value={project.url || ""}
                onChange={(e) => updateProject(project.id, { url: e.target.value || null })}
                placeholder="https://github.com/username/project"
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Technologies */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Technologies Used
            </label>
            <div className="flex flex-wrap gap-1.5 mb-2">
              {project.technologies.map((tech) => (
                <span
                  key={tech}
                  className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 text-sm rounded"
                >
                  {tech}
                  <button
                    onClick={() => handleRemoveTechnology(tech)}
                    className="hover:bg-emerald-200 dark:hover:bg-emerald-800 rounded"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={techInput}
                onChange={(e) => setTechInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTechnology())}
                placeholder="Add technology (e.g., React, Node.js...)"
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleAddTechnology}
                disabled={!techInput.trim()}
                className="p-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function ProjectsSection() {
  const projects = useResumeBuilderStore((s) => s.content.projects);
  const addProject = useResumeBuilderStore((s) => s.addProject);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleAddProject = () => {
    addProject({
      name: "",
      description: "",
      url: null,
      technologies: [],
      startDate: null,
      endDate: null,
      highlights: [],
    });
    setExpandedIndex(projects.length);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Projects
        </h3>
        <button
          onClick={handleAddProject}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Project
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
          <FolderGit2 className="h-10 w-10 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            No projects added yet
          </p>
          <button
            onClick={handleAddProject}
            className="text-blue-500 hover:text-blue-600 text-sm font-medium"
          >
            Add your first project
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((proj, index) => (
            <ProjectCard
              key={proj.id}
              project={proj}
              isExpanded={expandedIndex === index}
              onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
