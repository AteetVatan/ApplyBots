/**
 * JSON Export/Import functionality for resume data.
 *
 * Features:
 * - Export resume as JSON file
 * - Import resume from JSON file
 * - Validates JSON structure on import
 * - Supports JSON Resume standard format
 */

"use client";

import { useRef, useState } from "react";
import { useResumeBuilderStore, type ResumeContent } from "@/stores/resume-builder-store";
import {
  Download,
  Upload,
  X,
  FileJson,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from "lucide-react";

interface ExportImportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Convert our format to JSON Resume standard
function toJsonResumeFormat(content: ResumeContent, draftName: string): object {
  const [firstName, ...lastNameParts] = (content.fullName || "").split(" ");
  const lastName = lastNameParts.join(" ");

  return {
    $schema: "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
    basics: {
      name: content.fullName,
      label: content.workExperience[0]?.title || "",
      email: content.email,
      phone: content.phone,
      url: content.portfolioUrl,
      summary: content.professionalSummary,
      location: {
        address: content.location || "",
      },
      profiles: [
        content.linkedinUrl && {
          network: "LinkedIn",
          url: content.linkedinUrl,
        },
        content.githubUrl && {
          network: "GitHub",
          url: content.githubUrl,
        },
        ...(content.customLinks || []).map((link) => ({
          network: link.label,
          url: link.url,
        })),
      ].filter(Boolean),
    },
    work: content.workExperience.map((exp) => ({
      name: exp.company,
      position: exp.title,
      startDate: exp.startDate,
      endDate: exp.isCurrent ? "" : exp.endDate,
      summary: exp.description,
      highlights: exp.achievements,
      location: exp.location,
    })),
    education: content.education.map((edu) => ({
      institution: edu.institution,
      area: edu.fieldOfStudy,
      studyType: edu.degree,
      endDate: edu.graduationDate,
      score: edu.gpa?.toString(),
    })),
    skills: [
      ...content.skills.technical.flatMap((g) => g.items.map((s) => ({ name: s, level: "Expert", keywords: [] }))),
      ...content.skills.soft.map((s) => ({ name: s, level: "Expert", keywords: [] })),
      ...content.skills.custom.flatMap((g) => g.items.map((s) => ({ name: s, level: "Expert", keywords: [] }))),
      ...content.skills.tools.map((s) => ({ name: s, level: "Intermediate", keywords: [] })),
    ],
    projects: content.projects.map((proj) => ({
      name: proj.name,
      description: proj.description,
      url: proj.url,
      keywords: proj.technologies,
      startDate: proj.startDate,
      endDate: proj.endDate,
    })),
    certificates: content.certifications.map((cert) => ({
      name: cert.name,
      issuer: cert.issuer,
      date: cert.date,
      url: cert.url,
    })),
    awards: content.awards.map((award) => ({
      title: award.title,
      awarder: award.issuer,
      date: award.date,
      summary: award.description,
    })),
    languages: content.languages.map((lang) => ({
      language: lang.language,
      fluency: lang.proficiency,
    })),
    meta: {
      canonical: "https://applybots.com/resume",
      version: "v1.0.0",
      lastModified: new Date().toISOString(),
      templateId: content.templateId,
      draftName,
    },
  };
}

// Convert our format to custom ApplyBots format (includes all fields)
function toApplyBotsFormat(content: ResumeContent, draftName: string): object {
  return {
    version: "1.0.0",
    exportDate: new Date().toISOString(),
    draftName,
    content: {
      ...content,
      customLinks: content.customLinks || [],
    },
  };
}

// Validate and import JSON Resume format
function fromJsonResumeFormat(data: Record<string, unknown>): Partial<ResumeContent> | null {
  try {
    const basics = data.basics as Record<string, unknown> || {};
    const work = (data.work || []) as Array<Record<string, unknown>>;
    const education = (data.education || []) as Array<Record<string, unknown>>;
    const skills = (data.skills || []) as Array<Record<string, unknown>>;
    const projects = (data.projects || []) as Array<Record<string, unknown>>;
    const certificates = (data.certificates || []) as Array<Record<string, unknown>>;
    const awards = (data.awards || []) as Array<Record<string, unknown>>;
    const languages = (data.languages || []) as Array<Record<string, unknown>>;

    return {
      fullName: (basics.name as string) || "",
      email: (basics.email as string) || "",
      phone: (basics.phone as string) || null,
      location: ((basics.location as Record<string, unknown>)?.address as string) || null,
      linkedinUrl: ((basics.profiles as Array<Record<string, unknown>>) || []).find(
        (p) => p.network === "LinkedIn"
      )?.url as string || null,
      githubUrl: ((basics.profiles as Array<Record<string, unknown>>) || []).find(
        (p) => p.network === "GitHub"
      )?.url as string || null,
      portfolioUrl: (basics.url as string) || null,
      professionalSummary: (basics.summary as string) || null,
      workExperience: work.map((w) => ({
        id: crypto.randomUUID(),
        company: (w.name as string) || "",
        title: (w.position as string) || "",
        startDate: (w.startDate as string) || null,
        endDate: (w.endDate as string) || null,
        description: (w.summary as string) || null,
        achievements: ((w.highlights as string[]) || []),
        location: (w.location as string) || null,
        isCurrent: !w.endDate,
      })),
      education: education.map((e) => ({
        id: crypto.randomUUID(),
        institution: (e.institution as string) || "",
        degree: (e.studyType as string) || "",
        fieldOfStudy: (e.area as string) || null,
        graduationDate: (e.endDate as string) || null,
        gpa: e.score ? parseFloat(e.score as string) : null,
        location: null,
        achievements: [],
      })),
      skills: {
        technical: skills.filter((s) => s.level === "Expert").map((s) => s.name as string),
        soft: [],
        tools: skills.filter((s) => s.level !== "Expert").map((s) => s.name as string),
      },
      projects: projects.map((p) => ({
        id: crypto.randomUUID(),
        name: (p.name as string) || "",
        description: (p.description as string) || "",
        url: (p.url as string) || null,
        technologies: ((p.keywords as string[]) || []),
        startDate: (p.startDate as string) || null,
        endDate: (p.endDate as string) || null,
        highlights: [],
      })),
      certifications: certificates.map((c) => ({
        id: crypto.randomUUID(),
        name: (c.name as string) || "",
        issuer: (c.issuer as string) || "",
        date: (c.date as string) || null,
        expiryDate: null,
        credentialId: null,
        url: (c.url as string) || null,
      })),
      awards: awards.map((a) => ({
        id: crypto.randomUUID(),
        title: (a.title as string) || "",
        issuer: (a.awarder as string) || "",
        date: (a.date as string) || null,
        description: (a.summary as string) || null,
      })),
      languages: languages.map((l) => ({
        id: crypto.randomUUID(),
        language: (l.language as string) || "",
        proficiency: ((l.fluency as string) || "conversational") as "native" | "fluent" | "conversational" | "basic",
      })),
    };
  } catch {
    return null;
  }
}

// Import ApplyBots format
function fromApplyBotsFormat(data: Record<string, unknown>): { content: ResumeContent; draftName: string } | null {
  try {
    if (!data.content || typeof data.content !== "object") {
      return null;
    }
    
    const content = data.content as ResumeContent;
    const draftName = (data.draftName as string) || "Imported Resume";
    
    // Ensure IDs exist
    return {
      content: {
        ...content,
        workExperience: content.workExperience.map((w) => ({ ...w, id: w.id || crypto.randomUUID() })),
        education: content.education.map((e) => ({ ...e, id: e.id || crypto.randomUUID() })),
        projects: content.projects.map((p) => ({ ...p, id: p.id || crypto.randomUUID() })),
        certifications: content.certifications.map((c) => ({ ...c, id: c.id || crypto.randomUUID() })),
        awards: content.awards.map((a) => ({ ...a, id: a.id || crypto.randomUUID() })),
        languages: content.languages.map((l) => ({ ...l, id: l.id || crypto.randomUUID() })),
        customSections: content.customSections?.map((s) => ({ ...s, id: s.id || crypto.randomUUID() })) || [],
        customLinks: content.customLinks?.map((l) => ({ ...l, id: l.id || crypto.randomUUID() })) || [],
      },
      draftName,
    };
  } catch {
    return null;
  }
}

export function ExportImportModal({ isOpen, onClose }: ExportImportModalProps) {
  const content = useResumeBuilderStore((s) => s.content);
  const draftName = useResumeBuilderStore((s) => s.draftName);
  const setContent = useResumeBuilderStore((s) => s.setContent);
  const setDraftName = useResumeBuilderStore((s) => s.setDraftName);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState(false);

  if (!isOpen) return null;

  const handleExportApplyBots = () => {
    const data = toApplyBotsFormat(content, draftName);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${draftName.replace(/\s+/g, "_")}.applybots.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportJsonResume = () => {
    const data = toJsonResumeFormat(content, draftName);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${draftName.replace(/\s+/g, "_")}.jsonresume.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setImportError(null);
    setImportSuccess(false);

    try {
      const text = await file.text();
      const data = JSON.parse(text) as Record<string, unknown>;

      // Try ApplyBots format first
      if (data.version && data.content) {
        const result = fromApplyBotsFormat(data);
        if (result) {
          setContent(result.content);
          setDraftName(result.draftName);
          setImportSuccess(true);
          setTimeout(() => {
            onClose();
          }, 1500);
          return;
        }
      }

      // Try JSON Resume format
      if (data.basics || data.$schema) {
        const imported = fromJsonResumeFormat(data);
        if (imported) {
          const meta = data.meta as Record<string, unknown> | undefined;
          setContent({
            ...content,
            ...imported,
            templateId: (meta?.templateId as string) || content.templateId,
          });
          setDraftName((meta?.draftName as string) || "Imported Resume");
          setImportSuccess(true);
          setTimeout(() => {
            onClose();
          }, 1500);
          return;
        }
      }

      setImportError("Unrecognized file format. Please use ApplyBots or JSON Resume format.");
    } catch {
      setImportError("Failed to parse JSON file. Please check the file format.");
    } finally {
      setIsImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <FileJson className="h-5 w-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Export / Import
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-6">
          {/* Export Section */}
          <section>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Export Resume
            </h3>
            <div className="space-y-2">
              <button
                onClick={handleExportApplyBots}
                className="w-full flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
              >
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Download className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    ApplyBots Format
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Complete backup with all settings
                  </div>
                </div>
              </button>
              <button
                onClick={handleExportJsonResume}
                className="w-full flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
              >
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <Download className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    JSON Resume Format
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Standard format for other tools
                  </div>
                </div>
              </button>
            </div>
          </section>

          {/* Import Section */}
          <section>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Import Resume
            </h3>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isImporting}
              className="w-full flex items-center gap-3 p-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors text-left disabled:opacity-50"
            >
              <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                {isImporting ? (
                  <Loader2 className="h-5 w-5 text-gray-600 dark:text-gray-400 animate-spin" />
                ) : (
                  <Upload className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                )}
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">
                  {isImporting ? "Importing..." : "Import from JSON"}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Supports ApplyBots and JSON Resume formats
                </div>
              </div>
            </button>

            {/* Error/Success messages */}
            {importError && (
              <div className="mt-2 flex items-center gap-2 p-2 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {importError}
              </div>
            )}
            {importSuccess && (
              <div className="mt-2 flex items-center gap-2 p-2 bg-green-50 dark:bg-green-900/20 rounded-lg text-sm text-green-600 dark:text-green-400">
                <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
                Resume imported successfully!
              </div>
            )}
          </section>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Your data is processed locally and not uploaded anywhere.
          </p>
        </div>
      </div>
    </div>
  );
}

// Button to open the modal
export function ExportImportButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        <FileJson className="h-4 w-4 text-gray-500" />
        <span className="text-gray-700 dark:text-gray-300">JSON</span>
      </button>
      <ExportImportModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
