/**
 * Template selector modal/sidebar.
 */

"use client";

import { useState, useMemo } from "react";
import { useResumeBuilderStore, type ResumeContent } from "@/stores/resume-builder-store";
import { TEMPLATES, getTemplateComponent } from "./templates";
import { X, Check, ChevronRight, Layout } from "lucide-react";

interface TemplateSelectorProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Generate sample resume content for template previews.
 */
function getSampleContent(): ResumeContent {
  return {
    fullName: "John Doe",
    email: "john.doe@example.com",
    phone: "+1 (555) 123-4567",
    location: "San Francisco, CA",
    linkedinUrl: "https://linkedin.com/in/johndoe",
    portfolioUrl: "https://johndoe.dev",
    githubUrl: "https://github.com/johndoe",
    profilePictureUrl: null,
    customLinks: [],
    professionalSummary: "Experienced software engineer with a passion for building scalable web applications and leading cross-functional teams.",
    workExperience: [
      {
        id: "sample-1",
        company: "Tech Corp",
        title: "Senior Software Engineer",
        startDate: "2020-01",
        endDate: null,
        description: null,
        achievements: [
          "Led development of microservices architecture",
          "Improved system performance by 40%",
          "Mentored junior developers",
        ],
        location: "San Francisco, CA",
        isCurrent: true,
      },
      {
        id: "sample-2",
        company: "Startup Inc",
        title: "Full Stack Developer",
        startDate: "2018-06",
        endDate: "2019-12",
        description: null,
        achievements: [
          "Built RESTful APIs using Node.js",
          "Developed responsive frontend with React",
        ],
        location: "Remote",
        isCurrent: false,
      },
    ],
    education: [
      {
        id: "sample-edu-1",
        institution: "University of Technology",
        degree: "Bachelor of Science",
        fieldOfStudy: "Computer Science",
        graduationDate: "2018-05",
        gpa: 3.8,
        location: "Boston, MA",
        achievements: [],
      },
    ],
    skills: {
      technical: ["JavaScript", "TypeScript", "React", "Node.js", "Python"],
      soft: ["Leadership", "Communication", "Problem Solving"],
      tools: ["Git", "Docker", "AWS", "PostgreSQL"],
    },
    projects: [
      {
        id: "sample-proj-1",
        name: "E-Commerce Platform",
        description: "Built a full-stack e-commerce platform with payment integration",
        url: "https://example.com/project",
        technologies: ["React", "Node.js", "MongoDB"],
        startDate: "2021-01",
        endDate: "2021-06",
        highlights: [],
      },
    ],
    certifications: [
      {
        id: "sample-cert-1",
        name: "AWS Certified Solutions Architect",
        issuer: "Amazon Web Services",
        date: "2022-03",
        expiryDate: null,
        credentialId: "AWS-12345",
        url: null,
      },
    ],
    awards: [],
    languages: [
      {
        id: "sample-lang-1",
        language: "English",
        proficiency: "native",
      },
      {
        id: "sample-lang-2",
        language: "Spanish",
        proficiency: "fluent",
      },
    ],
    customSections: [],
    templateId: "bronzor",
    sectionOrder: ["contact", "summary", "experience", "education", "skills", "projects"],
    atsScore: null,
  };
}

export function TemplateSelector({ isOpen, onClose }: TemplateSelectorProps) {
  const templateId = useResumeBuilderStore((s) => s.templateId);
  const setTemplateId = useResumeBuilderStore((s) => s.setTemplateId);
  const themeSettings = useResumeBuilderStore((s) => s.themeSettings);
  
  // Memoize sample content to avoid recreating on every render
  const sampleContent = useMemo(() => getSampleContent(), []);

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

                {/* Template preview */}
                <div className="aspect-[8.5/11] bg-gray-100 dark:bg-gray-800 rounded-lg mb-3 flex items-center justify-center overflow-hidden relative">
                  <div className="w-full h-full p-1 pointer-events-none flex items-center justify-center">
                    <div 
                      className="relative"
                      style={{ 
                        transform: "scale(0.22)",
                        transformOrigin: "center center",
                        width: "8.5in",
                        minHeight: "11in",
                      }}
                    >
                      {(() => {
                        const TemplateComponent = getTemplateComponent(template.id);
                        return (
                          <TemplateComponent
                            content={sampleContent}
                            scale={1}
                            highlightSection={undefined}
                            themeSettings={themeSettings}
                          />
                        );
                      })()}
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
        className="flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex-shrink-0 max-w-[180px]"
      >
        <Layout className="h-4 w-4 text-gray-500 flex-shrink-0" />
        <span className="text-gray-700 dark:text-gray-300 truncate">
          {currentTemplate?.name || "Template"}
        </span>
        <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
      </button>
      <TemplateSelector isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
