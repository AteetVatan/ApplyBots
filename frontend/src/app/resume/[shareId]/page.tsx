/**
 * Public resume view page.
 *
 * Displays a shared resume in read-only view.
 * In production, this would fetch the resume from the backend.
 */

"use client";

import { useState, useMemo, useEffect } from "react";
import { useParams } from "next/navigation";
import { getTemplateComponent, TEMPLATES } from "@/components/resume-builder/templates";
import type { ResumeContent } from "@/stores/resume-builder-store";
import {
  Download,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Loader2,
  AlertCircle,
  FileText,
} from "lucide-react";

// Mock data for demo - in production, fetch from API
const MOCK_RESUME: ResumeContent = {
  fullName: "John Doe",
  email: "john.doe@example.com",
  phone: "+1 (555) 123-4567",
  location: "San Francisco, CA",
  linkedinUrl: "https://linkedin.com/in/johndoe",
  portfolioUrl: "https://johndoe.dev",
  githubUrl: "https://github.com/johndoe",
  profilePictureUrl: null,
  customLinks: [],
  professionalSummary:
    "Experienced software engineer with 5+ years of expertise in building scalable web applications. Passionate about clean code, user experience, and continuous learning. Strong background in full-stack development with a focus on modern JavaScript frameworks.",
  workExperience: [
    {
      id: "1",
      company: "Tech Corp",
      title: "Senior Software Engineer",
      startDate: "2021",
      endDate: null,
      description: null,
      achievements: [
        "Led development of a microservices architecture that improved system scalability by 200%",
        "Mentored 5 junior developers and conducted code reviews",
        "Reduced deployment time by 60% through CI/CD pipeline optimization",
      ],
      location: "San Francisco, CA",
      isCurrent: true,
    },
    {
      id: "2",
      company: "Startup Inc",
      title: "Software Engineer",
      startDate: "2019",
      endDate: "2021",
      description: null,
      achievements: [
        "Built real-time collaboration features serving 10K+ daily users",
        "Implemented OAuth2 authentication reducing security incidents by 80%",
      ],
      location: "Remote",
      isCurrent: false,
    },
  ],
  education: [
    {
      id: "1",
      institution: "University of California, Berkeley",
      degree: "Bachelor of Science",
      fieldOfStudy: "Computer Science",
      graduationDate: "2019",
      gpa: 3.8,
      location: "Berkeley, CA",
      achievements: [],
    },
  ],
  skills: {
    technical: ["TypeScript", "React", "Node.js", "Python", "PostgreSQL"],
    soft: ["Leadership", "Communication", "Problem Solving"],
    tools: ["Git", "Docker", "AWS", "Figma"],
  },
  projects: [
    {
      id: "1",
      name: "OpenSource CLI Tool",
      description: "A command-line tool for automating development workflows with 1000+ GitHub stars",
      url: "https://github.com/johndoe/cli-tool",
      technologies: ["Rust", "CLI", "Automation"],
      startDate: "2022",
      endDate: "2023",
      highlights: [],
    },
  ],
  certifications: [
    {
      id: "1",
      name: "AWS Solutions Architect",
      issuer: "Amazon Web Services",
      date: "2022",
      expiryDate: null,
      credentialId: null,
      url: null,
    },
  ],
  awards: [],
  languages: [
    { id: "1", language: "English", proficiency: "native" },
    { id: "2", language: "Spanish", proficiency: "conversational" },
  ],
  customSections: [],
  templateId: "bronzor",
  sectionOrder: [],
  atsScore: 85,
};

export default function PublicResumePage() {
  const params = useParams();
  const shareId = params.shareId as string;

  const [resume, setResume] = useState<ResumeContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scale, setScale] = useState(0.7);

  // Simulate API fetch
  useEffect(() => {
    const fetchResume = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // In production, fetch from API:
        // const response = await fetch(`/api/v1/resume/public/${shareId}`);
        // if (!response.ok) throw new Error("Resume not found");
        // const data = await response.json();
        // setResume(data.content);

        // For demo, use mock data with random delay
        await new Promise((resolve) => setTimeout(resolve, 500));
        
        // Simulate 404 for certain IDs
        if (shareId === "notfound" || shareId.length < 6) {
          throw new Error("Resume not found");
        }
        
        setResume(MOCK_RESUME);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load resume");
      } finally {
        setIsLoading(false);
      }
    };

    fetchResume();
  }, [shareId]);

  // Get template component
  const TemplateComponent = useMemo(() => {
    if (!resume) return null;
    return getTemplateComponent(resume.templateId);
  }, [resume?.templateId]);

  // Zoom controls
  const handleZoomIn = () => setScale(Math.min(scale + 0.1, 1.2));
  const handleZoomOut = () => setScale(Math.max(scale - 0.1, 0.3));
  const handleFitToWidth = () => setScale(0.7);

  // Export PDF
  const handleExport = () => {
    window.print();
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading resume...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !resume) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center max-w-md mx-4">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-8 w-8 text-red-500" />
          </div>
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Resume Not Found
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            This resume may have been removed or the link is incorrect.
          </p>
          <a
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Go to Homepage
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="flex-shrink-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          {/* Logo/Brand */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500 rounded-lg">
              <FileText className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900 dark:text-white">
                {resume.fullName}&apos;s Resume
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Shared via ApplyBots
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-4">
            {/* Zoom controls */}
            <div className="hidden sm:flex items-center gap-2">
              <button
                onClick={handleZoomOut}
                className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
                title="Zoom out"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[3rem] text-center">
                {Math.round(scale * 100)}%
              </span>
              <button
                onClick={handleZoomIn}
                className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
                title="Zoom in"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                onClick={handleFitToWidth}
                className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
                title="Fit to width"
              >
                <Maximize2 className="h-4 w-4" />
              </button>
            </div>

            {/* Download */}
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span className="hidden sm:inline">Download</span>
            </button>
          </div>
        </div>
      </header>

      {/* Resume view */}
      <main
        className="flex-1 overflow-auto p-6"
        style={{
          backgroundImage: "radial-gradient(circle, #cbd5e1 1px, transparent 1px)",
          backgroundSize: "16px 16px",
        }}
      >
        <div className="flex justify-center items-start" style={{ minHeight: "100%" }}>
          <div
            className="shadow-2xl bg-white print:shadow-none"
            style={{
              width: `${8.5 * 96 * scale}px`,
              minHeight: `${11 * 96 * scale}px`,
            }}
          >
            {TemplateComponent && (
              <TemplateComponent content={resume} scale={scale} />
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="flex-shrink-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Built with{" "}
            <a href="/" className="text-blue-500 hover:underline">
              ApplyBots Resume Builder
            </a>
          </p>
        </div>
      </footer>

      {/* Print styles */}
      <style jsx global>{`
        @media print {
          header,
          footer {
            display: none !important;
          }
          main {
            padding: 0 !important;
            background: white !important;
          }
          body {
            background: white !important;
          }
        }
      `}</style>
    </div>
  );
}
