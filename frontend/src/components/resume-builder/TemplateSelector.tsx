/**
 * Template selector modal/sidebar.
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { TEMPLATES } from "./templates";
import { X, Check, ChevronRight, Layout } from "lucide-react";

interface TemplateSelectorProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TemplateSelector({ isOpen, onClose }: TemplateSelectorProps) {
  const templateId = useResumeBuilderStore((s) => s.templateId);
  const setTemplateId = useResumeBuilderStore((s) => s.setTemplateId);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Layout className="h-5 w-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Choose Template
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Template grid */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {TEMPLATES.map((template) => (
              <button
                key={template.id}
                onClick={() => {
                  setTemplateId(template.id);
                  onClose();
                }}
                className={`relative group text-left p-4 rounded-xl border-2 transition-all ${
                  templateId === template.id
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                    : "border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600"
                }`}
              >
                {/* Selected indicator */}
                {templateId === template.id && (
                  <div className="absolute top-2 right-2 p-1 bg-blue-500 rounded-full">
                    <Check className="h-3 w-3 text-white" />
                  </div>
                )}

                {/* Template preview placeholder */}
                <div className="aspect-[8.5/11] bg-gray-100 dark:bg-gray-800 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
                  <div className="w-full h-full p-2">
                    {/* Mini preview */}
                    <div className="w-full h-full bg-white dark:bg-gray-900 rounded shadow-sm p-1">
                      <div
                        className={`h-2 w-1/2 mb-1 rounded ${
                          template.id.includes("modern")
                            ? "bg-blue-500"
                            : template.id.includes("tech")
                            ? "bg-cyan-500"
                            : template.id.includes("two")
                            ? "bg-emerald-500"
                            : "bg-gray-700"
                        }`}
                      />
                      <div className="space-y-0.5">
                        {[...Array(6)].map((_, i) => (
                          <div
                            key={i}
                            className="h-0.5 bg-gray-200 dark:bg-gray-700 rounded"
                            style={{ width: `${70 + Math.random() * 30}%` }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Template info */}
                <h3 className="font-medium text-gray-900 dark:text-white mb-1">
                  {template.name}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 line-clamp-2">
                  {template.description}
                </p>

                {/* ATS score badge */}
                <div className="flex items-center gap-1">
                  <span
                    className={`text-xs font-medium ${
                      template.atsScore >= 95
                        ? "text-green-600 dark:text-green-400"
                        : template.atsScore >= 90
                        ? "text-blue-600 dark:text-blue-400"
                        : "text-amber-600 dark:text-amber-400"
                    }`}
                  >
                    ATS: {template.atsScore}%
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function TemplateButton() {
  const [isOpen, setIsOpen] = useState(false);
  const templateId = useResumeBuilderStore((s) => s.templateId);
  const currentTemplate = TEMPLATES.find((t) => t.id === templateId);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        <Layout className="h-4 w-4 text-gray-500" />
        <span className="text-gray-700 dark:text-gray-300">
          {currentTemplate?.name || "Template"}
        </span>
        <ChevronRight className="h-4 w-4 text-gray-400" />
      </button>
      <TemplateSelector isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
